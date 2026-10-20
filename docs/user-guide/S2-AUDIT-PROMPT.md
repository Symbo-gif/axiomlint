# Separate-context S2 audit handoff

Use this in a genuinely new agent context or give it to an independent human.
The authoring session has not performed S2. Resolve charter/scope ratification
and formal S1 exit before starting an accepted S2 session.

## Reviewer instructions

Audit the AxiomLint foundation at
`/home/themichael/PerplexityWorkspace/axiomlint`. Source is read-only throughout
audit. Start by inspecting actual Git status/head and pinning the reviewed
revision, then read the original plan, charter, AMD-001, methodology, security,
evidence, testing and current WP-001 declaration before relying on the handoff.
Do not trust the author's claimed test count without reproducing it.

Run all checks only on this laptop. No hosted CI, pushes, installations,
network-model calls or reviewed-subject execution. Rootless isolation is not
implemented; do not run hostile resource/escape payloads naked on the host.
Use a clean local checkout and inspect each command's exact scope.

Assess implementation against authorized foundation scope, explicit deviations,
unimplemented controls and claim boundaries. Examine schema strictness,
duplicate keys/numeric semantics, source identity and dirty-state enforcement,
artifact corruption/symlink handling, trusted-parent assumptions, local-gate
false-green paths, actual test breadth, record cross-references, S1-S4 ordering,
privacy, licensing and scientific preregistration boundaries.

Independently inspect FIND-S1-001 and its regression tests, then reproduce both
main and fresh-clone identities. Verify retained raw logs/checksums; do not
mistake historical manifests for coverage of a newer documentation commit.

Record every actionable finding with ID, D1-D4, exact location and governing
clause, failure mode, impact, reproduction/evidence and remedy. State what you
did not examine and what remains deferred. Produce an S2 report with reviewed
head, reviewer/context identity, raw command evidence and PASS,
PASS-WITH-FINDINGS or FAIL. A D1 requires FAIL. Do not modify source to fix
issues during S2 or invent approvals/closure. Commit audit records separately
only when authorized; remediation belongs to S3.

