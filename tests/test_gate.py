import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hygiene_check import check as hygiene_check
from local_check import child_environment, command_inventory, invoke, source_identity
import local_check
import run_tests


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make_git(self):
        def git(*args):
            return subprocess.run(
                ["git", "-C", str(self.root), *args], check=True,
                capture_output=True,
            )
        git("init", "-b", "main")
        (self.root / "source.py").write_text("value = 1\n")
        (self.root / ".gitignore").write_text("artifacts/\n")
        git("add", ".")
        git("-c", "user.name=Test Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-m", "fixture")
        return git

    def test_clean_identity_has_commit_and_digest(self):
        self.make_git()
        commit, dirty, tree = source_identity(self.root)
        self.assertEqual(len(commit), 40)
        self.assertFalse(dirty)
        self.assertEqual(len(tree), 64)

    def test_dirty_modification_changes_tree(self):
        self.make_git()
        before = source_identity(self.root)
        (self.root / "source.py").write_text("value = 2\n")
        after = source_identity(self.root)
        self.assertTrue(after[1])
        self.assertNotEqual(before[2], after[2])

    def test_untracked_input_is_included(self):
        self.make_git()
        before = source_identity(self.root)
        (self.root / "new-input.txt").write_text("new")
        after = source_identity(self.root)
        self.assertTrue(after[1])
        self.assertNotEqual(before[2], after[2])

    def test_ignored_gate_artifacts_do_not_change_identity(self):
        self.make_git()
        before = source_identity(self.root)
        folder = self.root / "artifacts"
        folder.mkdir()
        (folder / "log").write_text("ignored")
        self.assertEqual(before, source_identity(self.root))

    def test_rename_changes_identity(self):
        self.make_git()
        (self.root / "untracked-old").write_text("same")
        before = source_identity(self.root)
        (self.root / "untracked-old").rename(self.root / "untracked-new")
        self.assertNotEqual(before[2], source_identity(self.root)[2])

    def test_filename_with_newline_is_unambiguous(self):
        self.make_git()
        (self.root / "with\nnewline.txt").write_text("data")
        self.assertEqual(len(source_identity(self.root)[2]), 64)

    def test_source_symlink_fails(self):
        self.make_git()
        (self.root / "link").symlink_to(self.root / "source.py")
        with self.assertRaises(ValueError):
            source_identity(self.root)

    def test_deleted_tracked_source_fails(self):
        self.make_git()
        (self.root / "source.py").unlink()
        with self.assertRaises(ValueError):
            source_identity(self.root)

    def test_non_git_directory_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            source_identity(self.root)

    def test_nested_directory_cannot_inherit_parent_git_identity(self):
        self.make_git()
        nested = self.root / "nested"
        nested.mkdir()
        with self.assertRaises(ValueError):
            source_identity(nested)

    def test_child_environment_excludes_credentials_home_and_proxy(self):
        with patch.dict(os.environ, {
            "AXIOMLINT_TEST_SECRET": "not-to-copy", "HOME": "/private",
            "HTTPS_PROXY": "https://private.invalid", "OPENAI_API_KEY": "not-a-real-key",
        }):
            env = child_environment(self.root)
        self.assertNotIn("AXIOMLINT_TEST_SECRET", env)
        self.assertNotIn("HOME", env)
        self.assertNotIn("HTTPS_PROXY", env)
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertEqual(env["PYTHONHASHSEED"], "0")

    def test_command_inventory_mandatory_and_local(self):
        commands = command_inventory(sys.executable)
        self.assertEqual([x[0] for x in commands], ["governance", "hygiene", "syntax", "tests"])
        self.assertTrue(all(x[1][0] == sys.executable for x in commands))

    def test_failed_command_is_preserved_and_not_clean(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            report = invoke("failure", [sys.executable, "-c",
                            "import sys; print('negative outcome'); sys.exit(7)"],
                            self.root, self.root)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["exit_code"], 7)
        self.assertIn(b"negative outcome", (self.root / "failure.stdout.log").read_bytes())

    def test_timeout_is_preserved(self):
        with contextlib.redirect_stdout(io.StringIO()):
            report = invoke("timeout", [sys.executable, "-c", "import time; time.sleep(1)"],
                            self.root, self.root, timeout=0.02)
        self.assertEqual(report["status"], "TIMEOUT")
        self.assertEqual(report["exit_code"], 124)

    def test_missing_executable_is_error(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            report = invoke("missing", ["/this/executable/does/not/exist"], self.root, self.root)
        self.assertEqual(report["status"], "ERROR")
        self.assertEqual(report["exit_code"], 127)

    def test_current_hygiene_passes(self):
        self.assertEqual(hygiene_check(ROOT), [])

    def test_hosted_workflow_rejected(self):
        folder = self.root / ".github/workflows"
        folder.mkdir(parents=True)
        (folder / "ci.yml").write_text("name: forbidden")
        self.assertTrue(any("prohibited" in x for x in hygiene_check(self.root)))

    def test_broken_document_link_rejected(self):
        (self.root / "README.md").write_text("[Missing](missing.md)")
        self.assertTrue(any("broken link" in x for x in hygiene_check(self.root)))

    def test_acceptance_refuses_dirty_tree_before_commands(self):
        self.make_git()
        (self.root / "untracked").write_text("dirty")
        with patch.object(local_check, "ROOT", self.root), patch.object(
            local_check, "invoke"
        ) as invoked, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(local_check.main(["--require-clean"]), 1)
            invoked.assert_not_called()

    def test_acceptance_cannot_disable_record_capture(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            local_check.main(["--require-clean", "--no-record"])
        self.assertEqual(error.exception.code, 2)

    def test_empty_test_selection_fails(self):
        empty = unittest.TestSuite()
        with patch.object(unittest.defaultTestLoader, "discover", return_value=empty):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(run_tests.run(), 1)
