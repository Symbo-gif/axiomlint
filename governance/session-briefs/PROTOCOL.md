# Four-session planning protocol

Status: DRAFT planning supplement. This document expands the existing method;
it does not ratify the charter, activate a package, close S1, or authorize an
audit, experiment, installation, hosted check, network call or publication.
Only the live state records and actual human approvals can do that.

## Stable sequence and authority

Each WP has four separately addressable briefs: S1 implementation, S2
independent read-only audit, S3 finding-only remediation, S4 documentation and
closure. Do not skip, merge or reorder them. One package is active at a time.
Four distinct session records and session-summary commits are mandatory even
when a session has no product delta. A stage may contain multiple work commits
and audit rounds; that does not make those rounds substitute sessions.

The dependency rule is the existing declaration's rule, not a new scheduling
decision. Normally finish WP-N S4 before WP-(N+1) S1. A dependency waiver, split,
reorder or additional correction package needs an actual approved amendment.
All briefs remain DRAFT_NOT_AUTHORIZED. The four existing WP-001 live session
records are not replaced with 144 invented executions.

WP-001 S1 is already open. Its S1 brief supplements remaining adoption work;
do not rerun history, discard the original commits or fabricate an earlier
approved entry. DEV-001, DEV-002, AMD-001 and FIND-S1-001 retain their actual state.

## Entry and exit discipline

- **S1:** actual declaration approval, closed dependencies or explicit approved
  waiver, scoped file/test inventory, pinned entry head and reference-availability
  probe. Reproduce baseline, implement with positive/negative tests, preserve
  failed attempts, run local gates, commit handoff and provisionally met criteria.
- **S2:** S1 exit evidence exists; a genuinely separate reviewer/context reads the
  governing contract before the diff. Reviewed source, tests, schemas and contract
  stay read-only. Write logs/audit artifacts separately, pin reviewed head, inspect
  actual changes and independently reproduce outcomes. Commit only audit records.
- **S3:** committed S2 report; work only on actual finding IDs in D1-D4 order.
  Verify regressions fail pre-fix for the intended reason and pass post-fix.
  Independent delta re-audit rounds occur within S3, with separate reviewer and
  artifact identity. If there are no findings, independently verify and commit
  a no-change closure table anyway. Do not invent findings to fill a template.
- **S4:** clean independent delta audit, all required evidence and real approvals.
  Complete documentation, ledgers, traceability and rollback; run applicable
  local acceptance on the exact candidate. Only actual approved closure permits
  a following package to activate.

D1 forces FAIL and blocks unrelated work. D1/D2 cannot be carried. D3/D4 carry
needs actual authority, owner, bounded scope, expiry and compensating controls.
A reported false positive may be declined only with reproducible rationale and
independent/authorized disposition; an agent cannot waive its own audit findings.

## Local-only verification and source identity

No hosted CI, pushes, hosted scans or remote runners. AMD-001 must be ratified
before local checks become authoritative acceptance; until then they are
development evidence. Historical plan clauses requiring hosted CI remain in
the original declaration but must never be executed by following a brief.

The known working baseline command is `python3 tools/local_check.py`. The
nonempty per-package command is `python3 tools/run_wp_tests.py WP-NNN`; it
intentionally fails until S1 creates a package-specific executable suite.
The current full suite is not a substitute for later backend/security/science
tests. Declare all additional commands and pinned local materials before use.
Missing tools, incomplete test selection or deferred mandatory checks block
that package's closure, not just a line in a summary.

Run `--require-clean` only after committing the candidate. Record commit,
dirty state, exact source identity, schema/tool/environment identities and raw
log digests; independently verify saved artifacts. A local clean replay is not
another reviewer, signed provenance or a hostile-host security guarantee.
No provisioning/download/host installation happens during tests. Obtain
separate approval before changing the host or acquiring required materials.

Do not manufacture a commit's hash inside itself. Prepare and commit a candidate,
run clean checks, and obtain a real approval bound to its commit and manifest.
If a later closure/docs record changes the head, verify that head separately;
its evidence is not inherited from the candidate. Preserve final approvals as
durable externally bound records where needed to avoid infinite self-reference.
If the current governance schema cannot represent that distinction without
invented hashes or a circular acceptance claim, open a finding and block closure
until the method/schema is legitimately amended.

## Execution and sensitive-action boundaries

Current subject execution and backends remain disabled. Future dynamic checks
need accepted WP-006 containment and the authorized capability policy. WP-006
itself needs staged independent containment-design review before dangerous
qualification tests; missing controls mean refusal, not naked-host experiments.
S2 may execute trusted verifier/tests through approved containment but cannot
alter the reviewed product source or bypass limits.

Local model service access is explicitly configured and authorized, never a
silent external fallback. Optional commercial/remote comparison arms need
separate charter/privacy/budget permission and remain outside the default plan.
Signing-key access, publication, pushing and release distribution are separately
authorized consequential actions, not consequences of drafting or closing a brief.

## Experiment checkpoints inside the four sessions

EXP-E0 authorization, EXP-E1 preregistration and independent EXP-E2 protocol
review must precede EXP-E3 data generation. For WP-030 through WP-033, S1 may
contain those preparatory checkpoints and only then frozen-protocol execution
and registered analysis. EXP-E2 is a real independent pre-execution review,
not the later S2 audit and not a fifth lifecycle session. Without it, S1 stops.

S2 independently audits protocol chronology, measurement, scorer and analysis;
S3 corrects reported defects without moving thresholds, seeds, denominators or
exclusions after results. A flaw needing new data requires a separately
authorized experiment/correction cycle; do not call retry-until-pass remediation.
S4 carries human result acceptance (EXP-E5) and appropriately scoped synthesis
(EXP-E6), preserving null, negative, unexpected and inconclusive results.
Cross-campaign synthesis closes only when the relevant campaigns actually finish.

Pilots are distinct exploratory experiments with their own preregistration and
independent review before their data exists. Pilot variance may inform a later
confirmatory protocol, but pilot tasks/outcomes cannot become untouched holdouts.
Never prefill statistical thresholds with convenient invented values.

## Dependency decisions that need approval

- **WP-025 calibration:** the original order places calibration before corpus
  governance. Either approve a separately licensed, independently labeled
  calibration dataset within WP-025, disjoint from all future confirmatory
  holdouts, or approve a scope/order/split amendment. An uncalibrated fallback
  preserves honest behavior but cannot silently satisfy a calibrated G5 gate.
- **WP-004 provisioning:** host installs and acquisition are not authorized by
  a session brief. Missing Nix/OCI/tool dependencies remain explicit entry blocks
  until separately approved local provisioning.
- **WP-032 remote arms:** default scope is local matched systems. Remote/API
  comparisons require a separate explicit amendment and privacy decision.
- **WP-036 release:** local candidate acceptance is not permission to publish.
  No hosted-check requirement reappears during release.

## Brief revisions and actual records

The catalogue binds each brief, its package contract and the generator/profile/
protocol inputs by digest. Contract changes require reviewed rebaselining.
Live progress belongs in actual execution records, not generated DRAFT plans.
Freeze the chosen approved brief revision at activation; preserve it if later
planning changes supersede the catalogue. Never regenerate accepted history in
place. The renderer refuses to overwrite an existing catalogue; revision
handling must be deliberate and reviewed, not an automatic formatting step.

