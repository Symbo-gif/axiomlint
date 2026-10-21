"""Structural and cross-reference checks, not approval or assurance certification."""

import hashlib
import re
from pathlib import Path
from typing import Any

from axiomlint.authority import check_ratification
from axiomlint.schema import InvalidRecord, check_schema, load_json, validate

REGISTERS = (
    "decisions", "deviations", "risks", "assumptions", "findings", "tools", "tcb",
    "corpus", "waivers", "evidence", "exclusions", "releases", "deferred-validations",
)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    schemas: dict[str, Any] = {}

    def fail(message: str) -> None:
        errors.append(message)

    def ref(path: str, owner: str) -> bool:
        if not path or Path(path).is_absolute() or ".." in Path(path).parts:
            fail(f"{owner}: invalid repository reference {path!r}")
            return False
        candidate = root / path
        if not candidate.resolve().is_relative_to(root.resolve()):
            fail(f"{owner}: reference escapes root")
            return False
        if any(p.is_symlink() for p in (candidate, *candidate.parents) if p != root.parent):
            fail(f"{owner}: symlink reference")
            return False
        if not candidate.is_file():
            fail(f"{owner}: missing reference {path}")
            return False
        return True

    try:
        for path in sorted((root / "schemas").glob("*.schema.json")):
            schema = load_json(path)
            check_schema(schema)
            schemas[path.name.removesuffix(".schema.json")] = schema
        if not schemas:
            raise InvalidRecord("No schemas found")
        config = load_json(root / "config/project.json")
        validate(config, schemas["project"])
        ref(config["amendment"], "project amendment")
        plan = root / "docs/reference/axiomlint-plan.md"
        if hashlib.sha256(plan.read_bytes()).hexdigest() != config["source_plan_sha256"]:
            fail("Source plan differs from pinned baseline")
    except (InvalidRecord, KeyError, OSError, TypeError) as exc:
        return [f"Project/schema baseline: {exc}"]

    errors.extend(check_ratification(root, config))

    def records(path: str, schema_name: str) -> list[dict[str, Any]]:
        try:
            rows = load_json(root / path)
            if not isinstance(rows, list):
                raise InvalidRecord("Expected top-level array")
            for row in rows:
                validate(row, schemas[schema_name])
            return rows
        except (InvalidRecord, KeyError, TypeError) as exc:
            fail(f"{path}: {exc}")
            return []

    requirements = records("governance/requirements/requirements.json", "requirement")
    packages = records("governance/work-packages/index.json", "work-package")
    sessions = records("governance/sessions/index.json", "session")
    ledgers = {
        name: records(f"governance/registers/{name}.json", "register-item")
        for name in REGISTERS
    }
    if not requirements or not packages or not sessions:
        fail("Mandatory requirement/package/session register is empty")
    all_rows = requirements + packages + sessions + [
        item for rows in ledgers.values() for item in rows
    ]
    seen: set[str] = set()
    for row in all_rows:
        rid = row["id"]
        if rid in seen:
            fail(f"Duplicate global ID: {rid}")
        seen.add(rid)
    reqs = {row["id"]: row for row in requirements}
    wps = {row["id"]: row for row in packages}
    if sum(row["status"] in ("ACTIVE", "AUDIT_PENDING") for row in packages) > 1:
        fail("More than one active work package")
    for req in requirements:
        if req["package"] not in wps:
            fail(f"{req['id']}: unknown work package")
        for path in req["evidence"]:
            ref(path, req["id"])
    for row in [item for rows in ledgers.values() for item in rows]:
        for rid in row["requirements"]:
            if rid not in reqs:
                fail(f"{row['id']}: unknown requirement {rid}")
        for path in row["evidence"]:
            ref(path, row["id"])
        if row["status"] in ("APPROVED", "VERIFIED"):
            ref(row["approval_ref"], row["id"])
        if row["category"] == "WAIVER" and row["severity"] in ("D1", "D2"):
            fail(f"{row['id']}: D1/D2 waiver prohibited")
    for wp in packages:
        pid = wp["id"]
        ref(wp["declaration"], pid)
        for rid in wp["requirements"]:
            if rid not in reqs:
                fail(f"{pid}: unknown requirement {rid}")
        for dep in wp["dependencies"]:
            if dep not in wps:
                fail(f"{pid}: missing dependency {dep}")
            elif wp["status"] in ("ACTIVE", "AUDIT_PENDING", "CLOSED") and wps[dep]["status"] != "CLOSED":
                fail(f"{pid}: dependency {dep} not closed")
        if wp["approval"] != "PENDING":
            ref(wp["approval_ref"], pid)
        if wp["status"] in ("ACTIVE", "AUDIT_PENDING") and wp["approval"] == "PENDING":
            fail(f"{pid}: active package lacks scope authorization")
        if wp["approval"] == "USER_AUTHORIZED_DRAFTS" and pid != "WP-001":
            fail(f"{pid}: bootstrap authorization is restricted to WP-001")

    # Detect cycles even in planned dependencies, without unbounded recursion.
    pending = {pid: set(wp["dependencies"]) & wps.keys() for pid, wp in wps.items()}
    while pending:
        leaves = {pid for pid, deps in pending.items() if not deps}
        if not leaves:
            fail(f"Dependency cycle: {sorted(pending)}")
            break
        pending = {pid: deps - leaves for pid, deps in pending.items() if pid not in leaves}

    by_package: dict[str, dict[str, dict[str, Any]]] = {}
    for session in sessions:
        pid = session["package"]
        if pid not in wps:
            fail(f"{session['id']}: unknown package")
        stages = by_package.setdefault(pid, {})
        if session["stage"] in stages:
            fail(f"{pid}: duplicate {session['stage']} session")
        stages[session["stage"]] = session
        if session["report"]:
            ref(session["report"], session["id"])
    for pid, wp in wps.items():
        if wp["status"] == "PLANNED" and pid not in by_package:
            continue
        stages = by_package.get(pid, {})
        if set(stages) != {"S1", "S2", "S3", "S4"}:
            fail(f"{pid}: must declare all four sessions")
            continue
        commits: list[str] = []
        for n in range(1, 5):
            session = stages[f"S{n}"]
            if session["status"] in ("IN_PROGRESS", "CLOSED") and any(
                stages[f"S{i}"]["status"] != "CLOSED" for i in range(1, n)
            ):
                fail(f"{pid}: S{n} started before predecessors closed")
            if session["status"] == "CLOSED":
                commit = session["commit"]
                if not re.fullmatch(r"[0-9a-f]{40}", commit):
                    fail(f"{session['id']}: closed session needs commit SHA")
                if commit in commits:
                    fail(f"{pid}: sessions need distinct commits")
                commits.append(commit)
                ref(session["report"], session["id"])
                if n == 2:
                    if not session["independent"]:
                        fail(f"{pid}: S2 not independent")
                    if not session["actor"] or session["actor"] == stages["S1"]["actor"]:
                        fail(f"{pid}: S2 actor not distinct")
                    if not session["context_id"] or session["context_id"] == stages["S1"]["context_id"]:
                        fail(f"{pid}: S2 context not distinct")
                    if session["reviewed_commit"] != stages["S1"]["commit"]:
                        fail(f"{pid}: audit reviewed wrong S1 commit")
        if wp["status"] == "CLOSED":
            if any(s["status"] != "CLOSED" for s in stages.values()):
                fail(f"{pid}: CLOSED before S1-S4 complete")
            if config["approval"] != "APPROVED" or wp["approval"] != "APPROVED":
                fail(f"{pid}: CLOSED without charter/scope approval")
            ref(wp["closure_approval_ref"], f"{pid} closure approval")
            if not wp["acceptance_evidence"]:
                fail(f"{pid}: CLOSED without acceptance evidence")
            for path in wp["acceptance_evidence"]:
                if ref(path, f"{pid} acceptance"):
                    try:
                        manifest = load_json(root / path)
                        validate(manifest, schemas["local-run"])
                        if (
                            manifest["status"] != "PASS" or manifest["dirty"]
                            or manifest["kind"] != "ACCEPTANCE_CANDIDATE"
                            or manifest["commit"] != stages["S4"]["commit"]
                            or manifest["source_tree_sha256"] != manifest["source_tree_after_sha256"]
                        ):
                            fail(f"{pid}: nonacceptance or stale manifest")
                    except (InvalidRecord, KeyError) as exc:
                        fail(f"{pid}: invalid acceptance manifest: {exc}")
            if any(
                r["severity"] in ("D1", "D2") and r["status"] not in ("VERIFIED", "REJECTED")
                for key in ("findings", "deviations") for r in ledgers[key]
            ):
                fail(f"{pid}: blocking finding/deviation unresolved")
    return errors
