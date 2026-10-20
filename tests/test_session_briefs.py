"""Planning integrity tests. These do not execute future package capabilities."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from axiomlint.schema import load_json
from check_session_briefs import check
from render_session_briefs import BASE, STAGES, build, contract_text, digest, field, write
from session_brief_profiles import PROFILES
import run_wp_tests


class SessionBriefTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", "artifacts", "__pycache__", ".venv",
        ))
        self.catalog_path = self.root / BASE / "catalog.json"
        self.catalog = load_json(self.catalog_path)

    def tearDown(self):
        self.tmp.cleanup()

    def save_catalog(self):
        self.catalog_path.write_text(json.dumps(self.catalog), encoding="utf-8")

    def brief(self, number=1, stage="S1"):
        return self.root / BASE / f"WP-{number:03d}" / f"{stage}.md"

    def test_complete_draft_catalogue_valid(self):
        self.assertEqual(check(self.root), [])

    def test_exact_36_by_4_coverage(self):
        self.assertEqual(len(self.catalog["briefs"]), 144)
        self.assertEqual(
            [(row["package"], row["stage"]) for row in self.catalog["briefs"]],
            [(f"WP-{n:03d}", stage) for n in range(1, 37) for stage in STAGES],
        )

    def test_each_stage_contains_its_own_specific_actions(self):
        for row in self.catalog["briefs"]:
            number = int(row["package"][-3:])
            content = (self.root / row["path"]).read_text()
            for action in PROFILES[number][STAGES[row["stage"]][2]]:
                self.assertIn(action, content)

    def test_original_acceptance_retained_all_144(self):
        for row in self.catalog["briefs"]:
            contract = contract_text((self.root / row["declaration"]).read_text())
            self.assertIn(field(contract, "Acceptance evidence"), (self.root / row["path"]).read_text())

    def test_no_findings_still_requires_independent_s3(self):
        for number in range(1, 37):
            content = self.brief(number, "S3").read_text()
            self.assertIn("no-change closure table", content)
            self.assertIn("independent delta", content)

    def test_s2_is_not_given_product_edit_authority(self):
        for number in range(1, 37):
            content = self.brief(number, "S2").read_text()
            self.assertIn("READ_ONLY_PRODUCT", content)
            self.assertIn("not permission for the reviewer to edit", content)

    def test_experiments_require_review_before_execution(self):
        for number in range(30, 34):
            for stage in STAGES:
                content = self.brief(number, stage).read_text()
                self.assertIn("EXP-E2 before any EXP-E3", content)
                self.assertIn("cannot retroactively supply EXP-E2", content)

    def test_calibration_order_conflict_explicit(self):
        self.assertIn("Calibration entry decision:", self.brief(25).read_text())
        self.assertIn("cannot satisfy calibrated G5", self.brief(25).read_text())

    def test_lean_trust_policy_not_only_text_blacklist(self):
        content = self.brief(19).read_text()
        self.assertIn("transitive axiom", content)
        self.assertIn("native_decide/bv_decide", content)
        self.assertIn("kernel-only baseline", content)

    def test_package_boundary_has_previous_wp_s4(self):
        for offset in range(4, 144, 4):
            self.assertEqual(
                self.catalog["briefs"][offset]["predecessor"],
                f"WP-{offset // 4:03d}-S4",
            )

    def test_missing_brief_rejected(self):
        self.brief().unlink()
        self.assertTrue(check(self.root))

    def test_duplicate_id_rejected(self):
        self.catalog["briefs"][1]["id"] = self.catalog["briefs"][0]["id"]
        self.save_catalog()
        self.assertTrue(any("144 unique" in item for item in check(self.root)))

    def test_fabricated_approval_rejected(self):
        self.catalog["approval"] = "APPROVED"
        self.save_catalog()
        self.assertTrue(check(self.root))

    def test_stage_reordering_rejected(self):
        self.catalog["briefs"][0]["stage"] = "S4"
        self.save_catalog()
        self.assertTrue(check(self.root))

    def test_skipped_predecessor_rejected(self):
        self.catalog["briefs"][4]["predecessor"] = "WP-001-S2"
        self.save_catalog()
        self.assertTrue(any("predecessor/successor" in item for item in check(self.root)))

    def test_tampered_brief_rejected(self):
        with self.brief().open("a") as stream:
            stream.write("\nUnauthorized change\n")
        self.assertTrue(check(self.root))

    def test_rehashed_tampering_still_rejected(self):
        path = self.brief()
        path.write_text(path.read_text() + "\nUnauthorized drift\n")
        self.catalog["briefs"][0]["sha256"] = digest(path.read_bytes())
        self.save_catalog()
        self.assertTrue(any("deterministic" in item or "drift" in item for item in check(self.root)))

    def test_changed_profile_source_rejected(self):
        with (self.root / "tools/session_brief_profiles.py").open("a") as stream:
            stream.write("\n# unreviewed source change\n")
        self.assertTrue(any("Input/navigation" in item for item in check(self.root)))

    def test_changed_protocol_rejected(self):
        with (self.root / BASE / "PROTOCOL.md").open("a") as stream:
            stream.write("\nUnreviewed protocol change\n")
        self.assertTrue(check(self.root))

    def test_changed_original_acceptance_rejected(self):
        path = self.root / "governance/work-packages/WP-001.md"
        path.write_text(path.read_text().replace(
            "**Acceptance evidence:**", "**Acceptance evidence:** Unapproved relaxation;", 1,
        ))
        self.assertTrue(any("source contract changed" in item for item in check(self.root)))

    def test_catalogue_path_escape_rejected(self):
        self.catalog["briefs"][0]["path"] = "../outside.md"
        self.save_catalog()
        self.assertTrue(any("Unsafe catalogue path" in item for item in check(self.root)))

    def test_symlink_brief_rejected(self):
        path = self.brief()
        content = path.read_bytes()
        path.unlink()
        target = Path(self.tmp.name) / "outside"
        target.write_bytes(content)
        path.symlink_to(target)
        self.assertTrue(check(self.root))

    def test_removed_declaration_navigation_rejected(self):
        path = self.root / "governance/work-packages/WP-001.md"
        path.write_text(path.read_text().split("<!-- BEGIN GENERATED SESSION BRIEF LINKS -->")[0])
        self.assertTrue(any("navigation drift" in item for item in check(self.root)))

    def test_render_is_deterministic_without_mutating_live_register(self):
        runtime = self.root / "governance/sessions/index.json"
        before = runtime.read_bytes()
        first = build(self.root, self.catalog["baseline_commit"])
        second = build(self.root, self.catalog["baseline_commit"])
        self.assertEqual(first, second)
        self.assertEqual(before, runtime.read_bytes())

    def test_renderer_refuses_to_overwrite_catalogue(self):
        before = self.catalog_path.read_bytes()
        with self.assertRaisesRegex(ValueError, "refuse to overwrite"):
            write(self.root, self.catalog["baseline_commit"])
        self.assertEqual(before, self.catalog_path.read_bytes())


class PackageTestRunnerTests(unittest.TestCase):
    def suite(self):
        return unittest.TestSuite([unittest.FunctionTestCase(lambda: None)])

    def test_empty_package_suite_refuses(self):
        with patch("run_wp_tests.unittest.TestLoader") as loader:
            loader.return_value.discover.return_value = unittest.TestSuite()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(run_wp_tests.run("WP-014"), 1)

    def test_all_skipped_package_suite_refuses(self):
        result = Mock(testsRun=1, skipped=[("fixture", "skip")])
        result.wasSuccessful.return_value = True
        with patch("run_wp_tests.unittest.TestLoader") as loader, patch(
            "run_wp_tests.unittest.TextTestRunner"
        ) as runner, contextlib.redirect_stderr(io.StringIO()):
            loader.return_value.discover.return_value = self.suite()
            runner.return_value.run.return_value = result
            self.assertEqual(run_wp_tests.run("WP-014"), 1)

    def test_failed_package_suite_refuses(self):
        result = Mock(testsRun=1, skipped=[])
        result.wasSuccessful.return_value = False
        with patch("run_wp_tests.unittest.TestLoader") as loader, patch(
            "run_wp_tests.unittest.TextTestRunner"
        ) as runner, contextlib.redirect_stdout(io.StringIO()):
            loader.return_value.discover.return_value = self.suite()
            runner.return_value.run.return_value = result
            self.assertEqual(run_wp_tests.run("WP-014"), 1)

    def test_invalid_package_ids_refuse(self):
        for value in ("WP-000", "WP-037", "../secret", "WP-014;echo bad"):
            with self.assertRaises(ValueError):
                run_wp_tests.run(value)
