"""Deterministically render proposed briefs; never create live session records."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from session_brief_profiles import PROFILES

ROOT = Path(__file__).resolve().parents[1]
BASE = "governance/session-briefs"
BOOK = "docs/planning/axiomlint-session-briefs-masterbook.md"
LINK_MARKER = "<!-- BEGIN GENERATED SESSION BRIEF LINKS -->"
STAGES = {
    "S1": ("Implementation", "IMPLEMENT_WITH_TESTS", "implement",
           "Approved implementer; does not self-approve entry, audit or closure"),
    "S2": ("Independent audit", "READ_ONLY_PRODUCT", "audit",
           "Independent human or genuinely separate agent context; not the S1 author context"),
    "S3": ("Finding-only remediation", "FINDINGS_ONLY", "remediate",
           "Authorized remediator plus separate independent delta reviewer"),
    "S4": ("Documentation and closure", "HUMAN_APPROVAL_REQUIRED", "close",
           "Documentation/closure owner; Michael is the actual human approver"),
}
SOURCES = {
    "GOV": ("Pinned four-session cycle", "https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/work-package-session-cycle.md"),
    "TEMPLATE": ("Pinned session-brief template", "https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/templates/session-brief.md"),
    "EXP": ("Pinned experimental cycle", "https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/experiment-cycle.md"),
    "BENCH": ("Pinned benchmark and reproducibility standard", "https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/standards/benchmarking-and-reproducibility.md"),
    "SSDF": ("NIST SSDF", "https://csrc.nist.gov/projects/ssdf"),
    "SARIF": ("OASIS SARIF 2.1.0", "https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html"),
    "SLSA": ("Versioned SLSA security levels", "https://slsa.dev/spec/v1.1/levels"),
    "PODMAN": ("Podman runtime reference", "https://docs.podman.io/en/latest/markdown/podman-run.1.html"),
    "HYPOTHESIS": ("Hypothesis replay API", "https://hypothesis.readthedocs.io/en/latest/reference/api.html"),
    "CROSSHAIR": ("CrossHair contracts", "https://crosshair.readthedocs.io/en/latest/contracts.html"),
    "Z3": ("Z3 Python guide", "https://microsoft.github.io/z3guide/programming/Z3%20Python%20-%20Readonly/Introduction/"),
    "SYMPY": ("SymPy assumptions", "https://docs.sympy.org/latest/guides/assumptions.html"),
    "LEAN": ("Lean axiom reference", "https://lean-lang.org/doc/reference/latest/Axioms/"),
}
INPUTS = (
    "tools/session_brief_profiles.py", "tools/render_session_briefs.py",
    "governance/session-briefs/PROTOCOL.md", "docs/research/session-brief-design.md",
    "schemas/session-brief-catalog.schema.json",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    # Production generation uses the foundation's duplicate-key-rejecting loader.
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from axiomlint.schema import load_json
    return load_json(path)


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def relative(target: str, source: str) -> str:
    return os.path.relpath(target, Path(source).parent).replace(os.sep, "/")


def contract_text(content: str) -> str:
    match = re.search(
        r"## Original plan scope and acceptance\n+(.*?)(?=\n## Project-specific declaration)",
        content, re.S,
    )
    if not match:
        raise ValueError("Cannot identify original package contract")
    return match.group(1).strip()


def field(contract: str, name: str) -> str:
    match = re.search(rf"\*\*{re.escape(name)}:\*\*\s*(.+)", contract)
    if not match:
        raise ValueError(f"Missing original contract field {name}")
    return match.group(1).strip()


def validate_profiles() -> None:
    if set(PROFILES) != set(range(1, 37)):
        raise ValueError("Profiles must cover exactly WP-001 through WP-036")
    for number, profile in PROFILES.items():
        required = {"scope", "implement", "audit", "remediate", "close",
                    "outputs", "checks", "risks", "sources"}
        if not required <= profile.keys():
            raise ValueError(f"WP-{number:03d}: incomplete specific profile")
        for key in required:
            values = profile[key]
            if not isinstance(values, list) or not values or any(
                not isinstance(x, str) or not x.strip() for x in values
            ):
                raise ValueError(f"WP-{number:03d}: invalid {key}")
        if min(len(profile[k]) for k in ("implement", "audit", "checks")) < 4:
            raise ValueError(f"WP-{number:03d}: insufficient specific actions/tests")
        if min(len(profile[k]) for k in ("remediate", "close")) < 3:
            raise ValueError(f"WP-{number:03d}: incomplete S3/S4 planning")
        if set(profile["sources"]) - SOURCES.keys():
            raise ValueError(f"WP-{number:03d}: unknown reference")


def session_path(number: int, stage: str) -> str:
    return f"{BASE}/WP-{number:03d}/{stage}.md"


def neighbours(number: int, stage: str) -> tuple[str, str]:
    offset = (number - 1) * 4 + int(stage[-1]) - 1
    def sid(value: int) -> str:
        return f"WP-{value // 4 + 1:03d}-S{value % 4 + 1}"
    return sid(offset - 1) if offset else "", sid(offset + 1) if offset < 143 else ""


def stage_entry(stage: str) -> list[str]:
    common = [
        "Read the actual declaration, requirements, current state, open findings/deferrals and approval records before the diff or implementation summary.",
        "Record the entry branch/head, exact source fingerprint, clean/intentionally dirty state, owner/context and baseline tool/material availability; placeholders must be resolved before work.",
        "Confirm no hosted test, push, installation, remote fallback, credential access or publication is implicitly authorized.",
    ]
    specific = {
        "S1": [
            "Require an actually approved file-level declaration and closed dependencies or explicit approved waiver; WP-001's historical bootstrap exception must be separately resolved.",
            "Reproduce the pre-change baseline and agree package acceptance/test inventory before implementation; drafting this brief is not approved S1 entry.",
        ],
        "S2": [
            "Require a committed S1 handoff, provisional acceptance evidence and exact reviewed S1 head.",
            "Use a genuinely independent reviewer/context that reads source directly. Keep product source, schemas, tests and governing contract read-only; logs/audit artifacts use separate writable locations.",
        ],
        "S3": [
            "Require the committed independent S2 report and a complete ordered finding set, including an explicitly empty set when appropriate.",
            "Lock change scope to actual finding IDs and approved dispositions; no features, refactors or hypothetical fixes merely because they appear below.",
        ],
        "S4": [
            "Require completed S3 closure table, clean independent delta audit and all mandatory package-specific checks/evidence.",
            "Require actual charter/AMD-001 and scope approvals before authoritative closure; unresolved D1/D2 or missing criteria block entry.",
        ],
    }
    return common + specific[stage]


def stage_actions(stage: str, profile: dict) -> list[str]:
    actions = list(profile[STAGES[stage][2]])
    tails = {
        "S1": [
            "Implement in small coherent increments with executable positive, negative and inconclusive-path tests; keep raw failed attempts and reference-availability disposition.",
            "Run the package-specific nonempty suite and full local gate; pin implementation and handoff in an S1-specific commit without claiming independent S2.",
        ],
        "S2": [
            "Inventory actual changed files and compare scope, architecture, correctness, test validity, security, privacy, documentation, hygiene, evidence and prior obligations.",
            "Record each actual finding's unique ID, D1-D4, clause, exact location, failure mode, impact, reproduction/reasoning and expected remedy.",
            "Commit only audit artifacts with PASS, PASS-WITH-FINDINGS or FAIL. Any D1 forces FAIL; do not repair product source or self-ratify acceptance.",
        ],
        "S3": [
            "Treat the package-specific remediation cases above as conditional categories, not invented findings. First reproduce the actual S2 issue and prove the regression fails pre-fix for the intended reason.",
            "Fix D1-D4 in order; link every change/test to its finding. Amendment/decline/carry decisions need actual authorized independent evidence; D1/D2 cannot be carried.",
            "Repeat targeted checks, full local gate and independent delta re-audit within S3 until clean. If no findings exist, commit an independently verified no-change closure table.",
        ],
        "S4": [
            "Update directory/API/user docs, examples/migrations where affected, changelog, requirements, risks, decisions, evidence and session/package state records.",
            "Commit a candidate, run clean exact-revision local acceptance and verify raw evidence. Do not put a commit's own unknown hash inside itself or reuse older logs for a newer head.",
            "Obtain real maintainer approval; verify any later closure-record commit separately and preserve externally bound final attestations as required by PROTOCOL.md.",
        ],
    }
    return actions + tails[stage]


def stage_artifacts(pid: str, stage: str, profile: dict) -> list[str]:
    common = [
        f"`governance/execution/{pid}/{stage}/record.json`: actual owner/context, entry/reviewed/exit revisions, dirty/source identities, decisions and evidence links; create only at authorized activation.",
        f"`governance/execution/{pid}/{stage}/handoff.md`: changed/examined files, criteria, command outcomes, limitations, outstanding obligations and next-stage decision.",
        "Raw local stdout/stderr, command inventory, pinned environment/tool/schema identities, artifact sizes/digests and failed/inconclusive outcomes; redact secrets without destroying restricted originals.",
    ]
    if stage == "S1":
        common += [f"Proposed product deliverable: `{path}`." for path in profile["outputs"]]
        common += [f"`tests/test_wp_{pid[-3:]}_*.py`: approved package-specific executable acceptance coverage, not empty placeholder tests."]
    elif stage == "S2":
        common += [
            f"`governance/audits/{pid}/S2-report.md`: independent identity, exact reviewed head, scope, reproduced evidence, limitations and verdict.",
            f"`governance/audits/{pid}/S2-findings.json`: actual findings or an explicit empty set; never generated allegations.",
            "Product files listed in scope/deliverables are audit inputs, not permission for the reviewer to edit them.",
        ]
    elif stage == "S3":
        common += [
            f"`governance/findings/{pid}/closure-table.md`: every finding, disposition, fix/amendment/rejection/carry authority, regression and independent verification.",
            f"`governance/audits/{pid}/S3-delta-review.md`: separate reviewer/context and exact remediated head per round, including no-change verification when empty.",
        ]
    else:
        common += [
            f"`governance/closures/{pid}.md`: original criteria-to-evidence, four distinct session commits, audit/delta verdicts, findings and real approval references.",
            f"`governance/state-reports/{pid}-S4.md`: exact accepted candidate/closure identities, residual limits, rollback and next declared package.",
            "Final local run manifest/schema/raw logs and independently checked approval binding; no fabricated CLOSED state, signature or external acceptance.",
        ]
    return common


def stage_exit(stage: str) -> list[str]:
    return {
        "S1": [
            "Approved scope implemented and original acceptance provisionally demonstrated by nonempty targeted tests plus full local gates.",
            "Source/material identities, raw artifacts, outstanding limits and truthful handoff are preserved; implementation pinned by its own S1 commit.",
            "No claim of independent audit, package closure or earned evidence tier follows automatically.",
        ],
        "S2": [
            "Independent report and complete finding set committed with a real verdict and exact reviewed S1 head.",
            "Source read-only discipline, reproduction scope and unavailable checks documented; no hidden product fixes.",
            "S3 receives prioritized actual findings, including explicit no-findings/no-change requirement; a PASS is not S4 closure.",
        ],
        "S3": [
            "Every finding independently verified fixed, explicitly approved amended/declined, or validly carried under policy; no unresolved D1/D2.",
            "Regression and complete local evidence exist, independent delta review is clean, and closure table has its own S3 commit.",
            "Even an empty finding set has independent no-change verification; S4 cannot be skipped.",
        ],
        "S4": [
            "All original acceptance criteria and mandatory package checks have exact evidence; docs/traceability/registers are complete.",
            "Four distinct session records/summary commits and independent S2/S3-delta evidence exist; actual human approvals bind the exact final acceptance scope.",
            "Only then mark the live package CLOSED and propose/activate its approved successor. Missing acceptance, ratification, risk or platform evidence means BLOCKED, not conditional success.",
        ],
    }[stage]


def render_brief(wp: dict, stage: str, contract: str, baseline: str) -> str:
    pid = wp["id"]
    number = int(pid[-3:])
    profile = PROFILES[number]
    title, boundary, _, role = STAGES[stage]
    path = session_path(number, stage)
    previous, following = neighbours(number, stage)
    navigation = []
    for label, sid in (("Previous planned session", previous), ("Next planned session", following)):
        if sid:
            target = session_path(int(sid[3:6]), sid[-2:])
            navigation.append(f"{label}: [{sid}]({relative(target, path)}).")
        else:
            navigation.append(f"{label}: none.")
    acceptance = field(contract, "Acceptance evidence")
    objective = field(contract, "Objective")
    rollback = field(contract, "Rollback")
    source_links = " ".join(f"[{SOURCES[key][0]}]({SOURCES[key][1]})" for key in profile["sources"])
    if profile.get("experiment"):
        experiment = f"""
## Experimental checkpoints

{pid} is an experimental work package. Apply EXP-E0 authorization and frozen
EXP-E1 plus genuinely independent EXP-E2 before any EXP-E3 measurement in S1.
Registered analysis follows verified raw manifests; S2 is a later independent
audit and cannot retroactively supply EXP-E2. S3 never moves thresholds, seeds,
denominators or exclusions and cannot retry unfavorable outcomes away. New
measurements affected by a design defect need a separately approved correction
cycle. S4 records real EXP-E5 acceptance and appropriately scoped EXP-E6 synthesis.
Keep null, negative, unknown, timeout and inconclusive outcomes permanently.
"""
    else:
        experiment = """
## Scientific boundary

Engineering fixtures and this session plan are not comparative benchmark results.
No campaign, outcome inspection or effectiveness claim is authorized here.
If proposed work becomes a measurement campaign, stop and obtain EXP-E0/E1/E2
before its data exists; never relabel post-result choices as preregistered.
"""
    extra = ""
    if number == 1:
        extra = "\nWP-001 S1 already exists: supplement remaining adoption work and preserve its original commits/records. Do not reset history or infer approval from this new brief.\n"
    if number == 25:
        extra += "\nCalibration entry decision: approve a separately licensed, independently labeled calibration corpus disjoint from future holdouts, or approve a scope/order/split amendment. The uncalibrated fallback alone cannot satisfy calibrated G5.\n"
    criteria = "\n".join(f"- `{pid}-AC-{i:02d}`: {item}" for i, item in enumerate(profile["checks"], 1))
    return f"""# {pid} {stage}: {title}

Work package: {wp["title"]}. Brief ID: `BRIEF-{pid}-{stage}`.
Brief status: `DRAFT_NOT_AUTHORIZED`; actual execution status is maintained
separately and is not changed by this file. Entry revision, owner/context,
approval evidence and reviewed head must be filled from reality at activation.
Role: {role}. Activity boundary: `{boundary}`.

Planning baseline: `{baseline}`. Package declaration:
`{wp["declaration"]}`. Governing seed requirements: {", ".join(wp["requirements"])}.
Dependency closures: {", ".join(wp["dependencies"]) or "none; bootstrap authority still requires resolution"}.
{" ".join(navigation)}

## Authority read

Read `governance/charter/CHARTER.md`, `governance/charter/AMD-001-local-only.md`,
`governance/STATE.md`, this package declaration, its requirement sources and
`governance/standards/methodology.md`, evidence/security/testing standards.
Then read `governance/session-briefs/PROTOCOL.md` and
`docs/research/session-brief-design.md`. Authority conflicts stop affected work.
The live `governance/sessions/index.json` is not replaced by the draft catalogue.
{extra}
## Entry gates

{bullets(stage_entry(stage))}

## Scope and non-goals

Objective: {objective}
Stage scope: {title}; operate only within its activity boundary.
Proposed file/subsystem scope: {", ".join(f"`{p}`" for p in profile["scope"])}.
These are planned locations, not claims those files/capabilities already exist.

No unrelated feature work, new language/repository-scale analysis, automatic
patching/repair, invented approvals, cross-stage shortcuts, hosted checks,
pushes or publication. S2 does not modify product code; S3 does not implement
unreported improvements; S4 does not hide a product fix in documentation.

## Required actions

{bullets(stage_actions(stage, profile))}

## Required artefacts

{bullets(stage_artifacts(pid, stage, profile))}

## Acceptance and verification matrix

Original declaration acceptance retained verbatim as source baseline:

> {acceptance}

Any hosted/pushed-CI phrase in that historical clause is not an executable
instruction: the user's local-only constraint prevails, and AMD-001 ratification
is required for authoritative local closure. Do not erase the original criterion
or claim it passed; record its approved local replacement.

Package-specific proposed acceptance obligations:

{criteria}

All stage work checks these obligations from its own role: S1 constructs
evidence, S2 independently challenges it, S3 resolves actual defects and S4
traces accepted evidence to every clause. Structural validity is not authority.

## Verification commands

Run on the user's laptop, from the repository root, with approved local materials:

```sh
python3 tools/check_session_briefs.py
python3 tools/run_wp_tests.py {pid}
python3 tools/local_check.py
```

The targeted command intentionally fails on missing/empty/all-skipped coverage.
S1 must create `tests/test_wp_{number:03d}_*.py` before claiming targeted acceptance;
do not run all 36 future suites now or count an absent tool as a clean scan.
Before work, declare additional package-specific invocation/replay commands,
versions and test fixtures implementing the matrix; baseline checks alone do
not exercise future solvers, proofs, sandbox enforcement or statistical validity.

After the relevant candidate is committed and ratification permits acceptance:

```sh
python3 tools/local_check.py --require-clean
python3 tools/verify_local_run.py artifacts/gates/RUN-ID --check-current-source
```

Use the printed real run ID. S2 verifies the reviewed S1 head; S3 verifies its
remediated head; S4 verifies its exact candidate and any later closure-record
head separately. Capture unsuccessful commands too. No command here provisions
tools, downloads data, starts a remote model, pushes or configures hosted CI.

{experiment.strip()}

## Stop/block conditions

{bullets(["Actual approval/dependency/independence missing; governing contracts conflict; source identity changes unexpectedly; mandatory checks are empty, unavailable or deferred.",
          "Any D1, unresolved D2, evidence corruption, privacy breach, invalid oracle, unsupported semantics or attempted unsupported assurance promotion.",
          "Execution without accepted containment, undeclared network/provisioning, hidden holdout access, or a request to retry until a favorable outcome.",
          *profile["risks"]])}

## Exit gates

{bullets(stage_exit(stage))}

## Rollback and retention

Original package rollback: {rollback}
Disable/quarantine affected capability or restore the prior source baseline,
but retain raw observations, failed attempts, findings and historical approvals.
Accepted records are superseded through new records/errata, not rewritten.
For {stage}, rollback never authorizes a different stage's work or automatic
downstream activation.

## Handoff

Provide actual entry/reviewed/exit commits, distinct session-summary commit,
files changed/examined, original-clause/AC evidence map, exact commands and raw
digests, verdict/dispositions, residual risks and unavailable checks. Name the
next owner and independence requirement without inventing their identity or
approval. Successor: `{following or "none; separate campaign or release action requires authorization"}`.
The recipient must read the governing source, not accept this summary as authority.

## Technical reference reading

{source_links}

These references inform proposed review tasks; pin actual executable versions
at authorized activation. No reference grants approval or reports a completed run.
"""


def link_section(wp: dict) -> str:
    pid = wp["id"]
    rows = [LINK_MARKER, "## Individual four-session briefs", "",
            "Draft planning only; these links do not activate or complete sessions.", ""]
    for stage, (title, _, _, _) in STAGES.items():
        target = session_path(int(pid[-3:]), stage)
        rows.append(f"- [{pid} {stage}: {title}]({relative(target, wp['declaration'])})")
    rows += ["", "Apply `governance/session-briefs/PROTOCOL.md`; retain real approval and audit requirements.",
             "<!-- END GENERATED SESSION BRIEF LINKS -->", ""]
    return "\n".join(rows)


def build(root: Path, baseline: str) -> tuple[dict[str, str], dict]:
    validate_profiles()
    if not re.fullmatch("[0-9a-f]{40}", baseline):
        raise ValueError("Planning baseline must be a full Git SHA")
    wps = read_json(root / "governance/work-packages/index.json")
    if [wp["id"] for wp in wps] != [f"WP-{n:03d}" for n in range(1, 37)]:
        raise ValueError("Authoritative declarations must contain all 36 packages in order")
    requirements = {row["id"] for row in read_json(root / "governance/requirements/requirements.json")}
    outputs: dict[str, str] = {}
    rows = []
    for wp in wps:
        if not set(wp["requirements"]) <= requirements:
            raise ValueError(f"{wp['id']}: unknown governing requirement")
        source = (root / wp["declaration"]).read_text(encoding="utf-8")
        contract = contract_text(source)
        number = int(wp["id"][-3:])
        for stage in STAGES:
            path = session_path(number, stage)
            content = render_brief(wp, stage, contract, baseline)
            outputs[path] = content
            previous, following = neighbours(number, stage)
            rows.append({
                "id": f"BRIEF-{wp['id']}-{stage}", "package": wp["id"], "stage": stage,
                "status": "DRAFT_NOT_AUTHORIZED", "path": path,
                "sha256": digest(content.encode()), "predecessor": previous,
                "successor": following, "requirements": wp["requirements"],
                "contract_sha256": digest(contract.encode()),
                "declaration": wp["declaration"],
            })
        original = source.split(LINK_MARKER)[0].rstrip() + "\n"
        outputs[wp["declaration"]] = original + "\n" + link_section(wp)
    overview = overview_text(wps, baseline)
    outputs[f"{BASE}/README.md"] = overview
    book = masterbook(wps, outputs, baseline, (root / BASE / "PROTOCOL.md").read_text(encoding="utf-8"))
    outputs[BOOK] = book
    catalog = {
        "schema_version": "0.1", "kind": "SESSION_BRIEF_PLAN",
        "status": "DRAFT_NOT_AUTHORIZED", "approval": "PENDING",
        "baseline_commit": baseline, "package_count": 36, "brief_count": 144,
        "session_order": list(STAGES), "briefs": rows,
        "inputs": [{"path": path, "sha256": digest((root / path).read_bytes())} for path in INPUTS],
        "overview": {"path": f"{BASE}/README.md", "sha256": digest(overview.encode())},
        "masterbook": {"path": BOOK, "sha256": digest(book.encode())},
    }
    outputs[f"{BASE}/catalog.json"] = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    return outputs, catalog


def overview_text(wps: list[dict], baseline: str) -> str:
    rows = []
    for wp in wps:
        cells = [
            f"[{wp['id']}]({relative(wp['declaration'], BASE + '/README.md')})",
            wp["title"],
        ] + [f"[{stage}]({wp['id']}/{stage}.md)" for stage in STAGES]
        rows.append("| " + " | ".join(cells) + " |")
    return f"""# AxiomLint Individual Session Briefs

This planning expansion contains **144 individual briefs for all 36 work packages**.
Every package follows S1 implementation, S2 independent audit, S3 finding-only
remediation, and S4 documentation/closure; none has been executed or approved by
creating this catalogue. Existing live states and pending ratifications remain unchanged.

Planning baseline: `{baseline}`. Begin with [the four-session protocol](PROTOCOL.md)
and the actual declaration, not a later-stage prompt chosen out of order.
The [consolidated masterbook]({relative(BOOK, BASE + '/README.md')}) contains the
same full briefs. [Source/design rationale]({relative('docs/research/session-brief-design.md', BASE + '/README.md')})
explains technical and experimental distinctions.

## How to use a brief

Read current authority/state, verify entry/dependency approval, pin a real
revision and owner/context, then instantiate a live record only for the
authorized session. Freeze the approved brief revision in that record.
Use a different context for S2 and independent S3 delta review. A no-findings S2
still requires an S3 no-change verification and separate commit.

The user requested planning, not activation or charter ratification. All future
briefs are DRAFT_NOT_AUTHORIZED. WP-001's open S1 is supplemented, not recreated.
Do not overwrite historical records with the draft catalogue.

## Navigation

| Package | Subject | Implementation | Independent audit | Remediation | Documentation/closure |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## Validation

```sh
python3 tools/check_session_briefs.py
python3 tools/local_check.py
```

Per-package suites are planned and must be implemented by their authorized S1:
`python3 tools/run_wp_tests.py WP-NNN` deliberately refuses empty/all-skipped
selections. Do not run nonexistent future tool suites just to obtain a zero exit.
No hosted CI, push, installation or subject/backend execution is part of this task.

## Decisions before execution

Ratify charter/AMD-001 and bootstrap scope first. Resolve WP-025 calibration
data versus corpus-order dependency without leaking later holdouts. Obtain
separate host provisioning approval where required. Keep remote comparison arms
and public publication disabled unless separately authorized.
EXP-E2 independent protocol review happens before measurement within S1; the
later S2 is not a retroactive substitute.

## Integrity and revision policy

`catalog.json` records every brief digest, package-contract digest, global
predecessor/successor and input hashes. Source contract changes or manual brief
edits fail reproducibility checks. Review and rebaseline plans deliberately;
do not regenerate accepted or executed history. Draft status is not a waiver.
"""


def masterbook(wps: list[dict], outputs: dict[str, str], baseline: str, protocol: str) -> str:
    text = [
        "# AxiomLint Four-Session Briefs Masterbook",
        "",
        "Full individual session briefs for all 36 work packages: 144 proposed sessions.",
        "This is a planning document, not execution, approval or closure evidence.",
        f"Planning baseline: `{baseline}`. Read the protocol before selecting a session.",
        "",
        "## Planning protocol", "",
    ]
    text.append(re.sub(r"^(#+) ", r"##\1 ", protocol, flags=re.M))
    text += ["", "## Contents", ""]
    for wp in wps:
        number = int(wp["id"][-3:])
        links = []
        for stage, (title, _, _, _) in STAGES.items():
            anchor = re.sub(r"[^a-z0-9 -]", "", f"{wp['id']} {stage} {title}".lower()).replace(" ", "-")
            links.append(f"[{stage}](#{anchor})")
        text.append(f"- **{wp['id']}: {wp['title']}**: " + " | ".join(links))
    for wp in wps:
        for stage in STAGES:
            content = outputs[session_path(int(wp["id"][-3:]), stage)]
            # Convert only brief-to-brief links to self-contained masterbook anchors.
            def anchor_link(match):
                label, target = match.groups()
                if re.fullmatch(r"WP-\d{3}-S[1-4]", label):
                    target_stage = label[-2:]
                    target_title = STAGES[target_stage][0]
                    anchor = re.sub(r"[^a-z0-9 -]", "",
                                    f"{label[:6]} {target_stage} {target_title}".lower()).replace(" ", "-")
                    return f"[{label}](#{anchor})"
                return match.group(0)
            content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", anchor_link, content)
            text += ["", "---", "", re.sub(r"^(#+) ", r"#\1 ", content, flags=re.M)]
    return "\n".join(text).rstrip() + "\n"


def write(root: Path, baseline: str) -> dict:
    catalog_path = root / BASE / "catalog.json"
    if catalog_path.exists():
        raise ValueError("Existing catalogue: refuse to overwrite planned or accepted history")
    actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().strip()
    if actual != baseline:
        raise ValueError("Authoring HEAD differs from declared baseline; recheck scope before writing")
    runtime_path = root / "governance/sessions/index.json"
    runtime_before = runtime_path.read_bytes()
    outputs, catalog = build(root, baseline)
    before = {path: (root / path).read_bytes() if (root / path).exists() else None for path in outputs}
    for path, content in outputs.items():
        target = root / path
        if target.exists() and path not in {f"governance/work-packages/WP-{n:03d}.md" for n in range(1, 37)}:
            raise ValueError(f"Refusing preexisting output {path}")
        if target.exists() and LINK_MARKER in target.read_text(encoding="utf-8"):
            raise ValueError(f"Preexisting generated navigation in {path}")
    for path, content in outputs.items():
        target = root / path
        current = target.read_bytes() if target.exists() else None
        if current != before[path]:
            raise ValueError(f"Concurrent edit detected: {path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    if runtime_path.read_bytes() != runtime_before:
        raise ValueError("Runtime session register changed during plan generation")
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    catalog = write(ROOT, args.baseline) if args.write else build(ROOT, args.baseline)[1]
    print(f"PLANNING_ONLY packages={catalog['package_count']} briefs={catalog['brief_count']} approval=PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
