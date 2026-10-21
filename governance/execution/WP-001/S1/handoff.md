# WP-001 S1 author delivery and separate-context handoff

Status: AUTHOR DELIVERY, not independent readiness approval or S2.
Formal S1 remains IN_PROGRESS until its lawful separate-context exit decision.
The principal's actual instruction to finish these artifacts is APR-002;
constitution ratification is already complete under APR-001.

## Scope and acceptance

Read `record.json` for the eight original acceptance clauses and their exact
artifact/verification map. `artifacts.json` records source-file bytes, including
the new glossary, license/material-adoption policy, amendment/exception procedure,
scope reconciliation and author execution/handoff controls.

Mutable live registers/status are checked by the governance validator and
captured in full by the final Git source pin, not frozen forever by the
artifact-byte subset. A later lawful readiness/session update is not itself
tampering. The author record's pending/unperformed labels describe this
source snapshot; actual later progress belongs in its own records.

The current increment adds no analyzer, backend, sandbox, benchmark, model call
or release. Prior bootstrap implementation is disclosed, not converted into
accepted later work packages. All original scope/non-goals and the 144
versioned planning briefs remain preserved.

## Obtain the actual review target

Use `artifacts/wp001-s1/AUDIT-TARGET.json`, generated only after the final author
commit and matching clean main/fresh-clone runs. It contains the real source
commit/fingerprint, raw gate identities, manifest digests, handoff manifest
digest and honest author-only status. Do not audit the entry head, old fe3be9d
milestone, uncommitted tree or a convenient newer head instead.

The tracked author record cannot contain its own unknown future commit hash.
The ignored, source-bound pin receipt avoids that self-reference; verify it
against Git and actual source rather than trusting the author's summary.
Copy it to controlled audit evidence before any later mutable artifact cleanup.

## Commands and actual evidence

```sh
python3 tools/check_wp001_delivery.py
python3 tools/check_session_briefs.py
python3 tools/run_wp_tests.py WP-001
python3 tools/local_check.py --require-clean
python3 tools/verify_local_run.py artifacts/gates/RUN-ID --check-current-source
```

Use the real printed run ID. The pin receipt and raw logs, not a prefilled
test-count sentence here, record actual final outcomes. The targeted runner
refuses empty/all-skipped suites. The complete gate remains narrower than
unimplemented Ruff/mypy/coverage/SCA/SBOM/Nix/OCI/Windows/formal-backend checks.

## Required independent preflight before accepted S2

The next actor must be a genuinely separate human or agent context, disclose
their identity and delegation basis, read the actual contract/constitution
before the diff, and assess scope, acceptance evidence and readiness.

Do not silently approve the author's readiness. Inspect APR-002's actual scope,
DEV-001/DEV-002, FIND-S1-001, inherited risk/assumption decisions and the
readiness/D2 ambiguity in `scope-reconciliation.md`. If the applicable rules
do not permit S1 exit/audit entry, record BLOCKED with exact clauses and seek
the required authorized resolution. That preflight is not a fabricated S2.

If lawful, record the separate-context readiness decision bound to the actual
pin, update live S1 exit honestly with its distinct commit, and separately
verify any metadata-only head. Start accepted S2 only after those prerequisites.
Do not reuse earlier logs as coverage for later metadata or invent a self hash.
Keep implementation snapshot and later entry/approval metadata identities distinct.

## S2 scope once entry is legitimately authorized

Use the full prompt at `docs/user-guide/S2-AUDIT-PROMPT.md`.
Examine constitutional acceptance first, then the whole disclosed foundation
and its trusted governance/evidence utilities for misleading claims or boundary
defects. Prior author tests and this acceptance map are audit inputs, not verdicts.

Source, schemas, tests and contract are read-only. Logs and audit reports go
to separate writable locations, and the S2 report/finding set receives its own
commit. No actual S2 actor/verdict is prepopulated here.

Every actionable finding needs ID, D1-D4, clause, file/location, failure mode,
impact, reproduction/reasoning and expected correction. Retain all failures
and limitations. Any D1 forces FAIL. Do not fix product code during S2,
waive D1/D2, accept material risks, leak holdouts, execute hostile subjects,
call remote models, install software, push or configure hosted checks.

S3 then fixes only actual findings with independent delta review; even zero
findings requires no-change verification. S4 and package closure remain later.
WP-002 cannot activate merely because this handoff exists.
