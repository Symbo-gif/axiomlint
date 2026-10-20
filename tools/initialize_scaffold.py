"""One-time deterministic materialization of seed records and inert boundaries.

Run only during initial adoption. Refuses to overwrite any output. Subsequent
changes to governed records are manual, reviewed edits, not regeneration.
This is a file-generation tool, not a test or governance acceptance command.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS: dict[str, str] = {}


def add(path: str, value: object) -> None:
    if isinstance(value, str):
        OUTPUTS[path] = value
    else:
        OUTPUTS[path] = json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def obj(properties: dict, required: list | None = None) -> dict:
    return {
        "type": "object", "properties": properties,
        "required": list(properties) if required is None else required,
        "additionalProperties": False,
    }


def string(**extra: object) -> dict:
    return {"type": "string", "minLength": 1, **extra}


def array(items: dict, minimum: int = 0) -> dict:
    return {"type": "array", "items": items, "minItems": minimum}


def enum(*values: str) -> dict:
    return string(enum=list(values))


def schema(name: str, body: dict, version: str = "0.1") -> None:
    add(f"schemas/{name}.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:axiomlint:foundation:{name}:{version}",
        "title": f"AxiomLint foundation {name}", **body,
    })


def main() -> None:
    text = (ROOT / "docs/reference/axiomlint-plan.md").read_text()
    source_digest = hashlib.sha256(text.encode()).hexdigest()
    id_field = string(pattern=r"^[A-Z][A-Z0-9-]*[0-9]$")
    links = array(string())
    approval = enum("PENDING", "USER_AUTHORIZED_DRAFTS", "APPROVED")
    schema("project", obj({
        "schema_version": {"const": "0.1"}, "name": string(), "maintainer": string(),
        "profile": enum("RESEARCH_HIGH_ASSURANCE"),
        "approval": approval, "hosted_ci": {"const": False},
        "subject_execution": {"const": False}, "telemetry": {"const": False},
        "network_during_checks": {"const": False}, "max_active_packages": {"const": 1},
        "local_gate": array(string(), 1), "amendment": string(),
        "baseline_framework_commit": string(pattern=r"^[0-9a-f]{40}$"),
        "source_plan_sha256": string(pattern=r"^[0-9a-f]{64}$"),
    }))
    schema("requirement", obj({
        "id": id_field, "title": string(), "source": string(), "rationale": string(),
        "owner": string(), "package": string(pattern=r"^WP-[0-9]{3}$"),
        "status": enum("DRAFT", "IMPLEMENTED", "VERIFIED", "DEFERRED"),
        "verification": string(), "evidence": links,
    }))
    schema("work-package", obj({
        "id": string(pattern=r"^WP-[0-9]{3}$"), "title": string(),
        "status": enum("PLANNED", "ACTIVE", "AUDIT_PENDING", "CLOSED", "BLOCKED"),
        "owner": string(), "approval": approval,
        "approval_ref": {"type": "string"}, "dependencies": links,
        "requirements": array(string(), 1), "declaration": string(),
        "acceptance_evidence": links, "closure_approval_ref": {"type": "string"},
    }))
    schema("session", obj({
        "id": id_field, "package": string(pattern=r"^WP-[0-9]{3}$"),
        "stage": enum("S1", "S2", "S3", "S4"),
        "status": enum("IN_PROGRESS", "BLOCKED", "PLANNED", "CLOSED"),
        "actor": {"type": "string"}, "context_id": {"type": "string"},
        "independent": {"type": "boolean"}, "commit": {"type": "string"},
        "reviewed_commit": {"type": "string"}, "report": {"type": "string"},
    }))
    schema("register-item", obj({
        "id": id_field, "category": enum(
            "DECISION", "DEVIATION", "RISK", "ASSUMPTION", "FINDING", "TOOL",
            "TCB", "CORPUS", "WAIVER", "EVIDENCE", "EXCLUSION", "RELEASE",
            "DEFERRED_VALIDATION",
        ), "status": enum("OPEN", "PENDING", "DEFERRED", "VERIFIED", "APPROVED", "REJECTED"),
        "severity": enum("D1", "D2", "D3", "D4", "NA"), "owner": string(),
        "summary": string(), "requirements": links, "evidence": links,
        "disposition": string(), "blocking_gate": string(),
        "approval_ref": {"type": "string"},
    }))
    schema("gate-command", obj({
        "name": string(), "argv": array(string(), 1), "exit_code": {"type": "integer"},
        "status": enum("PASS", "FAIL", "TIMEOUT", "ERROR"),
        "wall_seconds": {"type": "number", "minimum": 0},
        "stdout_sha256": string(pattern=r"^[0-9a-f]{64}$"),
        "stderr_sha256": string(pattern=r"^[0-9a-f]{64}$"),
        "stdout_bytes": {"type": "integer", "minimum": 0},
        "stderr_bytes": {"type": "integer", "minimum": 0},
    }))
    command_schema = json.loads(OUTPUTS["schemas/gate-command.schema.json"])
    command_schema = {k: v for k, v in command_schema.items() if not k.startswith("$")}
    schema("local-run", obj({
        "schema_version": {"const": "0.2"}, "run_id": string(),
        "source_identity_algorithm": {"const": "sha256-path-bytes-gitmode-v1"},
        "manifest_schema_sha256": string(pattern=r"^[0-9a-f]{64}$"),
        "kind": enum("DEVELOPMENT", "ACCEPTANCE_CANDIDATE"),
        "status": enum("PASS", "FAIL"), "commit": {"type": "string"},
        "dirty": {"type": "boolean"}, "source_tree_sha256": string(pattern=r"^[0-9a-f]{64}$"),
        "source_tree_after_sha256": string(pattern=r"^[0-9a-f]{64}$"),
        "python": string(), "platform": string(), "machine": string(),
        "environment_policy": {"const": "ALLOWLIST_NO_CREDENTIALS"},
        "started_utc": string(), "commands": array(command_schema, 4),
        "limitations": array(string(), 1),
    }), version="0.2")
    add("config/project.json", {
        "schema_version": "0.1", "name": "AxiomLint", "maintainer": "Michael Maillet",
        "profile": "RESEARCH_HIGH_ASSURANCE", "approval": "PENDING",
        "hosted_ci": False, "subject_execution": False, "telemetry": False,
        "network_during_checks": False, "max_active_packages": 1,
        "local_gate": ["python3", "tools/local_check.py", "--require-clean"],
        "amendment": "governance/charter/AMD-001-local-only.md",
        "baseline_framework_commit": "d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a",
        "source_plan_sha256": source_digest,
    })
    reqs = [
        ("REQ-GOV-001", "S1-S4 order and independent audit", "WP-001",
         "Plan: Governing profile, Work-package rules, Audit independence",
         "No self-review or fabricated closure", "IMPLEMENTED",
         "Schema/semantic mutation tests plus later independent audit",
         ["src/axiomlint/governance.py", "tests/test_governance.py"]),
        ("REQ-GOV-002", "Only one active package with declared dependencies", "WP-001",
         "Plan: Work-package rules", "Prevent undeclared parallel advancement",
         "IMPLEMENTED", "Dependency and active-count mutation tests",
         ["src/axiomlint/governance.py", "tests/test_governance.py"]),
        ("REQ-GOV-003", "Human approvals remain explicit and pending", "WP-001",
         "Plan: Authority hierarchy", "An agent cannot self-ratify governance",
         "IMPLEMENTED", "Premature-closure negative tests and maintainer review",
         ["governance/charter/CHARTER.md", "tests/test_governance.py"]),
        ("REQ-LOCAL-001", "No hosted checks or network during foundation tests", "WP-004",
         "User instruction 2026-10-20", "Respect authorized local-only scope",
         "IMPLEMENTED", "Policy/hygiene checks; inspect actual local commands",
         ["tools/hygiene_check.py", "tests/test_gate.py"]),
        ("REQ-EVID-001", "Schema subset rejects malformed and unsupported records", "WP-005",
         "Plan: WP-005", "Prevent permissive false-validity",
         "IMPLEMENTED", "Positive, negative, duplicate and unsupported-keyword fixtures",
         ["src/axiomlint/schema.py", "tests/test_schema.py"]),
        ("REQ-EVID-002", "Content-addressed evidence rejects corruption and unsafe paths", "WP-005",
         "Plan: WP-005", "Tie evidence bytes to stable content identity",
         "IMPLEMENTED", "Digest, corruption, missing, symlink and idempotence tests",
         ["src/axiomlint/evidence/store.py", "tests/test_store.py"]),
        ("REQ-EVID-003", "Bind local logs to exact commit and source tree", "WP-004",
         "Plan: Required record fields; AMD-001", "Prevent stale or dirty acceptance",
         "IMPLEMENTED", "Fingerprint/dirty-state tests and actual local-run manifest",
         ["tools/local_check.py", "tests/test_gate.py"]),
        ("REQ-SAFE-001", "Subject execution disabled without audited sandbox", "WP-006",
         "Plan: WP-006 and hostile-code policy", "Avoid executing hostile input on host",
         "IMPLEMENTED", "Runner refuses all calls; capability tests",
         ["src/axiomlint/runner/__init__.py", "tests/test_intake_cli.py"]),
        ("REQ-INTAKE-001", "Inventory never imports or runs source", "WP-007",
         "Plan: WP-007; bootstrap scope", "Nonexecuting maintainer-controlled metadata only",
         "IMPLEMENTED", "Malicious top-level side-effect fixture remains unexecuted",
         ["src/axiomlint/intake/static.py", "tests/test_intake_cli.py"]),
        ("REQ-CLAIM-001", "Unavailable checks never imply NO_FINDING or proof", "WP-009",
         "Plan: Product claims and soundness discipline", "Preserve epistemic boundaries",
         "IMPLEMENTED", "CLI status/inventory tests; future per-adapter conformance",
         ["src/axiomlint/cli.py", "tests/test_intake_cli.py"]),
        ("REQ-SEM-001", "Formal claims require declared semantics and correspondence", "WP-010",
         "Plan: Semantic correspondence", "A model theorem is not a source theorem",
         "DRAFT", "Later translator conformance and independent correspondence review",
         ["docs/supported-semantics/PyRS-0.md"]),
        ("REQ-PRIV-001", "No telemetry, environment snapshots or remote model calls", "WP-003",
         "Plan: Privacy and licensing", "Prevent unintended source/credential disclosure",
         "IMPLEMENTED", "Allowlisted child environment and disabled-capability tests",
         ["governance/standards/security-and-privacy.md", "tests/test_gate.py"]),
        ("REQ-BENCH-001", "Freeze experimental protocol before outcome access", "WP-026",
         "Plan: Benchmark protocol and E0-E6", "Avoid leakage and post-hoc thresholds",
         "DRAFT", "Later independent preregistration and frozen protocol digest",
         ["governance/standards/methodology.md", "governance/templates/preregistration.md"]),
        ("REQ-LIC-001", "FOSS-only mandatory core with per-artifact license review", "WP-001",
         "Plan: Free/open-source stack and exclusions", "Avoid mandatory restricted engines/rules",
         "DRAFT", "License/tool inventory review before each adoption",
         ["LICENSE", "governance/standards/security-and-privacy.md"]),
        ("REQ-ENV-001", "Pinned reproducible Linux and supported-platform environments", "WP-004",
         "Plan: WP-004", "A stdlib smoke run is not a locked environment",
         "DEFERRED", "Later local locks, Nix/OCI and fresh-checkout reproduction",
         ["environments/README.md"]),
        ("REQ-RELEASE-001", "No release before independent audit and complete acceptance", "WP-036",
         "Plan: G8 and WP-036", "Prevent release readiness by assertion",
         "DRAFT", "Release checklist, signed artifacts and independent approval",
         ["governance/templates/release-checklist.md"]),
    ]
    requirements = []
    for rid, title, package, source, rationale, status, verification, evidence in reqs:
        requirements.append({
            "id": rid, "title": title, "package": package, "source": source,
            "rationale": rationale, "owner": "Michael Maillet", "status": status,
            "verification": verification, "evidence": evidence,
        })
    add("governance/requirements/requirements.json", requirements)
    packages = []
    matches = list(re.finditer(r"^### (WP-\d{3}) [—–-] (.+)$", text, re.M))
    if len(matches) != 36:
        raise RuntimeError(f"Expected 36 packages in source plan, got {len(matches)}")
    for i, match in enumerate(matches):
        pid, title = match.group(1, 2)
        stop = matches[i + 1].start() if i + 1 < len(matches) else text.index("\n## Phase gates")
        original = text[match.end():stop].split("\n## Phase ")[0].strip()
        declaration = f"governance/work-packages/{pid}.md"
        associated = [x["id"] for x in requirements if x["package"] == pid] or ["REQ-GOV-001"]
        packages.append({
            "id": pid, "title": title, "status": "ACTIVE" if i == 0 else "PLANNED",
            "owner": "Michael Maillet",
            "approval": "USER_AUTHORIZED_DRAFTS" if i == 0 else "PENDING",
            "approval_ref": "governance/decisions/authorization.md" if i == 0 else "",
            "dependencies": [] if i == 0 else [f"WP-{i:03d}"],
            "requirements": associated, "declaration": declaration,
            "acceptance_evidence": [], "closure_approval_ref": "",
        })
        add(declaration, f"""# {pid}: {title}

Status: {"ACTIVE, S1 draft preparation" if i == 0 else "PLANNED, NOT AUTHORIZED"}.
Owner and approver: Michael Maillet. Formal scope approval: PENDING.
Dependencies: {", ".join(packages[-1]["dependencies"]) or "none"}.
Governing requirements: {", ".join(associated)}.

## Original plan scope and acceptance

{original}

## Project-specific declaration and tailoring

The source section above remains the full acceptance baseline. Hosted/pushed-CI
clauses are subject to proposed AMD-001, never silently treated as completed.
All listed artifacts are provisional until independent verification and approval.
{"Current user authorization permits charter drafting and inert development scaffolding, not closure of later packages. DEV-001 records that pre-ratification boundary." if i == 0 else "Before activation, expand this draft into an approved file-level scope, risk assessment, tests and evidence plan. No work execution is authorized by this draft."}

## Test/evidence plan and documentation impact

Use applicable local checks, explicit positive/negative fixtures, schema validation,
raw logs and source digests; add package-specific tests before implementation.
Independent S2 checks actual acceptance criteria, not S1 summaries.
Update affected docs, requirements, risk/finding registers and changelog in S4.
Exact acceptance artifact references: PENDING. Risk decisions: PENDING.

## Session outputs and rollback

S1: implementation, tests, raw local logs, handoff and distinct commit.
S2: independent read-only audit report and distinct commit.
S3: finding-only fixes or no-change verification, independent delta review and
distinct commit. S4: docs, registers, local acceptance, approval and distinct commit.
No session is implicitly complete. Preserve evidence when rolling back the
capability or restoring a prior baseline; accepted records use errata.
""")
    add("governance/work-packages/index.json", packages)
    sessions = []
    for n in range(1, 5):
        sessions.append({
            "id": f"SESSION-WP-001-S{n}", "package": "WP-001", "stage": f"S{n}",
            "status": "IN_PROGRESS" if n == 1 else "BLOCKED",
            "actor": "Computer authoring context" if n == 1 else "",
            "context_id": "72131cdc-563c-4d43-a6b3-f37dd1253e0c" if n == 1 else "",
            "independent": False, "commit": "", "reviewed_commit": "",
            "report": "governance/sessions/WP-001-S1.md" if n == 1 else "",
        })
    add("governance/sessions/index.json", sessions)
    def row(rid: str, category: str, summary: str, status: str = "PENDING",
            severity: str = "NA", gate: str = "G0", evidence: list | None = None,
            disposition: str = "Await maintainer decision or later package evidence") -> dict:
        return {
            "id": rid, "category": category, "status": status, "severity": severity,
            "owner": "Michael Maillet", "summary": summary, "requirements": [],
            "evidence": evidence or [], "disposition": disposition,
            "blocking_gate": gate, "approval_ref": "",
        }
    registers = {
        "decisions": [
            row("DEC-001", "DECISION", "Use AxiomLint from current attached plan as provisional name"),
            row("DEC-002", "DECISION", "Proposed authoritative local-only acceptance",
                evidence=["governance/charter/AMD-001-local-only.md"]),
            row("DEC-003", "DECISION", "Keep zero-dependency foundation and disabled subject execution"),
        ],
        "deviations": [
            row("DEV-001", "DEVIATION",
                "Scaffolding and charter drafts before formal baseline ratification",
                "OPEN", "D2", evidence=["governance/decisions/authorization.md"]),
            row("DEV-002", "DEVIATION",
                "Local-only override conflicts with upstream mandatory-CI tailoring wording",
                "OPEN", "D2", evidence=["governance/charter/AMD-001-local-only.md"]),
        ],
        "risks": [
            row("RISK-001", "RISK", "Same-user local host can rewrite evidence and manifests", "OPEN", "D2"),
            row("RISK-002", "RISK", "AST parser resource exhaustion on hostile inputs", "OPEN", "D2", "G1"),
            row("RISK-003", "RISK", "Unreviewed source-model translation may overstate assurance", "OPEN", "D2", "G4"),
            row("RISK-004", "RISK", "Private holdout leakage or invalid benchmark labels", "OPEN", "D2", "G6"),
            row("RISK-005", "RISK", "Core license and name not independently cleared", "OPEN", "D3", "G8"),
        ],
        "assumptions": [
            row("ASM-001", "ASSUMPTION", "Laptop user and store parent trusted; no hostile concurrent writes"),
            row("ASM-002", "ASSUMPTION", "Repository tests are maintainer-controlled, not untrusted review subjects"),
            row("ASM-003", "ASSUMPTION", "Python >=3.12 and Git available; package installation not needed"),
        ],
        "findings": [],
        "tools": [
            row("TOOL-001", "TOOL", "Python standard library; exact runtime recorded per local run"),
            row("TOOL-002", "TOOL", "Git source identity; exact executable version recorded in handoff"),
        ],
        "tcb": [
            row("TCB-001", "TCB", "Host kernel, filesystem, Python runtime and Git"),
            row("TCB-002", "TCB", "Schema/governance validator, local gate and source fingerprint code"),
            row("TCB-003", "TCB", "Evidence store and SHA-256 implementation"),
        ],
        "corpus": [], "waivers": [], "evidence": [], "exclusions": [], "releases": [],
    }
    deferred = [
        ("Full Draft 2020-12 engine and runtime schemas", "WP-005", "G1"),
        ("Official locally pinned SARIF schema and reporter", "WP-009", "G2"),
        ("Ruff/mypy/pytest/coverage with locked tools", "WP-004", "G1"),
        ("Nix flake/lock and rootless OCI pinned image", "WP-004", "G1"),
        ("Fresh clean-checkout local reproduction", "WP-004", "G1"),
        ("Windows supported-platform verification", "WP-004", "G1"),
        ("Sandbox enforcement, escape and resource-limit probes", "WP-006", "G1"),
        ("Solver/CAS/Lean runtime and conformance", "WP-013 through WP-022", "G4"),
        ("SCA/SBOM/secret scans, provenance and signatures", "WP-034", "G8"),
        ("Package build/install and locked build backend", "WP-004", "G1"),
        ("Independent S2 audit and maintainer ratification", "WP-001", "G0"),
    ]
    registers["deferred-validations"] = [
        row(f"DEFER-{i:03d}", "DEFERRED_VALIDATION", f"{title}; owner package {wp}",
            "DEFERRED", "D2", gate)
        for i, (title, wp, gate) in enumerate(deferred, 1)
    ]
    for name, records in registers.items():
        add(f"governance/registers/{name}.json", records)
    add("governance/evidence/baseline.json", {
        "source_plan_sha256": source_digest,
        "framework_url": "https://github.com/Symbo-gif/Methodology-Workflow-Governance",
        "framework_commit": "d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a",
        "adoption": "PROJECT_ADAPTATION_NOT_UNMODIFIED_VENDOR",
        "framework_license": "MIT; copyright 2026 Michael Maillet",
    })
    boundaries = {
        "src/axiomlint/specir": "Typed contracts, explicit domains and correspondence; WP-010.",
        "src/axiomlint/fusion": "Preserve disagreement/provenance; no aggregate confidence yet; WP-009.",
        "src/axiomlint/reporting": "Native JSON/Markdown/SARIF; official schema pin required; WP-009.",
        "lean/AxiomLint": "Formal model sources; pinned Lean/Lake required; WP-019.",
        "lean/Generated": "Generated models; no generation or claims enabled; WP-020.",
        "lean/Proofs": "Proof jobs and independent kernel replay; WP-021.",
        "rules/bandit": "Reviewed FOSS-safe rules; no remote ruleset download; WP-008.",
        "rules/semgrep": "Self-authored or OSI-licensed rules only; WP-008.",
        "benchmarks/corpus-manifest": "Licensed origins, hashes, hidden labels and leakage controls; WP-026.",
        "benchmarks/public": "Public task inputs only; no accepted tasks yet; WP-027.",
        "benchmarks/harness": "Matched budgets, randomized order, raw capture; disabled; WP-028.",
        "benchmarks/scorer": "Independent labels and blinded adjudication; not product logic; WP-028.",
        "benchmarks/analysis": "Preregistered metrics and uncertainty; disabled; WP-029.",
        "tests/unit": "Core foundation tests currently live in tests/test_*.py.",
        "tests/integration": "Future adapter and evidence integration.",
        "tests/conformance": "Future semantic and backend conformance.",
        "tests/adversarial": "Future contained abuse tests; no naked-host hostile execution.",
        "tests/golden": "Future deterministic native/SARIF/Markdown fixtures.",
        "tests/e2e": "Future bounded vertical slice; not yet operational.",
    }
    for backend in ("hypothesis", "crosshair", "z3", "cvc5", "sympy", "sage", "lean", "llm"):
        boundaries[f"src/axiomlint/backends/{backend}"] = (
            f"{backend} adapter unavailable. No execution, implicit success or assurance claim."
        )
    add("src/axiomlint/backends/__init__.py",
        '"""Future verifier boundaries; every backend is unavailable."""\n')
    for path, description in boundaries.items():
        add(f"{path}/README.md", f"# {path.split('/')[-1]} boundary\n\n{description}\n\nStatus: SCAFFOLD ONLY. No execution or acceptance implied.\n")
    existing = [path for path in OUTPUTS if (ROOT / path).exists()]
    if existing:
        raise RuntimeError(f"Refusing to overwrite existing outputs: {existing}")
    for path, content in OUTPUTS.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    print(f"Materialized {len(OUTPUTS)} new seed files; no approvals or closures granted.")


if __name__ == "__main__":
    main()
