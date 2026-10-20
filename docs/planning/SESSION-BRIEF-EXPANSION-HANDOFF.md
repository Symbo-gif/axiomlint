# AxiomLint Session-Brief Expansion Handoff

The laptop repository now contains **144 full individual briefs for all 36 work
packages**, plus a linked catalogue and a consolidated Markdown masterbook.
This is a planning-only expansion authorized by the current request, not
ratification, execution, independent audit or closure of those sessions.

## Locations and sequence

- **Navigation:** `governance/session-briefs/README.md`, with four direct links
  for every work package.
- **Individual briefs:** `governance/session-briefs/WP-NNN/S1.md` through `S4.md`.
  Each original WP declaration now links directly to its four briefs.
- **Masterbook:** `docs/planning/axiomlint-session-briefs-masterbook.md`, with
  the same complete text and internal navigation.
- **Planning contract:** `governance/session-briefs/PROTOCOL.md` and
  `governance/session-briefs/catalog.json`.
- **Design provenance:** `docs/research/session-brief-design.md` and the
  package-specific source profiles in `tools/session_brief_profiles.py`.

Every package preserves S1 implementation, S2 independent read-only audit,
S3 finding-only remediation and S4 documentation/closure. All stages need their
own actual state record and distinct session-summary commit. A no-findings S2
still requires independently verified S3 no-change closure, not stage skipping.
The planned sequence has 144 sessions; additional corrective work may require
a separately approved package with another full four-stage cycle.

## What each individual brief contains

Every brief has role/activity boundaries, authority reads, dependency/entry
gates, scope/non-goals, package-specific actions, proposed artifact paths,
the original acceptance clause, tailored acceptance/negative-test matrix,
local commands, stop/block conditions, exit criteria, rollback/retention,
handoff and technical references. Each runs approximately 1,100-1,220 words.

S1 tells the implementer what to build and test. S2 gives a different reviewer
concrete threats and falsification checks while forbidding source fixes.
S3 provides conditional package-specific remediation guidance but never invents
findings; only actual S2 IDs authorize changes. S4 identifies real documentation,
traceability, local acceptance and approval evidence required for closure.

## Non-obvious constraints made explicit

- **Experimental review:** EXP-E2 approval precedes EXP-E3 outcome generation
  inside S1. The later S2 is not retroactive preregistration or protocol review.
  S3 cannot move thresholds or retry negative results into success.
- **Calibration dependency:** WP-025 must use an approved independent
  calibration corpus disjoint from future holdouts, or receive a scope/order/split
  amendment. An uncalibrated fallback cannot silently pass calibrated G5.
- **Proof trust:** Lean sessions inspect transitive axioms and pinned-toolchain
  native-evaluation trust, not just textual `sorry` scanning.
- **Local-only acceptance:** hosted CI, remote runners and pushes remain
  prohibited. Charter/AMD-001 ratification is still required for authoritative
  local closure. Older evidence never automatically covers a later commit.
- **Sensitive actions:** provisioning, external model/comparator access,
  signing credentials and public publication need separate authorization.

## Verification actually performed

The unchanged baseline passed 106 local tests before expansion. The expanded
repository then passed all four foundation gate commands and **135 tests with
zero failures or skips**, including 29 added planning/selection-guard tests.
The catalogue checker passed exact coverage/order, original-acceptance retention,
source/input/digest checks, stage boundaries and deterministic rendering.
Final committed-head and fresh-local-clone results are retained under
`artifacts/session-brief-expansion/`; do not substitute these author checks for S2.

At initial generation, each brief had 1,103-1,213 words. The source profiles,
protocol, schema and renderer are digest-bound in the catalogue; a manually
changed or rehashed brief, changed contract, missing stage, path escape,
fabricated approval or removed declaration navigation fails validation.
The renderer refuses to overwrite an existing catalogue, protecting against
silent regeneration of accepted or executed history.

## Preserved live authority

Planning baseline: `083f21c4b12a60c8556138d26d0aee516eb24d2b`.
The live session register remains four existing WP-001 records; only WP-001
remains active. The package-state index, live sessions, project configuration,
charter and AMD-001 remain byte-for-byte unchanged from that baseline.
No approval, finding disposition, backend enablement, benchmark or phase closure
was fabricated. Individual declaration changes are navigation additions only.

## Commands and next use

```sh
cd /home/themichael/PerplexityWorkspace/axiomlint
python3 tools/check_session_briefs.py
python3 tools/local_check.py
```

At actual approved package implementation, create the declared
`tests/test_wp_NNN_*.py` coverage and run `python3 tools/run_wp_tests.py WP-NNN`.
That runner rejects absent, empty and all-skipped suites; the planning task did
not fake 36 implemented package test suites.

Resolve the existing adoption/ratification decisions, finish the open WP-001 S1
handoff legitimately, and use a genuinely separate context for S2. Read and
freeze the approved brief at activation; keep actual runtime progress separate
from this draft planning catalogue.

