"""Source-bound adoption checks; neither principal authentication nor S2."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from axiomlint.authority import ACTIVE, APPROVAL, check_ratification, checked_file
from axiomlint.governance import check as check_governance
from axiomlint.schema import InvalidRecord, load_json, validate

ROOT = Path(__file__).resolve().parents[1]


class RatificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", "artifacts", "__pycache__", ".venv",
        ))
        self.config = load_json(self.root / "config/project.json")

    def tearDown(self):
        self.tmp.cleanup()

    def record(self):
        return load_json(self.root / APPROVAL)

    def active(self):
        return load_json(self.root / ACTIVE)

    def replace_record_and_rehash(self, key, value):
        record = self.record()
        record[key] = value
        path = self.root / APPROVAL
        path.write_text(json.dumps(record))
        active = self.active()
        active["approval_record_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.root / ACTIVE).write_text(json.dumps(active))

    def test_actual_record_validates_against_pinned_schema(self):
        validate(self.record(), load_json(self.root / "schemas/constitutional-ratification.schema.json"))

    def test_active_source_bound_constitution_passes(self):
        self.assertEqual(check_ratification(self.root, self.config), [])

    def test_approval_flag_without_active_record_fails(self):
        (self.root / ACTIVE).unlink()
        self.assertTrue(check_ratification(self.root, self.config))

    def test_missing_principal_record_fails(self):
        (self.root / APPROVAL).unlink()
        self.assertTrue(check_ratification(self.root, self.config))

    def test_record_byte_tampering_fails(self):
        with (self.root / APPROVAL).open("a") as stream:
            stream.write("\n")
        self.assertTrue(any("record digest" in x for x in check_ratification(self.root, self.config)))

    def test_changed_charter_fails(self):
        with (self.root / "governance/charter/CHARTER.md").open("a") as stream:
            stream.write("\nUnapproved edit\n")
        self.assertTrue(any("document digest" in x for x in check_ratification(self.root, self.config)))

    def test_changed_local_only_amendment_fails(self):
        with (self.root / "governance/charter/AMD-001-local-only.md").open("a") as stream:
            stream.write("\nUnapproved edit\n")
        self.assertTrue(check_ratification(self.root, self.config))

    def test_changed_delegation_amendment_fails(self):
        with (self.root / "governance/charter/AMD-002-delegated-decisions.md").open("a") as stream:
            stream.write("\nUnapproved edit\n")
        self.assertTrue(check_ratification(self.root, self.config))

    def test_changed_packet_fails(self):
        with (self.root / self.record()["packet"]).open("a") as stream:
            stream.write("\nChanged scope\n")
        self.assertTrue(check_ratification(self.root, self.config))

    def test_pending_configuration_cannot_claim_active_baseline(self):
        self.assertTrue(check_ratification(self.root, {**self.config, "approval": "PENDING"}))

    def test_original_general_grant_is_not_rewritten_as_ratification(self):
        grant = load_json(self.root / "governance/decisions/delegated-authority.json")
        self.assertEqual(grant["ratification"], "NOT_A_RATIFICATION")
        self.assertEqual(self.record()["answer"], "Ratify bounded delegation")

    def test_rehashed_false_principal_still_fails(self):
        self.replace_record_and_rehash("principal", "Computer assistant")
        self.assertTrue(check_ratification(self.root, self.config))

    def test_rehashed_false_answer_still_fails(self):
        self.replace_record_and_rehash("answer", "Keep ratification pending")
        self.assertTrue(check_ratification(self.root, self.config))

    def test_active_target_list_cannot_expand(self):
        active = self.active()
        active["targets"].append({"path": "extra.md", "sha256": "0" * 64})
        (self.root / ACTIVE).write_text(json.dumps(active))
        self.assertTrue(check_ratification(self.root, self.config))

    def test_unsafe_authority_reference_rejected(self):
        with self.assertRaises(InvalidRecord):
            checked_file(self.root, "../outside")

    def test_symlink_charter_rejected(self):
        path = self.root / "governance/charter/CHARTER.md"
        target = Path(self.tmp.name) / "target"
        target.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(target)
        self.assertTrue(check_ratification(self.root, self.config))

    def test_symlink_approval_rejected(self):
        path = self.root / APPROVAL
        target = Path(self.tmp.name) / "approval"
        target.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(target)
        self.assertTrue(check_ratification(self.root, self.config))

    def test_adoption_does_not_close_live_sessions_or_packages(self):
        # Ratification must not change live state, whatever the legitimate
        # current stage is. Do not freeze the project's historical open state.
        paths = [
            self.root / "governance/sessions/index.json",
            self.root / "governance/work-packages/index.json",
        ]
        before = [path.read_bytes() for path in paths]
        self.assertEqual(check_ratification(self.root, self.config), [])
        self.assertEqual([path.read_bytes() for path in paths], before)
        self.assertIn("PACKAGE_OR_PHASE_CLOSURE", self.record()["not_approved"])

    def test_ratification_check_preserves_already_closed_s1_fixture(self):
        # This isolated fixture is not a real exit approval. It proves that
        # constitution checking neither closes nor reopens legitimate stages.
        path = self.root / "governance/sessions/index.json"
        sessions = load_json(path)
        sessions[0].update(status="CLOSED", commit="1" * 40)
        path.write_text(json.dumps(sessions))
        before = path.read_bytes()
        self.assertEqual(check_ratification(self.root, self.config), [])
        self.assertEqual(path.read_bytes(), before)

    def test_full_governance_gate_enforces_ratified_bytes(self):
        with (self.root / "governance/charter/AMD-002-delegated-decisions.md").open("a") as stream:
            stream.write("\nSilently widened delegation\n")
        self.assertTrue(any("document digest" in x for x in check_governance(self.root)))

    def test_principal_must_match_current_maintainer(self):
        self.assertTrue(check_ratification(self.root, {**self.config, "maintainer": "Different owner"}))

    def test_source_revision_mismatch_fails(self):
        active = self.active()
        active["ratified_source_commit"] = "0" * 40
        (self.root / ACTIVE).write_text(json.dumps(active))
        self.assertTrue(any("revision mismatch" in x for x in check_ratification(self.root, self.config)))

    def test_historical_pending_scaffold_without_activation_is_supported(self):
        (self.root / ACTIVE).unlink()
        self.assertEqual(check_ratification(self.root, {**self.config, "approval": "PENDING"}), [])
