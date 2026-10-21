# WP-001 S3 delta review — independent

- **Reviewer context ID:** `374e955d-a5d5-46b4-892c-c52335b5c716`
- **Independence:** Genuinely separate execution context. No continuity claimed with the S1
  author (`72131cdc-563c-4d43-a6b3-f37dd1253e0c`), the S2 auditor
  (`39122e38-95a9-41a1-b210-d98ed7f9618a`), or the S3 remediator
  (`0e8e8253-00be-41e0-9197-dc87c53d3aa1`).
- **Pinned head reviewed:** `b40f5071f8af0e857d35a59102eb10246daf04d6`
- **Entry commit for S3:** `63bd5f8bc6e66803cd4d5a06c92b6701b1ac09f6`
- **Remediation commits:** `a6403c34872ba52b61c5bd39581a380cf5b9d66a`,
  `1e1355963854104943e7d1199ea739a2b6767550`
- **Source tree fingerprint at reviewed head** (`sha256-path-bytes-gitmode-v1`,
  from the reproduced gate manifest): `5390d20c45c400540047bf452e749d7fd866a2ea82365d40ba55fbc04b9439b6`
- **Round:** 1 (independent)

## Entry anomaly (recorded, restored under user authorization)

At entry, `HEAD` matched the pin but the tree was dirty. Four S3 records
(`S3-delta-review.md`, `S3/handoff.md`, `S3/record.json`, `closure-table.md`)
were 0 bytes on disk, and four files were reverted toward `63bd5f8` content:
`tools/verify_local_run.py` and `src/axiomlint/schema.py` lost the remediation,
`governance/registers/findings.json` lost the VERIFIED reconciliation, and
`tests/test_schema.py` lost the two edits to existing tests while keeping the
new ones (a state matching no commit). All anomalies shared mtime 02:08:35,
about 25 s after the `b40f507` commit — the same signature as the entry anomaly
the S3 remediator recorded for the S2 files. Cause unknown; this is the second
occurrence. With the user's authorization the eight files were rewritten from
`HEAD` blobs; the tree was clean before any review action. Committed content
was never affected. Recorded here as `dirty_before: true`.

## Per-task results

1. **Scope — PASS.** `git diff 63bd5f8..b40f507` touches exactly
   `tools/verify_local_run.py`, `src/axiomlint/schema.py`,
   `tests/test_run_verifier.py`, `tests/test_schema.py`,
   `governance/registers/findings.json`, and the four new S3 governance records.
   Nothing else. `governance/registers/deviations.json` untouched.

2. **FIND-S2-001 (D3) — PASS.** `verify_local_run.py:81` adds
   `elif manifest["kind"] == "ACCEPTANCE_CANDIDATE" and skipped != 0`. The
   empty/incomplete/all-skipped check is unchanged. No bypasses found: the
   counts regex requires exactly one `COUNTS` line (`len(counts) != 1` errors),
   the `tests` command is mandatory in `command_inventory` (inventory mismatch
   fails closed), `kind` is a required enum field in `local-run.schema.json`
   (`DEVELOPMENT`/`ACCEPTANCE_CANDIDATE` only), `elif` ordering is correct
   because all-skipped is already an error, and `DEVELOPMENT` behavior is
   intentionally unchanged per the finding. Tests are meaningful:
   `test_acceptance_candidate_zero_skips_passes` asserts `verify() == []`,
   proving the fixture is otherwise valid, so the two rejection tests can only
   pass through the new check for their counts (199/199/5, 2/2/1).

3. **FIND-S2-002 (D4) — PASS, with one NEW finding.**
   `check_schema` enforces co-occurrence via `SCALAR_KEYWORD_TYPES`: `minimum`
   requires `integer`/`number`; `pattern`, `minLength`, `maxLength` require
   `string`. The loop runs after the `type` validity check, so absent or
   non-string `type` values cannot slip through; recursion into `properties`
   and `items` covers nested schemas. The `minLength`/`maxLength` extension is
   acceptable scope — the same bypass class the finding describes ("such as
   'minimum' or 'pattern'"). All 15 published schemas still validate
   (`hygiene` PASS inside the reproduced gate). **`minItems` — and likewise
   `required`, `properties`, `items`, `additionalProperties` — remain
   uncovered**: a reproduced probe shows `validate(7, {"minItems": 3})`,
   `validate("x", {"required": ["a"]})`, `validate(5, {"properties": ...})`,
   `validate("s", {"items": ...})` and `validate(3, {"additionalProperties": false})`
   all pass at the reviewed head. Reported as new finding FIND-S3-001 below.

4. **Existing-test edit — PASS.** `test_invalid_schema_pattern` changed from
   `{"pattern": "["}` to `{"type": "string", "pattern": "["}` (commit `1e13559`).
   This is the only edit to a pre-existing assertion; the rest of the test delta
   is pure addition. The edit preserves intent — without `type: string` the new
   co-occurrence check fires first and the regex compile is never exercised.
   The companion change at `a6403c3` made the untyped-bypass case
   `(5, {"pattern": "^z"})` (not `"text"`), which fails pre-fix for the right
   reason; confirmed at `63bd5f8`.

5. **FIND-S1-001 register reconciliation — PASS.** Status `VERIFIED` with
   `approval_ref` = `governance/audits/WP-001/S2-report.md`. The cited evidence
   supports VERIFIED: S2-report §3.3 records the independent auditor's fresh
   clones at `846b0dc` (`81f219a3…`) and `ff38d38` (`740e7097…`), byte-identical
   across clones, matching the disposition text verbatim. The disposition does
   not overstate — it explicitly says "This is an S2 independent verification
   recorded by the S3 remediator" and keeps DEV-001/DEV-002 OPEN. Using the S2
   report as `approval_ref` is acceptable: VERIFIED requires independent
   verification evidence, and the S2 report is exactly that. Minor observation:
   the reference is an audit report, not a formal approval artifact — acceptable
   here, and the governance validator (`check_wp001_delivery.py`) accepts it.

6. **DEV-001 / DEV-002 — PASS.** `governance/registers/deviations.json` is not
   in the delta; both remain `OPEN` `D2` blocking `G0` with empty
   `approval_ref`. Nothing waived, closed or carried.

7. **Closure-table and handoff accuracy — PASS.**
   - "12 new assertions failed pre-fix": reproduced — 2 verifier failures +
     10 schema subcase failures at `63bd5f8` with HEAD test files.
   - "43 tests across the two modules pass" post-fix: reproduced — 14 + 29,
     all pass at `b40f507`.
   - Gate claims: reproduced — 205/205, 0 skipped, `dirty=False`.
   - Deterministic log digests in `record.json` match my independent runs
     byte-for-byte (delivery `0aaa5e23…`, briefs `a61fe673…`, targeted.stdout
     `83563443…`, verify-gate `8f12cee1…`).
   - Recorded S3 gate `20261021T050657Z-73c94738678f` re-verified internally
     consistent under the new verifier (PASS without `--check-current-source`).
   - Entry-anomaly note confirmed accurate; the four committed S2 files are
     unchanged between `63bd5f8` and `HEAD`, and the same anomaly recurred at
     this review's entry (see above).
   - Commit identities, counts and test names all match reality.

8. **Independence and overclaiming — PASS.** The S3 records consistently
   disclaim independence ("NOT INDEPENDENT"), keep every grant flag false,
   and name independent delta review as PENDING. No claim of closure, G0
   passage, waiver or WP-002 activation exists anywhere in the delta.

## New findings

### FIND-S3-001 (Severity: D4)

- **Title:** Keyword-type co-occurrence check omits composite keywords
  (`minItems`, `items`, `required`, `properties`, `additionalProperties`)
- **Location:** `src/axiomlint/schema.py` (`SCALAR_KEYWORD_TYPES` /
  `check_schema`, lines 19–24 and 110–112)
- **Failure mode:** Same class as FIND-S2-002. `validate()` applies these
  keywords only to values of their matching JSON type (`minItems`/`items` →
  list; `required`/`properties`/`additionalProperties` → dict). An untyped
  schema using them therefore imposes no constraint on other-typed values:
  `validate(7, {"minItems": 3})` passes, as do string/int values against
  `required`, `properties`, `items` and `additionalProperties` schemas.
  Reproduced at the reviewed head in
  `artifacts/wp001-s3-delta-review/residual-gap-probe.log` (5 probe cases, all
  bypass). `minItems` was explicitly disclosed by the remediator as out of
  scope; the composite keywords were not disclosed but are the same class.
- **Impact:** Same as FIND-S2-002 — no current impact; all 15 published schemas
  declare `type`. Future schemas could omit `type` and silently weaken
  constraints.
- **Expected remedy:** In a further S3 round (or valid disposition): extend
  co-occurrence enforcement to map `minItems`/`items` → `array` and
  `required`/`properties`/`additionalProperties` → `object`, with regression
  tests in `tests/test_schema.py`; or obtain an authorized decline with
  reproducible rationale.

## Reproduction summary

All commands run on this laptop from the repository root; raw logs and SHA-256
digests are in `artifacts/wp001-s3-delta-review/` (gitignored) and recorded in
`governance/execution/WP-001/S3/delta-review-record.json`.

| Command | Result |
|---|---|
| `python3 tools/check_wp001_delivery.py` | PASS (`AUTHOR_DELIVERY=PASS criteria=8`) |
| `python3 tools/check_session_briefs.py` | PASS (36 packages, 144 briefs) |
| `python3 tools/run_wp_tests.py WP-001` | PASS (61/61, 0 skipped) |
| `python3 tools/local_check.py --require-clean` | PASS, run `20261021T063000Z-f7a33280e078`, 205/205, 0 skipped |
| `python3 tools/verify_local_run.py artifacts/gates/20261021T063000Z-f7a33280e078 --check-current-source` | `LOCAL_EVIDENCE=PASS; not independent approval` |
| Pre-fix: HEAD test files on `63bd5f8` export (`/tmp/wp001-prefix`) | FAIL as designed: 12 assertions fail for the intended reason |
| Post-fix: same test files at `b40f507` | PASS (43/43 across the two modules) |

The independent delta review **confirms the FIND-S2-001 and FIND-S2-002
remediations are correct and correctly evidenced**. This review grants no
package closure, no G0 passage, no S3 exit, no S4 activation, no waiver and no
WP-002 activation.

## Verdict

**FINDINGS-OPEN** — the reviewed delta is faithful to the S2 findings and
cleanly evidenced, but new finding FIND-S3-001 (D4) is an unresolved defect of
the same class and is reported for another S3 remediation round.
