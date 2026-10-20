# Work-package, session and scientific methodology

This standard governs process, not just file layout. A passing structural
validator cannot authorize a session or judge scientific validity.

## Work-package contract

Before implementation, declare ID, owner, status, approval, dependencies,
objective, governing requirements, exact file/subsystem scope, non-goals,
acceptance criteria and evidence, risks, test plan, documentation impact,
rollback, and S1-S4 outputs. Only one package is ACTIVE. Draft future
declarations may exist but cannot satisfy approved-entry conditions.

The original plan is preserved. Work-package drafts refer to its acceptance
criteria; local-only tailoring must never silently erase those criteria.
Scope changes need an amendment, not incidental implementation.

## Sessions and finding handling

- **S1 implementation:** work within declared scope, add tests for changed
  behavior, retain failed attempts and local logs, identify reference availability,
  write handoff, commit implementation.
- **S2 audit:** independent context; governing contract first, exact S1 revision
  second; source read-only; reproduce tests rather than trust S1 summaries.
  Commit audit report separately with PASS, PASS-WITH-FINDINGS or FAIL.
- **S3 remediation:** findings only, highest severity first; link fix and
  regression tests; re-audit deltas independently. An empty audit still needs a
  no-change verification record and separate session commit.
- **S4 closure:** update traceability, docs, changelog and ledgers; preserve
  manifests; run applicable local acceptance; obtain explicit approval.

An audit report names reviewed head, reviewer/context, files examined, commands,
threats, requirement clauses, limits and unresolved questions. A finding has ID,
severity, exact location, failure mode, impact, evidence/reproduction, governing
clause, expected remedy, owner and disposition. Closure has independent verification.

- **D1:** critical integrity, escape, secret exposure or fabricated assurance.
  Stop affected and dependent work; audit verdict FAIL.
- **D2:** major correctness, security, scientific validity or required-control gap.
  Blocks package closure, claims and releases.
- **D3:** material nonblocking defect only with explicit policy-approved,
  bounded disposition, owner, expiry and downstream restrictions.
- **D4:** low-impact improvement. No silent deferral; carry only by explicit approval.

OPEN, FIXED-PENDING-VERIFY, VERIFIED, AMENDED and CARRIED are distinct. No
agent converts a report into “approved” because tests passed. No D1/D2 carry.

## Experimental E0-E6

Use EXP-E0 through EXP-E6 to avoid collision with evidence EV-E0 through EV-E6.
Benchmark execution is disabled in the foundation. Unit tests are engineering
verification, not a comparative experiment or effectiveness result.

- **EXP-E0 authorization:** question, campaign order, budgets, stop conditions,
  correction policy and dependencies.
- **EXP-E1 preregistration:** freeze hypotheses, task IDs, comparator selection,
  seeds, randomization/counterbalancing, cache policy, denominators, power/sample
  rationale, exclusions, multiplicity, uncertainty, statistical analysis,
  practical-effect and non-inferiority margins, abstention and resource budgets.
- **EXP-E2 independent review:** leakage, oracle validity, pseudoreplication,
  confounds, fairness and feasibility; approval before outcome access.
- **EXP-E3 execution:** protocol digest fixed; append raw outcomes including
  timeout, unknown, negative and operational abort; no retry-until-positive.
- **EXP-E4 analysis:** verify manifests first; registered analyses only for
  confirmatory claims; label all exploratory analyses, preserve raw-to-table lineage.
- **EXP-E5 acceptance:** complete report including nulls, limits and deviations;
  maintainer accepts or rejects conclusions; accepted artifacts immutable by policy.
- **EXP-E6 synthesis:** reconcile contradictions, external validity, residual
  risks and follow-up authorization; correct accepted records through errata.

Pilot tasks cannot later become untouched confirmatory holdouts. Separate
matched-harness and native-agent strata; do not pretend remote and local hardware
are identical. Keep hidden answers away from prompts, source context and product
logic. Two labels plus adjudication precede accepted ground truth.

## Evidence retention and rollback

Retain rejected, blocked and inconclusive records. Hash artifacts before
acceptance, validate schemas, preserve commands/environment and independent replay.
Accepted records are superseded through new records with parent references, never
rewritten in place. Roll back capability or source, not inconvenient history.

