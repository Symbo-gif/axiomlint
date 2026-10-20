# Research-informed foundation decisions

Research date: 2026-10-20. Purpose: resolve governance, local-only verification,
trust and evidence design before activating formal-analysis work packages.
This is a focused foundation investigation, not a completed literature review.

## Baseline and explicit tailoring

The supplied plan is the product baseline. The governing reference framework
requires declaration, independent S1-S4, immutable-revision evidence and recorded
human approvals; its Research profile adds preregistered EXP-E0-E6
([framework README](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/README.md),
[session cycle](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/work-package-session-cycle.md),
[experiment cycle](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/experiment-cycle.md)).

The framework's tailoring document says authoritative CI remains mandatory,
whereas its CI standard allows a charter-named alternative; therefore the user's
local-only instruction needs an explicit project override and compensating
evidence, not a claim that hosted CI ran
([tailoring](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/tailoring.md),
[CI standard](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/standards/ci-cd-and-branch-protection.md)).
Project decision: AMD-001, no hosted workflow, ratification pending.

## Secure development and standards status

NIST SSDF organizes practice around Prepare the Organization, Protect the
Software, Produce Well-Secured Software and Respond to Vulnerabilities
([NIST SSDF](https://csrc.nist.gov/projects/ssdf)).
At this research date, NIST lists SP 800-218 v1.1 as final and revision 1/v1.2
as an initial public draft; do not quietly treat a draft as a final baseline
([NIST publications](https://csrc.nist.gov/publications/sp800?source=post_page---------------------------&page=15)).
Project mapping is design guidance, not certification:
PO -> charter/roles/requirements/local checks; PS -> source/evidence binding;
PW -> tests/threat model/dependency review; RV -> findings/incidents/errata.

## Evidence formats and validation

SARIF 2.1.0 is appropriate for interchange and distinguishes tool-execution
failures from source findings; a failed run cannot imply a complete empty result
set ([OASIS SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html)).
Decision: defer SARIF emission until the official schema is locally pinned;
never ship a nominally valid placeholder as a product review.

JSON Schema Draft 2020-12 defines assertions and property controls but does not
automatically validate application-specific authority or semantic relationships
([JSON Schema core](https://json-schema.org/draft/2020-12/json-schema-core)).
Decision: publish portable simple schemas, implement only an explicitly closed
foundation vocabulary, reject unsupported keywords, and add semantic governance
checks. Do not claim a complete Draft 2020-12 engine.

## Hostile inputs and isolation

Python warns that complex AST inputs can exhaust stack resources; parsing is
not proof of executable validity, and literal_eval is not safe against resource
attacks ([Python AST documentation](https://docs.python.org/3/library/ast.html)).
Decision: small trusted-file inventory only, compile without executing for
scope validity, no subject import, no hostile-input assurance.

Podman documents network-deny, read-only, capability and resource controls,
with rootless/cgroup limitations ([Podman run](https://docs.podman.io/en/latest/markdown/podman-run.1.html)).
Decision: leave the runner disabled; merely writing an OCI recipe is not an
isolation implementation. Probe enforcement and adversarial cleanup in WP-006.

## Provenance without inflated supply-chain claims

SLSA v1.1 distinguishes unsigned provenance from hosted signed/hardened builds;
local development/test builds alone do not confer those guarantees
([SLSA security levels](https://slsa.dev/spec/v1.1/levels)).
Decision: capture exact Git head, dirty state, content fingerprints and log
digests, but claim no SLSA level, signing or malicious-host tamper resistance.
The v1.2 levels URL did not fetch successfully during research; this document
uses the explicitly versioned v1.1 source, not an invented “latest” claim.

## Research gaps and follow-through

Backend versions/licenses, Lean axiom controls, formal source semantics, runtime
schema design, official SARIF schema pin, SBOM/SCA tools, Nix/OCI locks, solver
diversity and statistical thresholds require later package-specific investigation.
No benchmark, model evaluation, power calculation or formal proof was performed.
The baseline framework was read from the pinned source tree above; project
documents are new adaptations, not an unmodified vendored framework.

