"""Fail-closed checks of draft brief coverage, ordering, content and provenance."""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axiomlint.schema import InvalidRecord, load_json, validate
from render_session_briefs import BASE, STAGES, build, contract_text, digest, field
from session_brief_profiles import PROFILES

HEADINGS = (
    "Authority read", "Entry gates", "Scope and non-goals", "Required actions",
    "Required artefacts", "Acceptance and verification matrix", "Verification commands",
    "Stop/block conditions", "Exit gates", "Rollback and retention", "Handoff",
)


def check(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    def safe_file(path: str) -> Path:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise InvalidRecord(f"Unsafe catalogue path: {path}")
        candidate = root / path
        if not candidate.resolve().is_relative_to(root.resolve()):
            raise InvalidRecord(f"Catalogue path escapes root: {path}")
        for part in (candidate, *candidate.parents):
            if part == root.parent:
                break
            if part.is_symlink():
                raise InvalidRecord(f"Symlink catalogue path: {path}")
        if not candidate.is_file():
            raise InvalidRecord(f"Missing catalogue file: {path}")
        return candidate
    try:
        catalog = load_json(safe_file(f"{BASE}/catalog.json"))
        validate(catalog, load_json(root / "schemas/session-brief-catalog.schema.json"))
        expected_ids = [
            f"BRIEF-WP-{n:03d}-{stage}" for n in range(1, 37) for stage in ("S1", "S2", "S3", "S4")
        ]
        ids = [row["id"] for row in catalog["briefs"]]
        if ids != expected_ids:
            errors.append("Brief IDs are not exactly 144 unique ordered S1-S4 plans")
        for offset, row in enumerate(catalog["briefs"]):
            number = int(row["package"][-3:])
            if number not in PROFILES:
                raise InvalidRecord("Unknown package in brief catalogue")
            expected_stage = f"S{offset % 4 + 1}"
            expected_package = f"WP-{offset // 4 + 1:03d}"
            if row["stage"] != expected_stage or row["package"] != expected_package:
                errors.append(f"{row['id']}: package/stage order mismatch")
            previous = expected_ids[offset - 1].removeprefix("BRIEF-") if offset else ""
            following = expected_ids[offset + 1].removeprefix("BRIEF-") if offset < 143 else ""
            if (row["predecessor"], row["successor"]) != (previous, following):
                errors.append(f"{row['id']}: predecessor/successor mismatch")
            content = safe_file(row["path"]).read_text(encoding="utf-8")
            if digest(content.encode()) != row["sha256"]:
                errors.append(f"{row['id']}: brief digest mismatch")
            for heading in HEADINGS:
                if f"## {heading}\n" not in content:
                    errors.append(f"{row['id']}: missing heading {heading}")
            if len(content.split()) < 650:
                errors.append(f"{row['id']}: incomplete individual brief")
            if STAGES[row["stage"]][1] not in content:
                errors.append(f"{row['id']}: missing stage boundary")
            for action in PROFILES[number][STAGES[row["stage"]][2]]:
                if action not in content:
                    errors.append(f"{row['id']}: missing package-specific action")
            contract = contract_text(safe_file(row["declaration"]).read_text(encoding="utf-8"))
            if digest(contract.encode()) != row["contract_sha256"]:
                errors.append(f"{row['id']}: source contract changed")
            if field(contract, "Acceptance evidence") not in content:
                errors.append(f"{row['id']}: original acceptance criterion omitted")
            for marker in (
                "DRAFT_NOT_AUTHORIZED", "No command here provisions",
                "S3", "S4", "python3 tools/run_wp_tests.py",
            ):
                if marker not in content:
                    errors.append(f"{row['id']}: missing mandatory boundary {marker}")
        for row in catalog["inputs"] + [catalog["overview"], catalog["masterbook"]]:
            if digest(safe_file(row["path"]).read_bytes()) != row["sha256"]:
                errors.append(f"Input/navigation digest mismatch: {row['path']}")
        # Independent structural checks above remain useful if renderer logic is defective.
        outputs, expected = build(root, catalog["baseline_commit"])
        if expected != catalog:
            errors.append("Catalogue differs from deterministic package-contract rendering")
        for path, expected_content in outputs.items():
            if safe_file(path).read_text(encoding="utf-8") != expected_content:
                errors.append(f"Generated content/navigation drift: {path}")
    except (InvalidRecord, OSError, UnicodeError, ValueError, KeyError, IndexError) as exc:
        errors.append(f"Brief catalogue: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    problems = check()
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        catalog = load_json(ROOT / BASE / "catalog.json")
        words = [len((ROOT / row["path"]).read_text().split()) for row in catalog["briefs"]]
        print(f"SESSION_BRIEFS=PASS packages=36 briefs=144 stages=S1,S2,S3,S4 "
              f"words_min={min(words)} words_max={max(words)} approval=PENDING execution=UNCHANGED")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

