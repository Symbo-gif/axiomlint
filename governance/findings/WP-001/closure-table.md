# WP-001 S3 finding closure table

Session: `SESSION-WP-001-S3` (finding-only remediation, activity boundary `FINDINGS_ONLY`).
Entry HEAD: `63bd5f8bc6e66803cd4d5a06c92b6701b1ac09f6`, clean after restoring four S2 files
that were found truncated to 0 bytes on disk (see the S3 handoff). Source of findings:
`governance/audits/WP-001/S2-report.md` (verdict PASS-WITH-FINDINGS) and `S2-findings.json`.

This table grants no package closure, no G0 passage, no risk acceptance, no waiver and no
WP-002 activation. The fix commit and gate run identities are recorded in
`governance/execution/WP-001/S3/record.json`, because a commit cannot contain its own hash.

## Findings

| ID | Sev | Disposition | Change | Regression tests | Verification status |
|---|---|---|---|---|---|
| FIND-S2-001 | D3 | FIXED by remediator; awaiting independent verification | `tools/verify_local_run.py`: for `kind == ACCEPTANCE_CANDIDATE`, any nonzero `skipped` is now an error (`Acceptance candidate test execution has skipped tests`). The existing empty/incomplete/all-skipped check is unchanged. | `tests/test_run_verifier.py`: `test_acceptance_candidate_partial_skips_rejected` (199/199/5), `test_acceptance_candidate_single_skip_rejected` (2/2/1), `test_acceptance_candidate_zero_skips_passes` | Pre-fix: both rejection tests FAILED (no error raised); positive test passed. Post-fix: all pass. Logs `artifacts/wp001-s3-remediation/prefix.*.log`, `postfix.*.log`. Remediator evidence only, not an independent audit. |
| FIND-S2-002 | D4 | FIXED by remediator; awaiting independent verification | `src/axiomlint/schema.py`: new `SCALAR_KEYWORD_TYPES`; `check_schema` rejects `minimum` unless `type` is `integer`/`number`, and `pattern`, `minLength`, `maxLength` unless `type` is `string`. Untyped or mismatched declarations are rejected. | `tests/test_schema.py`: `test_scalar_keywords_require_compatible_declared_type` (8 subcases), `test_scalar_keywords_with_compatible_type_accepted`, `test_untyped_value_cannot_bypass_minimum_or_pattern` | Pre-fix: 10 subcase failures (schemas accepted); positive test passed. Post-fix: all pass; `tools/hygiene_check.py` confirms all published schemas still satisfy the rule. Remediator evidence only, not an independent audit. |
| FIND-S1-001 | D3 | VERIFIED (register reconciliation) | No code change in S3. `governance/registers/findings.json` moved from PENDING to VERIFIED, citing the S2 report. | `tests/test_gate.py`: `test_umask_readwrite_permissions_do_not_change_git_source_identity`, `test_executable_bit_changes_source_identity` | Independently verified by the S2 auditor (context `39122e38-95a9-41a1-b210-d98ed7f9618a`): fresh clones at `846b0dcbae94b0eb268fe10571c395c90a4f1228` gave `81f219a370872e93bae912093f2d1b54396258aea2536b895b09dc037730de5f` and at `ff38d388331699cd0d7c2a3adc9d1e88d8297e8d` gave `740e7097eddc287a8688bc885ea9df8677a60e3c6cfd847886d14f01f294c439`, byte-identical across clones. The original technical fix commit is `fe3be9da8f7b8ada431b4656ea8e9e1b7ab055c4`. |

## Retained items (not closed, not waived, not carried)

| ID | Sev | Status | Note |
|---|---|---|---|
| DEV-001 | D2/G0 | OPEN | Resolved only at S4 package closure. `governance/registers/deviations.json` unchanged. |
| DEV-002 | D2/G0 | OPEN | Resolved only at S4 package closure. `governance/registers/deviations.json` unchanged. |

## Observations outside scope (no change made)

- The FIND-S2-002 fix covers the scalar keywords named by the finding (`minimum`, `pattern`) plus
  `minLength`/`maxLength`. `minItems` is likewise skipped by `validate()` for non-arrays but is not
  scalar-specific and is not covered. No finding exists for it, so it was not changed.
- `DEVELOPMENT` runs may still contain partial skips; the finding and its remedy concern
  `ACCEPTANCE_CANDIDATE` runs only.
- FIND-S2-001 and FIND-S2-002 are recorded in `S2-findings.json`, not in the findings register. No
  register row was added because S3 was not asked to, and the register has no representation
  for "fixed, awaiting independent verification".

## Independence

No separate reviewer context exists for S3. The independent delta re-audit required by the S3 exit
gate is PENDING (see `governance/audits/WP-001/S3-delta-review.md`). S3 exit and S4 entry remain
unmet until a genuinely separate reviewer verifies FIND-S2-001 and FIND-S2-002.
