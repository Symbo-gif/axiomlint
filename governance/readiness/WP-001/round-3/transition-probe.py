"""Independent round-3 bounded probe; execute ONLY from authoritative laptop repo.

All changed session/package/finding records exist only in Python objects.
Corrected real test methods run without their disk-writing setup or mutations.
Synthetic transition inputs are not actual readiness, S2 or finding dispositions.
"""
import copy
import json
from pathlib import Path
from unittest.mock import patch
import axiomlint.governance as g
from axiomlint.schema import load_json
from local_check import source_identity
import test_governance as t
import test_wp_001_ratification as r

root = Path.cwd()
before = source_identity(root)
assert before[0] == "846b0dcbae94b0eb268fe10571c395c90a4f1228"
assert before[2] == "81f219a370872e93bae912093f2d1b54396258aea2536b895b09dc037730de5f"
base = {}
state = {}
for rel in ("governance/sessions/index.json",
            "governance/work-packages/index.json",
            "governance/registers/findings.json"):
    base[rel] = load_json(root / rel)
base["governance/sessions/index.json"][0].update(
    status="CLOSED", commit=before[0],
    report="governance/sessions/WP-001-S1.md",
)
base["governance/sessions/index.json"][1].update(status="PLANNED")

def reset():
    state.clear()
    state.update(copy.deepcopy(base))

def relative(path):
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return None

def loader(path):
    rel = relative(path)
    return copy.deepcopy(state[rel]) if rel in state else load_json(path)

read_bytes = Path.read_bytes
def memory_read_bytes(path):
    rel = relative(path)
    return json.dumps(state[rel]).encode() if rel in state else read_bytes(path)

def mutate(path, fn):
    value = loader(root / path)
    fn(value)
    state[path] = value

def expect(phrase):
    problems = g.check(root)
    assert any(phrase in p for p in problems), problems
    print("EXPECTED_REJECTION", phrase)

reset()
with patch.object(g, "load_json", side_effect=loader), \
     patch.object(t, "load_json", side_effect=loader), \
     patch.object(r, "load_json", side_effect=loader), \
     patch.object(Path, "read_bytes", memory_read_bytes):
    assert g.check(root) == []
    print("S1_CLOSED_S2_PLANNED_PACKAGE_ACTIVE=PASS")
    rat = r.RatificationTests("test_adoption_does_not_close_live_sessions_or_packages")
    rat.root = root
    rat.config = load_json(root / "config/project.json")
    rat.test_adoption_does_not_close_live_sessions_or_packages()
    print("CORRECTED_RATIFICATION_PURITY_AT_CLOSED_S1=PASS")
    names = (
        "test_s2_cannot_start_before_s1_closes",
        "test_self_audit_closed_fails",
        "test_reused_session_commit_fails",
        "test_wrong_audit_revision_fails",
        "test_closed_session_requires_report_and_sha",
    )
    for name in names:
        reset()
        case = t.GovernanceTests(name)
        case.root = root
        case.mutate = mutate
        getattr(case, name)()
        print("CORRECTED_OR_RETAINED_REAL_METHOD=PASS", name)
    reset()
    sessions = state["governance/sessions/index.json"]
    sessions[1].update(
        status="IN_PROGRESS", actor="SYNTHETIC-PROBE-ONLY independent auditor",
        context_id="SYNTHETIC-PROBE-ONLY S2 context", independent=True,
    )
    assert g.check(root) == []
    print("HYPOTHETICAL_DISTINCT_S2_AFTER_CLOSED_S1=PASS_NOT_ACTUAL_S2")
    sessions[1].update(
        status="CLOSED", commit="3" * 40, reviewed_commit=before[0],
        report="governance/sessions/WP-001-S1.md",
    )
    assert g.check(root) == []
    print("HYPOTHETICAL_DISTINCT_AUDIT_COMMIT_AND_REVIEWED_HEAD=PASS")
    reset()
    state["governance/work-packages/index.json"][0]["status"] = "CLOSED"
    for finding in state["governance/registers/findings.json"]:
        if finding["id"] == "READINESS-WP001-001":
            finding["status"] = "VERIFIED"
    assert all(row["status"] == "OPEN"
               for row in load_json(root / "governance/registers/deviations.json"))
    expect("blocking finding/deviation unresolved")
    expect("CLOSED before S1-S4 complete")
    print("OPEN_DEV001_DEV002_STILL_BLOCK_CLOSURE_WITH_READINESS_FIX_VERIFIED=PASS")
    reset()
    assert g.check(root) == []

assert source_identity(root) == before
print("PROBE=PASS real_corrected_or_retained_methods=6 actual_source_unchanged=True")
print("All transition/disposition inputs were in-memory only; no S2 or live-state changes.")
