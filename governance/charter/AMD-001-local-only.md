# AMD-001: Local-only authoritative verification

Status: PROPOSED, ratification pending.
Requested constraint: user instruction on 2026-10-20, “only run test things
locally, no hosted CI checks.” This constraint is effective immediately.
Baseline: attached AxiomLint plan and pinned Methodology-Workflow-Governance.

## Explicit replacements

Replace requirements for hosted authoritative CI, pushed-head validation, hosted
branch-check enforcement and hosted release workflows with a charter-named
local acceptance procedure. No `.github/workflows`, GitLab pipelines, remote
runner, scheduled hosted scan, or automatic pre-push network operation is added.
No push or public release happens under this request.

This is a recorded project-level deviation from the base framework's statement
that authoritative CI remains mandatory under tailoring. The upstream CI standard
also permits a charter-named alternative, but that does not automatically approve
this amendment. The project does not assert full upstream compliance.

## Authoritative local acceptance procedure

After ratification, an authorized independent reviewer uses a clean local checkout
of the exact proposed S4 acceptance commit on the laptop, without downloading
dependencies during checks. Run `python3 tools/local_check.py --require-clean`.
The runner records the Git commit, exact source-tree digest, dirty state,
Python/OS/architecture, sanitized environment policy, commands, exit codes,
elapsed time and stdout/stderr digests. Preserve the complete run directory.

The reviewer independently verifies raw logs, test counts, source-tree identity,
mandatory command inventory, and any deferred validations. The maintainer then
records an approval bound to the commit and manifest digest. An after-the-fact
documentation commit may record that acceptance, but is not itself silently
covered: it needs a separate documentation-only local verification.

Closure cannot rely on an uncommitted tree, old logs, an empty test selection,
skipped command, shell success after a swallowed error, or a verifier that only
checks its own summaries. `local_check.py` is a foundation development gate,
not complete security/release tooling; deferred controls must be satisfied
before their packages close.

## Preserved controls and limitations

No change to S1-S4 order, independent audit, human approval, E0-E6 scientific
governance, fixed thresholds, required test evidence, finding closure or retention.
Exact source binding does not imply independent reproduction or authenticated
provenance. The same user can alter Git history, files, tool binaries or logs;
unsigned local digests do not defend against that adversary.

Record unavailable platform checks as DEFERRED with owner and blocking gate.
No Windows, Nix, OCI, solver, CAS, Lean, coverage or supply-chain success is
claimed. No SLSA level, branch protection equivalence or release readiness is claimed.

## Approval record to complete

Approver: PENDING. Approved baseline digest: PENDING.
Decision and scope: PENDING. Timestamp and evidence reference: PENDING.
Expiry/reassessment: before public release, adding remote capability, changing
host authority, or changing the threat model.

