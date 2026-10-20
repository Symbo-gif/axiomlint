# AxiomLint project charter

Version: 0.1-draft. Owner and human approver: Michael Maillet.
Status: DRAFT, awaiting recorded ratification. Default profile: Research, with
High-Assurance controls for evidence, execution, benchmark acceptance and release.

## Mission and boundary

Build a local-first FOSS orchestrator that turns review candidates into bounded,
replayable evidence. Initial subjects are small deterministic typed Python
functions and compact patches. Absence of a finding never means correctness.
Models, executable counterexamples, symbolic results, kernel proofs and source
correspondence are distinct claims, not interchangeable confidence scores.

Automatic generation, patching, repair, remote services, production execution,
repository-scale analysis and new languages are outside this charter.
The foundation may draft governance and scaffold future interfaces, but may not
claim the corresponding work packages or gates are complete.

## Authority and decision rights

Precedence, highest first:

1. Ratified charter and explicit approved amendments, including the user's
   current prohibition on hosted checks.
2. Normative project safety, evidence, governance and benchmark standards.
3. Approved work-package and experiment declarations.
4. Versioned specifications and semantic subsets.
5. Session briefs and recipes.
6. Raw evidence, reports, logs and generated artifacts.
7. Prompts, agent instructions and generated explanations.

Conflict blocks affected work. Agents can draft and implement within authorized
scope, but cannot self-approve scope, audit verdicts, residual risks, experiment
protocols, E6 correspondence or releases. Michael is the designated approver,
not a fabricated approval signature. Every approval needs approver, exact
document/revision digest, scope, decision, timestamp and evidence location.

## Local-only adoption

The current user request authorizes scaffolding and local tests; no push,
publication, hosted test job or host-software installation is authorized.
[AMD-001](AMD-001-local-only.md) proposes the authoritative local acceptance
procedure. The explicit no-hosted-check constraint takes effect now; formal
tailoring and package closure still require ratification.

The base framework says tailoring cannot remove authoritative CI, while its CI
standard permits a charter-named alternative. We do not conceal that tension:
this is an explicit project override pending approval, not unqualified framework
compliance. Until ratified, local checks are DEVELOPMENT evidence only.

## Scope and bootstrap exception

Only WP-001 is active. Drafting all registers, requirements, threat model,
templates and inert module boundaries is preparatory work authorized by the
current request. It does not close WP-001, activate WP-002 onward, authorize
formal execution, or bypass independent audit.

Because the upstream method expects an approved declaration before S1, record
DEV-001 for constitution bootstrapping under user authorization. It must be
resolved by maintainer ratification or rollback before the next package begins.
This prevents retroactively pretending the charter had been approved.

## Independence and closure

S1 implementation, S2 independent read-only audit, S3 finding-only remediation,
S4 documentation/closure occur in order, each with its own record and commit.
Independent means a different human or genuinely separate agent context that
reads governing contracts and code directly. Self-review is useful but is not S2.
No separate reviewer has yet performed S2 for this foundation.

Package closure requires all acceptance evidence, resolved D1/D2 findings,
valid dispositions for lower-priority findings, reviewed requirement traceability,
exact-revision local acceptance, independent replay and human approval. Releases
add license/security review, approved residual risks, SBOM, provenance, signatures
and independently checked reproduction; none are implied by this scaffold.

## Licensing and retention

Project code is MIT. Mandatory dependencies, rules, models and corpus materials
need recorded OSI-compatible licenses and version/digest review before adoption.
No proprietary engine is mandatory. No online API is required. No telemetry is
enabled. Raw and derived accepted research evidence is permanently retained
subject to privacy and license limits, with manifests and redacted public views.

## Amendments

An amendment identifies baseline digest, conflict, proposed replacement, reason,
impact, compensating controls, approval and effective revision. Historical
evidence remains unchanged. A threshold or hypothesis affected by an execution
cannot be revised retroactively: start a new protocol and retain the old outcome.

