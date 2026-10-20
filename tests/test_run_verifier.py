import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from axiomlint.evidence.store import canonical_json, sha256
from local_check import command_inventory
from verify_local_run import verify


class RunVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        commands = []
        for name, argv in command_inventory(sys.executable):
            stdout = b"COUNTS discovered=1 executed=1 skipped=0\n" if name == "tests" else b"OK\n"
            (self.directory / f"{name}.stdout.log").write_bytes(stdout)
            (self.directory / f"{name}.stderr.log").write_bytes(b"")
            commands.append({
                "name": name, "argv": argv, "exit_code": 0, "status": "PASS",
                "wall_seconds": 0.1, "stdout_sha256": sha256(stdout),
                "stderr_sha256": sha256(b""), "stdout_bytes": len(stdout), "stderr_bytes": 0,
            })
        self.manifest = {
            "schema_version": "0.1", "run_id": "fixture-only", "kind": "DEVELOPMENT",
            "status": "PASS", "commit": "1" * 40, "dirty": False,
            "source_tree_sha256": "2" * 64, "source_tree_after_sha256": "2" * 64,
            "python": "fixture", "platform": "fixture", "machine": "fixture",
            "environment_policy": "ALLOWLIST_NO_CREDENTIALS",
            "started_utc": "2026-10-20T00:00:00Z", "commands": commands,
            "limitations": ["Synthetic unit-test fixture, not real accepted evidence"],
        }
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        content = canonical_json(self.manifest)
        (self.directory / "manifest.json").write_bytes(content)
        (self.directory / "manifest.sha256").write_text(sha256(content) + "\n")

    def test_complete_fixture_passes_structural_integrity_only(self):
        self.assertEqual(verify(self.directory), [])

    def test_raw_log_corruption_detected(self):
        (self.directory / "tests.stdout.log").write_bytes(b"tampered")
        self.assertTrue(verify(self.directory))

    def test_manifest_corruption_detected(self):
        with (self.directory / "manifest.json").open("ab") as stream:
            stream.write(b"\n")
        self.assertIn("Manifest checksum mismatch", verify(self.directory))

    def test_missing_log_detected(self):
        (self.directory / "tests.stderr.log").unlink()
        self.assertTrue(verify(self.directory))

    def test_command_inventory_cannot_be_replaced(self):
        self.manifest["commands"][0]["name"] = "invented"
        self.save()
        self.assertTrue(verify(self.directory))

    def test_wrong_argv_detected(self):
        self.manifest["commands"][0]["argv"] = [sys.executable, "-c", "pass"]
        self.save()
        self.assertTrue(any("argv mismatch" in p for p in verify(self.directory)))

    def test_false_green_exit_code_detected(self):
        self.manifest["commands"][0]["exit_code"] = 8
        self.save()
        self.assertTrue(verify(self.directory))

    def test_changed_source_detected(self):
        self.manifest["source_tree_after_sha256"] = "3" * 64
        self.save()
        self.assertIn("Source changed during run", verify(self.directory))

    def test_dirty_acceptance_detected(self):
        self.manifest.update(kind="ACCEPTANCE_CANDIDATE", dirty=True)
        self.save()
        self.assertIn("Dirty acceptance candidate", verify(self.directory))

    def test_zero_or_all_skipped_counts_detected_even_with_rehashed_logs(self):
        for output in (
            b"COUNTS discovered=0 executed=0 skipped=0\n",
            b"COUNTS discovered=1 executed=1 skipped=1\n",
        ):
            (self.directory / "tests.stdout.log").write_bytes(output)
            self.manifest["commands"][-1].update(
                stdout_bytes=len(output), stdout_sha256=sha256(output),
            )
            self.save()
            self.assertTrue(any("test execution" in p for p in verify(self.directory)))

