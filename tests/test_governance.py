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

    def test_current_constitution_is_ratified_and_wp001_closed(self):
        self.assertEqual(check(self.root), [])
        config = load_json(self.root / "config/project.json")
        self.assertEqual(config["approval"], "APPROVED")
        packages = load_json(self.root / "governance/work-packages/index.json")
        self.assertEqual([row["id"] for row in packages if row["status"] == "CLOSED"], ["WP-001"])

    def test_all_36_packages_present_and_wp002_active(self):
        packages = load_json(self.root / "governance/work-packages/index.json")
        self.assertEqual(len(packages), 36)
        self.assertEqual([x["id"] for x in packages if x["status"] == "ACTIVE"], ["WP-002"])
        self.assertEqual([x["id"] for x in packages if x["status"] == "CLOSED"], ["WP-001"])

    def test_multiple_active_packages_fail(self):
        self.mutate("governance/work-packages/index.json", lambda x: x[2].update(
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
        # Explicitly establish the forbidden predecessor state, even when the
        # actual project has legitimately progressed past S1.
        def change(rows):
            rows[0].update(status="IN_PROGRESS")
            rows[1].update(status="IN_PROGRESS")
        self.mutate("governance/sessions/index.json", change)
        self.assert_problem("started before predecessors closed")

    def closed_s1_with_synthetic_readiness(self):
        """Isolated stage-order fixture, not real approval authentication."""
        sessions = load_json(self.root / "governance/sessions/index.json")
        fixture = {
            "fixture_only": True,
            "decision": "APPROVE_S1_EXIT",
            "reviewed_commit": "1" * 40,
            "source_tree_sha256": "2" * 64,
            "reviewer_context": "unit-fixture-independent-readiness-context",
            "implementation_context": sessions[0]["context_id"],
            "authority": "governance/charter/AMD-002-delegated-decisions.md",
            "scope": "Synthetic S1 stage-order fixture; not S2 or package closure",
        }
        self.assertNotEqual(fixture["reviewer_context"], fixture["implementation_context"])
        relative = "governance/readiness/unit-fixture-s1.json"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(fixture))
        def reset_to_s1_exit(rows):
            rows[0].update(status="CLOSED", commit=fixture["reviewed_commit"], report=relative)
            rows[1].update(status="PLANNED", commit="", report="", actor="", context_id="", independent=False, reviewed_commit="")
            rows[2].update(status="BLOCKED", commit="", report="", actor="", context_id="", independent=False, reviewed_commit="")
            rows[3].update(status="BLOCKED", commit="", report="", actor="", context_id="", independent=False, reviewed_commit="")
            rows[:] = rows[:4]
        self.mutate("governance/sessions/index.json", reset_to_s1_exit)
        def reset_wps(rows):
            rows[0].update(status="ACTIVE", acceptance_evidence=[], closure_approval_ref="")
            rows[1].update(status="PLANNED", approval="PENDING", approval_ref="")
        self.mutate("governance/work-packages/index.json", reset_wps)
        return fixture

    def test_source_bound_s1_exit_allows_s2_to_remain_blocked(self):
        fixture = self.closed_s1_with_synthetic_readiness()
        self.mutate("governance/sessions/index.json", lambda rows: rows[1].update(status="BLOCKED"))
        self.assertEqual(check(self.root), [])
        sessions = load_json(self.root / "governance/sessions/index.json")
        self.assertEqual(sessions[0]["commit"], fixture["reviewed_commit"])
        self.assertEqual(sessions[1]["status"], "BLOCKED")

    def test_s2_can_start_after_s1_closes_without_merging_sessions(self):
        self.closed_s1_with_synthetic_readiness()
        self.mutate("governance/sessions/index.json", lambda rows: rows[1].update(
            status="IN_PROGRESS", actor="unit-fixture-independent-auditor",
            context_id="unit-fixture-s2-context", independent=True,
        ))
        self.assertEqual(check(self.root), [])
        sessions = load_json(self.root / "governance/sessions/index.json")
        self.assertNotEqual(sessions[0]["context_id"], sessions[1]["context_id"])
        self.assertEqual(sessions[2]["status"], "BLOCKED")
        self.assertEqual(sessions[3]["status"], "BLOCKED")

    def test_s1_exit_does_not_waive_open_d2_package_closure_block(self):
        self.closed_s1_with_synthetic_readiness()
        self.mutate("governance/registers/deviations.json", lambda rows: rows[0].update(status="OPEN"))
        self.mutate("governance/work-packages/index.json", lambda rows: rows[0].update(status="CLOSED"))
        self.assert_problem("blocking finding/deviation unresolved")
        self.assert_problem("CLOSED before S1-S4 complete")

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
        # Negative fixture establishing premature closure conditions.
        self.mutate("governance/work-packages/index.json",
                    lambda x: x[0].update(status="CLOSED", approval="PENDING", approval_ref="", acceptance_evidence=[]))
        self.mutate("governance/sessions/index.json",
                    lambda rows: rows[3].update(status="IN_PROGRESS", commit=""))
        self.mutate("governance/registers/deviations.json",
                    lambda rows: rows[0].update(status="OPEN"))
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
        # Negative fixtures must explicitly remove fields, not assume live records are empty.
        self.mutate("governance/sessions/index.json",
                    lambda x: x[0].update(status="CLOSED", commit="", report=""))
        self.assert_problem("closed session needs commit SHA")
        self.assert_problem("invalid repository reference")

    def test_d1_d2_waiver_prohibited(self):
        risks = load_json(self.root / "governance/registers/risks.json")
        value = {**risks[0], "id": "WAIVE-001", "category": "WAIVER"}
        (self.root / "governance/registers/waivers.json").write_text(json.dumps([value]))
        self.assert_problem("D1/D2 waiver prohibited")
