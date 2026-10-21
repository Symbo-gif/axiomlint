"""Internal ratification consistency, not cryptographic principal authentication."""

import hashlib
from pathlib import Path

from axiomlint.schema import InvalidRecord, load_json, validate

ACTIVE = "governance/charter/ACTIVE-BASELINE.json"
APPROVAL = "governance/approvals/APR-001-constitutional-ratification.json"


def checked_file(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise InvalidRecord("Unsafe authority reference")
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise InvalidRecord("Authority reference escapes root")
    for part in (path, *path.parents):
        if part == root.parent:
            break
        if part.is_symlink():
            raise InvalidRecord("Symlink authority reference")
    if not path.is_file():
        raise InvalidRecord(f"Missing authority file: {relative}")
    return path


def check_ratification(root: Path, config: dict) -> list[str]:
    """A boolean approval flag alone can never be a valid active baseline."""
    active_exists = (root / ACTIVE).exists() or (root / ACTIVE).is_symlink()
    if config["approval"] != "APPROVED" and not active_exists:
        return []
    errors: list[str] = []
    try:
        if config["approval"] != "APPROVED":
            raise InvalidRecord("Active authority contradicts project approval state")
        active = load_json(checked_file(root, ACTIVE))
        validate(active, load_json(checked_file(root, "schemas/active-authority.schema.json")))
        record_path = checked_file(root, APPROVAL)
        if hashlib.sha256(record_path.read_bytes()).hexdigest() != active["approval_record_sha256"]:
            raise InvalidRecord("Principal approval record digest mismatch")
        record = load_json(record_path)
        validate(record, load_json(checked_file(root, "schemas/constitutional-ratification.schema.json")))
        grant = load_json(checked_file(root, active["delegation_grant"]))
        validate(grant, load_json(checked_file(root, "schemas/delegated-authority.schema.json")))
        if active["ratified_source_commit"] != record["ratified_source_commit"]:
            raise InvalidRecord("Ratification source revision mismatch")
        if active["targets"] != record["targets"]:
            raise InvalidRecord("Active authority target identities mismatch")
        targets = [{"path": record["packet"], "sha256": record["packet_sha256"]}, *record["targets"]]
        for target in targets:
            content = checked_file(root, target["path"]).read_bytes()
            if hashlib.sha256(content).hexdigest() != target["sha256"]:
                errors.append(f"Ratified document digest mismatch: {target['path']}")
        if config["maintainer"] != record["principal"]:
            errors.append("Principal differs from project maintainer")
        if config["amendment"] != record["targets"][1]["path"]:
            errors.append("Local-only amendment pointer mismatch")
    except (InvalidRecord, OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"Ratification: {exc}")
    return errors
