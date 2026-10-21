# AxiomLint

A local-first, FOSS evidence-carrying review orchestrator for small, deterministic,
typed Python functions. This repository is a governed foundation, not an operational
formal analyzer or a security sandbox.

## Start locally

Python 3.12 or newer and Git are the only foundation prerequisites. No package
installation, model endpoint, account, network access, or hosted CI is required.

```sh
python3 tools/local_check.py
PYTHONPATH=src python3 -m axiomlint status
PYTHONPATH=src python3 -m axiomlint governance check --root .
PYTHONPATH=src python3 -m axiomlint inventory examples/absolute.py
python3 tools/local_check.py --require-clean
```

The last command is an acceptance-mode check and refuses a dirty Git worktree.
Other commands are development checks only. A green development run is not package
closure, independent audit, release authorization, or a correctness proof.

## Implemented and deliberately absent

- Implemented: strict foundation-record schemas; schema-subset validation;
  governance consistency checks; a local content-addressed evidence store;
  bounded, nonexecuting AST inventory; explicit disabled capabilities; local test
  capture with exact source-tree digests.
- Scaffolded: intake, adapters, SpecIR, fusion, reporting, backends, Lean, rules,
  benchmark corpus/harness/scorer/analysis, architecture and assurance case.
- Disabled: analyzed-code execution, remote models, solver/CAS/proof invocation,
  automatic changes, benchmarking, assurance-level promotion, releases.
- Deferred: dependency lock generation, Ruff/mypy/pytest/coverage, full JSON Schema
  and SARIF validation, Nix/OCI environments, signing, SBOM/SCA and sandbox probes.
  These are tracked, not silently skipped or represented as passed.

## Governing entry points

- [Active ratified authority](governance/charter/ACTIVE-BASELINE.json)
- [Actual principal ratification](governance/approvals/APR-001-constitutional-ratification.md)
- [Derived authority map](governance/decisions/authority-map.md)
- [Charter](governance/charter/CHARTER.md)
- [Local-only amendment](governance/charter/AMD-001-local-only.md)
- [Bounded-delegation amendment](governance/charter/AMD-002-delegated-decisions.md)
- [Methodology](governance/standards/methodology.md)
- [Requirements](governance/requirements/requirements.json)
- [Work-package register](governance/work-packages/index.json)
- [Current state](governance/STATE.md)
- [Implementation and verification handoff](HANDOFF.md)
- [All 144 individual session briefs](governance/session-briefs/README.md)
- [Four-session masterbook](docs/planning/axiomlint-session-briefs-masterbook.md)
- [Current WP-001 S1 author handoff](governance/execution/WP-001/S1/handoff.md)
- [Independent S1 readiness decision](governance/readiness/WP-001/round-3/review.md)
- [S1 exit recording supplement](governance/execution/WP-001/S1/exit.md)
- [S2 preparation, not started](governance/execution/WP-001/S2/entry-preparation.md)
- [Claim glossary](governance/standards/claim-glossary.md)
- [License/material-adoption policy](governance/standards/license-policy.md)
- [Amendment and exception procedure](governance/standards/amendments-and-exceptions.md)
- [Local checks](docs/user-guide/local-development.md)
- [Research and adoption rationale](docs/research/foundation-decisions.md)
- [Original plan](docs/reference/axiomlint-plan.md)

The principal ratified the charter and AMD-001/AMD-002 in APR-001. Their exact
reviewed bytes are preserved; historical DRAFT/PROPOSED labels in those snapshots
do not supersede the active source-bound approval record.

Only WP-001 is active. Its S1 is recorded CLOSED following the genuine separate
readiness decision for implementation commit
`846b0dcbae94b0eb268fe10571c395c90a4f1228`; the separate metadata recording head
requires its own independent verification before transition completion or S2
entry. See the exit supplement for that external receipt and exact identities.
S2 is PLANNED, NOT STARTED; S3/S4 remain BLOCKED. Later packages remain planned,
and no package or phase gate is closed. DEV-001/DEV-002 remain OPEN and
FIND-S1-001 remains PENDING. This is not a claim that WP-002 through WP-036
were executed or that ratification verifies implementation.

The name follows the attached plan and remains provisional. No legal clearance
or later assistant-suggested rename is inferred as a maintainer decision.
