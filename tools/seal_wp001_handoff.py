"""Author snapshot/pin writer. Does not approve readiness or start S2."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axiomlint.schema import load_json, validate
from check_wp001_delivery import MANIFEST, RECORD, check, snapshot
from local_check import source_identity
from verify_local_run import verify


def encode(value: dict) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def write_new(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)


def write_snapshot(root: Path = ROOT) -> None:
    value = snapshot(root)
    validate(value, load_json(root / "schemas/wp001-artifacts.schema.json"))
    write_new(root / MANIFEST, encode(value))
    print(f"AUTHOR_SNAPSHOT={root / MANIFEST}")


def validate_run_pair(main: dict, clone: dict, identity: tuple[str, bool, str]) -> None:
    commit, dirty, source_tree = identity
    if dirty:
        raise ValueError("Handoff pin requires a clean committed source tree")
    for row in (main, clone):
        if (
            row["status"] != "PASS" or row["kind"] != "ACCEPTANCE_CANDIDATE" or row["dirty"]
            or row["commit"] != commit or row["source_tree_sha256"] != source_tree
            or row["source_tree_after_sha256"] != source_tree
        ):
            raise ValueError("Handoff pin requires matching clean passed main/clone identities")
    if main["run_id"] == clone["run_id"]:
        raise ValueError("Main and fresh-clone runs must be distinct actual records")


def write_pin(main_directory: Path, clone_directory: Path, root: Path = ROOT) -> Path:
    errors = check(root)
    if errors:
        raise ValueError("Author delivery is not internally consistent: " + "; ".join(errors))
    live = load_json(root / "governance/sessions/index.json")
    current_s1 = next(row for row in live if row["package"] == "WP-001" and row["stage"] == "S1")
    if current_s1["status"] != "IN_PROGRESS":
        raise ValueError("A new author pin cannot misstate a later live S1 transition")
    identity = source_identity(root)
    for directory in (main_directory, clone_directory):
        if not directory.resolve().is_relative_to((root / "artifacts").resolve()):
            raise ValueError("Pin inputs must be local ignored artifact directories")
        problems = verify(directory, root=root, check_current=True)
        if problems:
            raise ValueError("Raw run verification failed: " + "; ".join(problems))
    records = [load_json(path / "manifest.json") for path in (main_directory, clone_directory)]
    validate_run_pair(*records, identity)
    record = load_json(root / RECORD)
    payload = {
        "schema_version": "0.1", "kind": "AUTHOR_S1_HANDOFF_PIN",
        "source_commit": identity[0], "source_tree_sha256": identity[2],
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "author_context": record["context_id"],
        "artifact_manifest_sha256": hashlib.sha256((root / MANIFEST).read_bytes()).hexdigest(),
        "brief_sha256": record["frozen_brief_sha256"],
        "scope_authorization": record["scope_authorization"],
        "author_checks": "PASS",
        "formal_readiness": "PENDING_SEPARATE_CONTEXT",
        "s1_formal_state": "IN_PROGRESS", "s2": "NOT_PERFORMED",
        "package_closure": "NOT_GRANTED",
        "runs": [
            {
                "role": role, "run_id": value["run_id"], "directory": str(directory.resolve()),
                "manifest_sha256": hashlib.sha256((directory / "manifest.json").read_bytes()).hexdigest(),
            }
            for role, value, directory in zip(
                ("MAIN_AUTHOR", "FRESH_LOCAL_CLONE_SAME_AUTHOR"), records,
                (main_directory, clone_directory),
            )
        ],
        "limitations": [
            "Same author and laptop; not independent readiness, S2, authenticated provenance or scientific result",
            "DEV-001/DEV-002 and FIND-S1-001 remain unverified; separate-context entry decision required",
            "Verify this pin against actual Git/source before relying on it",
        ],
    }
    validate(payload, load_json(root / "schemas/wp001-handoff-pin.schema.json"))
    output = root / record["pin_receipt"]
    if not output.parent.resolve().is_relative_to((root / "artifacts").resolve()):
        raise ValueError("Pin output escapes local artifact directory")
    write_new(output, encode(payload))
    if source_identity(root) != identity:
        raise ValueError("Source changed while writing handoff pin")
    print(f"AUTHOR_AUDIT_TARGET={output}")
    print(f"PIN_SHA256={hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(f"SOURCE_COMMIT={identity[0]} READINESS=PENDING_SEPARATE_CONTEXT S2=NOT_PERFORMED")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--snapshot", action="store_true")
    action.add_argument("--pin", action="store_true")
    parser.add_argument("--main-run", type=Path)
    parser.add_argument("--clone-run", type=Path)
    args = parser.parse_args()
    try:
        if args.snapshot:
            write_snapshot()
        else:
            if not args.main_run or not args.clone_run:
                parser.error("--pin requires --main-run and --clone-run")
            write_pin(args.main_run, args.clone_run)
    except (OSError, ValueError, KeyError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
