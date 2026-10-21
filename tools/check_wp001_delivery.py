"""WP-001 S1 artifact consistency only; never grants readiness or audit approval."""

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axiomlint.authority import checked_file
from axiomlint.governance import REGISTERS, check as governance_check
from axiomlint.schema import InvalidRecord, load_json, validate

BASE = "governance/execution/WP-001/S1"
RECORD = f"{BASE}/record.json"
MANIFEST = f"{BASE}/artifacts.json"
CRITERIA = [
    "Approved charter", "Authority map", "License policy", "Claim glossary",
    "Amendment rules", "Exception rules", "Initialized decision/risk/finding/session registers",
    "Governance validator passing",
]
SNAPSHOT_OMITS = (
    "This manifest, mutable live registers/status, ignored logs, and post-commit pin receipts "
    "are excluded; the Git pin binds the complete author source"
)


def expected_paths(root: Path) -> list[str]:
    record = load_json(checked_file(root, RECORD))
    paths = {
        RECORD, record["handoff"], record["scope_authorization"], record["constitution"],
        record["frozen_brief"], "LICENSE", "README.md", "config/project.json",
        "governance/STATE.md", "governance/sessions/WP-001-S1.md",
        "governance/sessions/index.json", "governance/work-packages/index.json",
        "governance/work-packages/WP-001.md", "governance/requirements/requirements.json",
        "governance/approvals/APR-001-constitutional-ratification.json",
        "governance/approvals/APR-001-constitutional-ratification.md",
        "governance/charter/AMD-001-local-only.md", "governance/charter/AMD-002-delegated-decisions.md",
        f"{BASE}/scope-reconciliation.md", "docs/user-guide/S2-AUDIT-PROMPT.md",
        "tools/check_wp001_delivery.py", "tools/seal_wp001_handoff.py",
        "schemas/wp001-s1-delivery.schema.json", "schemas/wp001-materials.schema.json",
        "schemas/wp001-artifacts.schema.json", "schemas/wp001-handoff-pin.schema.json",
    }
    paths.update(f"governance/registers/{name}.json" for name in REGISTERS)
    paths.update(str(path.relative_to(root)) for path in (root / "governance/standards").glob("*.md"))
    for row in record["criteria"]:
        paths.update(row["artifacts"])
    # Live progress is not frozen forever by an author's S1 snapshot. The full
    # Git pin captures its original state; future valid stage records are not
    # evidence tampering merely because their status legitimately changes.
    mutable = {
        "README.md", "governance/STATE.md", "governance/sessions/WP-001-S1.md",
        "governance/sessions/index.json", "governance/work-packages/index.json",
        "governance/requirements/requirements.json",
        *(f"governance/registers/{name}.json" for name in REGISTERS),
    }
    return sorted(paths - mutable)


def snapshot(root: Path) -> dict:
    rows = []
    for relative in expected_paths(root):
        data = checked_file(root, relative).read_bytes()
        rows.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return {
        "schema_version": "0.1", "kind": "AUTHOR_S1_ARTIFACT_SNAPSHOT",
        "omits": SNAPSHOT_OMITS,
        "files": rows,
    }


def check(root: Path = ROOT) -> list[str]:
    errors = governance_check(root)
    try:
        record = load_json(checked_file(root, RECORD))
        validate(record, load_json(root / "schemas/wp001-s1-delivery.schema.json"))
        if [row["id"] for row in record["criteria"]] != [f"WP-001-C{n:02d}" for n in range(1, 9)]:
            errors.append("S1 acceptance criteria are not exactly C01-C08 in order")
        if [row["criterion"] for row in record["criteria"]] != CRITERIA:
            errors.append("Original WP-001 acceptance criterion mapping changed")
        brief = checked_file(root, record["frozen_brief"]).read_bytes()
        if hashlib.sha256(brief).hexdigest() != record["frozen_brief_sha256"]:
            errors.append("Frozen S1 brief changed")
        for relative in (record["scope_authorization"], record["handoff"], record["constitution"]):
            checked_file(root, relative)
        materials = load_json(checked_file(root, "governance/licenses/foundation-materials.json"))
        validate(materials, load_json(root / "schemas/wp001-materials.schema.json"))
        license_record = materials["project_license"]
        if hashlib.sha256(checked_file(root, license_record["path"]).read_bytes()).hexdigest() != license_record["sha256"]:
            errors.append("Project license bytes differ from material inventory")
        manifest = load_json(checked_file(root, MANIFEST))
        validate(manifest, load_json(root / "schemas/wp001-artifacts.schema.json"))
        if manifest != snapshot(root):
            errors.append("S1 artifact set/bytes/digests differ from the author snapshot")
        # Current live states are validated by the normative governance checker,
        # not forced forever to this historical author's IN_PROGRESS snapshot.
    except (InvalidRecord, OSError, UnicodeError, KeyError, ValueError, StopIteration) as exc:
        errors.append(f"S1 delivery: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = check()
    for error in errors:
        print(error, file=sys.stderr)
    print(f"AUTHOR_DELIVERY={'FAIL' if errors else 'PASS'} criteria=8 "
          "readiness=PENDING_SEPARATE_CONTEXT s1=IN_PROGRESS s2=NOT_PERFORMED")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
