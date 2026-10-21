# WP-001 S3 delta review

> [!IMPORTANT]
> **Independence status: NOT INDEPENDENT. Independent delta review is PENDING.**
> This document is a remediator self-check of the S3 delta. The S3 brief requires a separate
> reviewer context with its own identity. None exists, and none is invented here. This file is
> not an independent audit, grants no approval, and does not satisfy the S3 exit gate.

- Remediated head reviewed: `1e1355963854104943e7d1199ea739a2b6767550`
  (remediation commit `a6403c34872ba52b61c5bd39581a380cf5b9d66a`, then test-fixture commit `1e13559…`)
- Entry head: `63bd5f8bc6e66803cd4d5a06c92b6701b1ac09f6`
- Reviewer: S3 remediator (same context as the author of the delta)
- Round: 1 (self-check)

## Delta examined

`git diff 63bd5f8..1e13559` touches only: `tools/verify_local_run.py`, `src/axiomlint/schema.py`,
`tests/test_run_verifier.py`, `tests/test_schema.py`, `governance/registers/findings.json`, and the new
`governance/findings/WP-001/closure-table.md`. No other product, schema, or contract file changed.

## Checks performed (self-check, not independent)

| Finding | Check | Result |
|---|---|---|
| FIND-S2-001 | Regression fails pre-fix for the intended reason (no error raised for 199/199/5 and 2/2/1 acceptance-candidate counts) | Confirmed, `artifacts/wp001-s3-remediation/prefix.stderr.log` |
| FIND-S2-001 | Passes post-fix; skipped=0 acceptance candidate still passes; zero/all-skipped checks unchanged | Confirmed |
| FIND-S2-002 | Regression fails pre-fix (10 subcases accepted wrong schemas) | Confirmed |
| FIND-S2-002 | Passes post-fix; all published schemas still valid (`tools/hygiene_check.py`, full gate) | Confirmed |
| FIND-S1-001 | Register VERIFIED with S2 report as evidence; the governance validator accepts the reference | Confirmed (`check_wp001_delivery.py` PASS) |
| Retained | `governance/registers/deviations.json` untouched; DEV-001 and DEV-002 OPEN | Confirmed |

## Points an independent reviewer should challenge

1. **Existing-test edit.** `test_invalid_schema_pattern` was changed from `{"pattern": "["}` to
   `{"type": "string", "pattern": "["}`. Without the edit it would still pass, but for the wrong
   reason (the type co-occurrence check fires first). The edit preserves its intent. This is the only
   change to a pre-existing assertion.
2. **Pre/post logs predate the edit.** `prefix.*.log` and `postfix.*.log` were captured before that
   one-line fixture change. The full gate on the final head covers it (205/205, 0 skipped).
3. **Keyword scope.** `minLength` and `maxLength` were added alongside `minimum` and `pattern`, for
   the same bypass class. `minItems` was not, as it is not scalar-specific and has no finding.
4. **Scope of skip rule.** The skip rule applies to `ACCEPTANCE_CANDIDATE` only, per the S2 remedy.
5. **Recorded dispositions.** FIND-S1-001 VERIFIED rests on the S2 auditor's evidence, not on a new
   S3 run of the clone check.

## Outcome

Self-check found no defect in the delta. **Independent verification of FIND-S2-001 and FIND-S2-002 is
outstanding.** S3 cannot exit and S4 cannot start until a genuinely separate reviewer completes it.
