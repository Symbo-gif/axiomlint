# S1 author verification record

These are retained engineering observations, not accepted benchmark results,
formal evidence tiers, human approvals or independent S2 audit reports.
Original raw manifests/logs are preserved byte-for-byte. Schema snapshots for
older runs are recovered from their pinned historical source revision.

## Run chronology

| Run ID | Source state | Tests | Interpretation |
|---|---|---:|---|
| 20261020T165407Z-460078ab17fe | d511612, clean | 85 | Initial foundation development check |
| 20261020T165639Z-15e5f94a3867 | d511612 + dirty refinement | 103 | Development only; never acceptance |
| 20261020T165700Z-cd5fef58068d | 0b6e985, clean | 103 | Clean check, old full-permission fingerprint |
| 20261020T165701Z-8232cfd0a7cb | fresh local clone of 0b6e985 | 103 | Tests pass, but cross-checkout fingerprints differ; not reproducibility acceptance |
| 20261020T165929Z-d414257d80d7 | 0b6e985 + dirty correction | 106 | Development only; new schema 0.2 and Git-mode fingerprint |
| 20261020T165930Z-4e0d9add3254 | fe3be9d, clean | 106 | Corrected implementation local check and evidence verification |
| 20261020T165931Z-1d88bcbe7f93 | fresh local clone of fe3be9d | 106 | Same commit and tree fingerprint; author replay only |
| 20261020T170216Z-32cbf4c6857c | fe3be9d + dirty handoff | 106 | FAIL: one negative-test fixture assumed live S1 commit metadata was empty |

All runs before 17:02:16Z had zero failures and zero skipped tests. The failed
cross-checkout identity expectation at 0b6e985 is preserved as a finding, not
hidden because individual test processes exited successfully.

The handoff run at 17:02:16Z failed one of 106 tests after recording the real S1
commit. Its negative fixture changed status to CLOSED but assumed the live
commit field remained empty. The correction explicitly blanks both commit and
report and asserts both failures; it does not weaken validation or remove the
test. The raw failed run is retained. Subsequent verification is a separate run,
not a rewrite of that result.

## Correction and schema version boundary

Old fingerprint included ordinary read/write permissions; Git checkout inherited
0664 rather than source transfer's 0644. Source bytes were identical.
New algorithm `sha256-path-bytes-gitmode-v1` includes paths, bytes and Git's
user-executable mode. It does not claim full environment/security-policy equality.

Local-run schema 0.2 records that algorithm, schema digest and snapshot. Current
verifier intentionally supports the pinned 0.2 schema only; use the historical
source/schema for 0.1 development runs rather than rewriting them to appear new.
Migration support is deferred to WP-005. Nothing here is a signed attestation.

## Corrected implementation identities

Commit: `fe3be9da8f7b8ada431b4656ea8e9e1b7ab055c4`.
Both tree digests:
`3f53236db91b6615c4aec6eaea47ca75fd55f6810bef5c277f316c88106f901a`.
Main manifest SHA-256:
`a38fc9e67910cd288d135f622f9795d56e34566d27d928a1ff04e4fa35193f79`.
Fresh-clone manifest SHA-256:
`58ee54fb11133d16365f63941e171ff8aa429f356bc5f61e006b63bfd63d8c55`.

Final docs/evidence commits have different source identities and are rechecked
separately; they do not retroactively inherit these exact-revision observations.
