# Claim glossary and prohibited assurance

Status: WP-001 S1 implementation of the ratified claim boundaries and existing
evidence standard. Independent S2 verification is pending. This is vocabulary,
not an operational promotion engine or proof that any backend works.

## Distinct claim types

| Claim | Required boundary | Meaning that is not permitted |
|---|---|---|
| Finding | Pinned location, failure mode, impact, assumptions, evidence and remedy | Fluent criticism is not reproduced defect evidence |
| Counterexample | Concrete source-domain input, explicit executable property/oracle, pinned code/environment and failing replay | A generated test or seed alone does not establish a source failure |
| SMT | Exact formula, logic, assumptions, solver/build, SAT/UNSAT/UNKNOWN and replay | UNSAT about a formula is not Python correctness |
| CAS | Exact query/expression, assumptions/domain, backend/build, conditional/unevaluated state and replay | Simplification cannot erase singularities or IEEE behavior |
| Lean | Pinned theorem/imports/axiom closure, approved kernel-trust policy and clean replay | Proof search text or acceptance of the wrong model is not source assurance |
| Correspondence | Independently reviewed source-to-model argument for a declared subset, pinned artifacts and required approvals | Differential tests alone do not establish refinement |
| Review verdict | Actual successful/failed/incomplete checks, preserved evidence links, disagreement and limitations | An unavailable or failed scan cannot imply a clean review |

Formal claims prove or establish something only about the object actually
checked. Source behavior, mathematical model, specification, translation and
tool output are separate objects. A true statement about an irrelevant or
vacuous specification does not satisfy the intended requirement.

## Evidence vocabulary

EV-E0 through EV-E6 describe evidence records, not a single probability scale.
No level automatically upgrades another or overrides contradictory evidence.

| Label | Necessary evidence | Bounded wording |
|---|---|---|
| EV-E0 | Attributed candidate/hypothesis | Suspected; unverified |
| EV-E1 | Reproducible, successful static-tool result | Tool detected within its configured scope |
| EV-E2 | Saved concrete input and independently justified failing replay | Reproduced failure under the recorded property/environment |
| EV-E3 | Archived SMT obligation, solver status and replay | Under this SMT model and assumptions |
| EV-E4 | Exact symbolic operation with domains, conditions and replay | Symbolically established under the stated assumptions |
| EV-E5 | Approved-policy Lean kernel replay and transitive axiom record | Proved about this formal model |
| EV-E6 | EV-E5 plus independently reviewed bounded source correspondence and two authorized approvals | Established for this source fragment within declared semantics |

The current foundation has no operational EV-E1 through EV-E6 promotion
capability. Unit tests of its governance utilities are engineering verification,
not examples of those product assurance tiers.

## Outcomes, verdicts and abstention

- **NO_FINDING:** configured checks actually completed successfully and found
  no finding in their declared scope. It never means the program is correct.
- **NOT_REVIEWED:** inventory/metadata only, or the required analysis never ran.
  The current AST inventory uses this verdict even when parsing succeeds.
- **UNKNOWN:** the tool did not decide the declared obligation. Preserve its
  reason; do not map it to false, clean, SAT or UNSAT.
- **TIMEOUT:** the declared time/resource budget expired. Partial output is
  diagnostic, not a completed empty scan.
- **UNSUPPORTED:** semantics, syntax, contract or capability is outside support.
  Refuse the unsupported claim; do not guess a translation.
- **ERROR / FAILED:** invocation, parsing, proof, replay or validation failed.
  Preserve raw output and nonzero/signaled status rather than success wording.
- **CONFLICT:** decisive or otherwise relevant evidence disagrees. Keep both
  branches and open a finding; no majority voting or convenient selection.
- **NOT_RUN:** the check did not execute, including absent optional tools.
  Do not include it in a denominator as if it passed.

Abstention reasons include insufficient specification, untrusted execution,
unsupported semantics, contradictory evidence, timeout and missing required
materials. Denominators and incomplete coverage must remain visible.

## Confidence, severity and independence

Severity is impact; evidence tier is evidence type; calibrated confidence is an
empirical property requiring approved held-out data and verified analysis.
No numeric confidence is invented from a tool name, model prose or evidence tier.
The unavailable calibration path remains unavailable until its actual criteria
are satisfied; a no-confidence fallback cannot silently pass calibrated G5.

An author-run fresh clone is reproducibility evidence from the same author,
not an independent S2. A model that generates both claim and unvalidated oracle
does not supply independent evidence. A disclosed delegate is not the principal
personally reviewing evidence, and an implementation author cannot approve
their own independent review or readiness.

## Prohibited-to-permitted wording examples

| Prohibited | Permitted bounded alternative |
|---|---|
| “No bugs; verified correct” after an empty scan | “Configured checks completed with NO_FINDING; excluded checks and semantics are listed” |
| “Z3 proved this Python function correct” | “The archived formula was UNSAT under this logic/model; correspondence status is stated separately” |
| “Lean proved the implementation” without source linkage | “The pinned theorem about this formal model replayed under the approved axiom policy” |
| “All backends agree” when one timed out | “Recorded outcomes include the timeout; no complete agreement claim is made” |
| “Immutable and authenticated” for local unsigned hashes | “Digest integrity checks passed within the trusted local-store assumptions” |
| “Independent audit passed” after author tests | “Author checks passed; independent S2 remains unperformed” |
| “Statistically supported gain” from an exploratory pilot | “Exploratory pilot observation; no confirmatory conclusion” |

