import json
import shutil
import tempfile
import unittest
from pathlib import Path

from axiomlint.governance import check
from axiomlint.schema import load_json

ROOT = Path(__file__).resolve().parents[1]


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", "artifacts", "__pycache__", ".venv",
        ))

    def tearDown(self):
        self.tmp.cleanup()

    def mutate(self, path, fn):
        target = self.root / path
        value = load_json(target)
        fn(value)
        target.write_text(json.dumps(value), encoding="utf-8")

    def assert_problem(self, phrase):
        problems = check(self.root)
        self.assertTrue(any(phrase in p for p in problems), problems)

    def test_current_draft_is_structurally_valid_not_approved(self):
        self.assertEqual(check(self.root), [])
        config = load_json(self.root / "config/project.json")
        self.assertEqual(config["approval"], "PENDING")

    def test_all_36_packages_present_only_first_active(self):
        packages = load_json(self.root / "governance/work-packages/index.json")
        self.assertEqual(len(packages), 36)
        self.assertEqual([x["id"] for x in packages if x["status"] == "ACTIVE"], ["WP-001"])
        self.assertFalse(any(x["status"] == "CLOSED" for x in packages))

    def test_multiple_active_packages_fail(self):
        self.mutate("governance/work-packages/index.json", lambda x: x[1].update(
            status="ACTIVE", approval="USER_AUTHORIZED_DRAFTS",
            approval_ref="governance/decisions/authorization.md",
        ))
        self.assert_problem("More than one active")

    def test_dependency_cycle_fails(self):
        self.mutate("governance/work-packages/index.json",
                    lambda x: x[0].update(dependencies=["WP-036"]))
        self.assert_problem("Dependency cycle")

    def test_unknown_dependency_fails(self):
        self.mutate("governance/work-packages/index.json",
                    lambda x: x[5].update(dependencies=["WP-999"]))
        self.assert_problem("missing dependency")

    def test_duplicate_global_id_fails(self):
        self.mutate("governance/requirements/requirements.json", lambda x: x.append(x[0].copy()))
        self.assert_problem("Duplicate global ID")

    def test_orphan_requirement_package_fails(self):
        self.mutate("governance/requirements/requirements.json", lambda x: x[0].update(package="WP-999"))
        self.assert_problem("unknown work package")

    def test_missing_evidence_reference_fails(self):
        self.mutate("governance/requirements/requirements.json",
                    lambda x: x[0].update(evidence=["missing-file.py"]))
        self.assert_problem("missing reference")

    def test_path_traversal_evidence_fails(self):
        self.mutate("governance/requirements/requirements.json",
                    lambda x: x[0].update(evidence=["../outside"]))
        self.assert_problem("invalid repository reference")

    def test_empty_mandatory_register_fails(self):
        self.mutate("governance/requirements/requirements.json", lambda x: x.clear())
        self.assert_problem("Mandatory requirement")

    def test_malformed_register_is_not_silently_accepted(self):
        (self.root / "governance/registers/risks.json").write_text('{"not":"an array"}')
        self.assert_problem("Expected top-level array")

    def test_s2_cannot_start_before_s1_closes(self):
        self.mutate("governance/sessions/index.json", lambda x: x[1].update(status="IN_PROGRESS"))
        self.assert_problem("started before predecessors closed")

    def test_self_audit_closed_fails(self):
        def change(x):
            for i in (0, 1):
                x[i].update(status="CLOSED", commit=str(i + 1) * 40,
                            report="governance/sessions/WP-001-S1.md")
            x[1].update(actor=x[0]["actor"], context_id=x[0]["context_id"],
                        independent=False, reviewed_commit=x[0]["commit"])
        self.mutate("governance/sessions/index.json", change)
        self.assert_problem("S2 not independent")
        self.assert_problem("S2 actor not distinct")
        self.assert_problem("S2 context not distinct")

    def test_reused_session_commit_fails(self):
        def change(x):
            for i in (0, 1):
                x[i].update(status="CLOSED", commit="1" * 40,
                            report="governance/sessions/WP-001-S1.md")
            x[1].update(actor="independent human", context_id="other",
                        independent=True, reviewed_commit=x[0]["commit"])
        self.mutate("governance/sessions/index.json", change)
        self.assert_problem("distinct commits")

    def test_wrong_audit_revision_fails(self):
        def change(x):
            for i in (0, 1):
                x[i].update(status="CLOSED", commit=str(i + 1) * 40,
                            report="governance/sessions/WP-001-S1.md")
            x[1].update(actor="reviewer", context_id="other",
                        independent=True, reviewed_commit="9" * 40)
        self.mutate("governance/sessions/index.json", change)
        self.assert_problem("audit reviewed wrong S1 commit")

    def test_premature_package_closure_fails(self):
        self.mutate("governance/work-packages/index.json", lambda x: x[0].update(status="CLOSED"))
        self.assert_problem("CLOSED before S1-S4 complete")
        self.assert_problem("CLOSED without charter/scope approval")
        self.assert_problem("CLOSED without acceptance evidence")
        self.assert_problem("blocking finding/deviation unresolved")

    def test_schema_keyword_escape_fails(self):
        self.mutate("schemas/project.schema.json", lambda x: x.update(**{"anyOf": [{}]}))
        self.assert_problem("Unsupported schema keywords")

    def test_plan_baseline_tampering_fails(self):
        with (self.root / "docs/reference/axiomlint-plan.md").open("a") as stream:
            stream.write("\nUnapproved change\n")
        self.assert_problem("differs from pinned baseline")

    def test_closed_session_requires_report_and_sha(self):
        self.mutate("governance/sessions/index.json", lambda x: x[0].update(status="CLOSED"))
        self.assert_problem("closed session needs commit SHA")

    def test_d1_d2_waiver_prohibited(self):
        risks = load_json(self.root / "governance/registers/risks.json")
        value = {**risks[0], "id": "WAIVE-001", "category": "WAIVER"}
        (self.root / "governance/registers/waivers.json").write_text(json.dumps([value]))
        self.assert_problem("D1/D2 waiver prohibited")

