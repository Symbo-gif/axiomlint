"""Author delivery guards, not an independent S2 review."""

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from axiomlint.schema import InvalidRecord, load_json, validate
from check_wp001_delivery import MANIFEST, RECORD, check, expected_paths, snapshot
from seal_wp001_handoff import validate_run_pair, write_new, write_snapshot


class DeliveryArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", "artifacts", "__pycache__", ".venv",
        ))
        self.record = load_json(self.root / RECORD)
        self.schema = load_json(self.root / "schemas/wp001-s1-delivery.schema.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_author_delivery_is_consistent_not_approved(self):
        self.assertEqual(check(self.root), [])
        self.assertEqual(self.record["readiness_approval"], "PENDING_SEPARATE_CONTEXT")
        self.assertEqual(self.record["independent_audit"], "NOT_PERFORMED")

    def test_exact_original_eight_acceptance_clauses(self):
        self.assertEqual([x["id"] for x in self.record["criteria"]],
                         [f"WP-001-C{n:02d}" for n in range(1, 9)])
        self.assertTrue(all(x["independent_assessment"] == "PENDING" for x in self.record["criteria"]))

    def test_all_new_constitutional_deliverables_have_snapshot_bytes(self):
        paths = expected_paths(self.root)
        for path in (
            "governance/standards/claim-glossary.md",
            "governance/standards/license-policy.md",
            "governance/standards/amendments-and-exceptions.md",
            "governance/decisions/authority-map.md",
        ):
            self.assertIn(path, paths)

    def test_mutable_live_status_is_not_frozen_forever(self):
        paths = expected_paths(self.root)
        self.assertNotIn("governance/sessions/index.json", paths)
        self.assertNotIn("governance/registers/findings.json", paths)
        self.assertIn("governance/execution/WP-001/S1/record.json", paths)

    def test_changed_glossary_invalidates_author_snapshot(self):
        with (self.root / "governance/standards/claim-glossary.md").open("a") as stream:
            stream.write("\nUnreviewed change\n")
        self.assertTrue(any("snapshot" in item for item in check(self.root)))

    def test_missing_license_policy_fails(self):
        (self.root / "governance/standards/license-policy.md").unlink()
        self.assertTrue(check(self.root))

    def test_missing_acceptance_clause_fails(self):
        value = copy.deepcopy(self.record)
        value["criteria"].pop()
        (self.root / RECORD).write_text(json.dumps(value))
        self.assertTrue(check(self.root))

    def test_duplicate_criterion_fails(self):
        value = copy.deepcopy(self.record)
        value["criteria"][1]["id"] = value["criteria"][0]["id"]
        (self.root / RECORD).write_text(json.dumps(value))
        self.assertTrue(check(self.root))

    def test_author_cannot_claim_independent_readiness(self):
        value = {**self.record, "readiness_approval": "APPROVED"}
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_author_cannot_claim_s2_completed(self):
        with self.assertRaises(InvalidRecord):
            validate({**self.record, "independent_audit": "PASS"}, self.schema)

    def test_author_cannot_close_package_in_delivery_record(self):
        with self.assertRaises(InvalidRecord):
            validate({**self.record, "package_closure": "CLOSED"}, self.schema)

    def test_changed_project_license_fails(self):
        with (self.root / "LICENSE").open("a") as stream:
            stream.write("\nChanged notice\n")
        self.assertTrue(any("license" in item.lower() for item in check(self.root)))

    def test_material_inventory_is_not_full_clearance(self):
        materials = load_json(self.root / "governance/licenses/foundation-materials.json")
        schema = load_json(self.root / "schemas/wp001-materials.schema.json")
        validate(materials, schema)
        with self.assertRaises(InvalidRecord):
            validate({**materials, "release_clearance": "GRANTED"}, schema)

    def test_manifest_cannot_omit_a_required_artifact(self):
        value = load_json(self.root / MANIFEST)
        value["files"].pop()
        (self.root / MANIFEST).write_text(json.dumps(value))
        self.assertTrue(any("artifact set" in item for item in check(self.root)))

    def test_existing_snapshot_is_not_overwritten(self):
        before = (self.root / MANIFEST).read_bytes()
        with self.assertRaises(FileExistsError):
            write_snapshot(self.root)
        self.assertEqual((self.root / MANIFEST).read_bytes(), before)

    def test_missing_scope_authorization_fails(self):
        (self.root / self.record["scope_authorization"]).unlink()
        self.assertTrue(check(self.root))

    def test_frozen_brief_is_not_silently_rewritten(self):
        with (self.root / self.record["frozen_brief"]).open("a") as stream:
            stream.write("\nChanged source brief\n")
        self.assertTrue(any("Frozen S1 brief" in item for item in check(self.root)))

    def test_author_manifest_itself_is_excluded_from_its_byte_list(self):
        self.assertNotIn(MANIFEST, expected_paths(self.root))
        self.assertEqual(snapshot(self.root), load_json(self.root / MANIFEST))


class HandoffPinGuardTests(unittest.TestCase):
    def setUp(self):
        self.identity = ("1" * 40, False, "2" * 64)
        self.main = {
            "run_id": "synthetic-unit-main", "status": "PASS", "kind": "ACCEPTANCE_CANDIDATE",
            "dirty": False, "commit": "1" * 40,
            "source_tree_sha256": "2" * 64, "source_tree_after_sha256": "2" * 64,
        }
        self.clone = {**self.main, "run_id": "synthetic-unit-clone"}

    def test_pair_guard_accepts_matching_synthetic_identities(self):
        validate_run_pair(self.main, self.clone, self.identity)

    def test_pair_guard_rejects_dirty_current_source(self):
        with self.assertRaises(ValueError):
            validate_run_pair(self.main, self.clone, ("1" * 40, True, "2" * 64))

    def test_pair_guard_rejects_failed_run(self):
        with self.assertRaises(ValueError):
            validate_run_pair(self.main, {**self.clone, "status": "FAIL"}, self.identity)

    def test_pair_guard_rejects_development_run(self):
        with self.assertRaises(ValueError):
            validate_run_pair({**self.main, "kind": "DEVELOPMENT"}, self.clone, self.identity)

    def test_pair_guard_rejects_different_source(self):
        with self.assertRaises(ValueError):
            validate_run_pair(self.main, {**self.clone, "commit": "3" * 40}, self.identity)

    def test_pair_guard_rejects_different_tree(self):
        with self.assertRaises(ValueError):
            validate_run_pair(self.main, {**self.clone, "source_tree_sha256": "3" * 64}, self.identity)

    def test_pair_guard_rejects_reusing_same_run(self):
        with self.assertRaises(ValueError):
            validate_run_pair(self.main, self.main, self.identity)

    def test_pin_writer_refuses_existing_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pin.json"
            write_new(path, b"first")
            with self.assertRaises(FileExistsError):
                write_new(path, b"replacement")
            self.assertEqual(path.read_bytes(), b"first")
