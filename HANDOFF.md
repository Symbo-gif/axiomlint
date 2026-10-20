# AxiomLint Foundation Handoff

Built on the laptop at `/home/themichael/PerplexityWorkspace/axiomlint`.
This is an implemented, locally tested governance and engineering foundation,
not a completed code-review system, formal assurance stack or closed phase gate.
No hosted CI was configured or run, no software installed, and nothing pushed
or published.

## What is ready

- **Governance:** charter and authority hierarchy, explicit local-only amendment,
  S1-S4 lifecycle, independent audit rules, finding/deviation controls,
  experiment preregistration, evidence vocabulary, privacy and licensing policy.
- **Planning:** all 36 original work packages preserved as declarations; WP-001
  alone active, later packages planned and unapproved; 16 seed requirements,
  13 register files and eight operational templates.
- **Runnable foundation:** CLI/status, conservative static inventory, closed
  schema vocabulary, semantic governance checks, content-addressed artifact store,
  source-bound local gate and a separate raw-log verifier.
- **Scaffolding:** intake, runner, adapters, SpecIR, fusion, reporting,
  Hypothesis/CrossHair/Z3/cvc5/SymPy/Sage/Lean/LLM boundaries, Lean proof layout,
  FOSS-rule directories and separate benchmark corpus/harness/scorer/analysis.
- **Safety defaults:** no subject execution or backend invocation; no LLM,
  automatic repairs, telemetry, remote scan or required network dependency.

The original plan is copied unchanged under `docs/reference/axiomlint-plan.md`;
its SHA-256 and the upstream governance revision are pinned in configuration.
Project documents adapt, rather than silently vendor or claim complete
conformance with, the
[reference governance framework](https://github.com/Symbo-gif/Methodology-Workflow-Governance/tree/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a).

## Actual local verification

| Check | Recorded result |
|---|---|
| Governance structure/cross-references | PASS |
| No-hosted-config and Markdown/schema hygiene | PASS |
| Compile-only syntax checks | PASS, 24 Python source files |
| Unit/negative/integrity suite | PASS, 106 executed, zero failures/skips |
| Clean local checkout gate | PASS |
| Fresh local clone gate | PASS, same 106 tests |
| Manifest, schema snapshot and raw-log verification | PASS for both corrected clean runs |
| Main versus fresh-clone source identity | Same Git commit and source fingerprint |
| Independent S2, charter ratification, phase closure | NOT PERFORMED / NOT APPROVED |

Recorded implementation baseline:
`fe3be9da8f7b8ada431b4656ea8e9e1b7ab055c4`.
Main and replay source SHA-256:
`3f53236db91b6615c4aec6eaea47ca75fd55f6810bef5c277f316c88106f901a`.
The documentation/evidence handoff is committed afterward and receives another
full local check; its exact current commit and latest run directory are available
from `git log -1` and `artifacts/final-console.log`.

Environment actually exercised: Python 3.12.3, Git 2.43.0, Linux
7.1.5-76070105-generic, x86_64, glibc 2.39. Main and replay used the same laptop
and author context; this is not independent hardware/environment reproduction.
Raw runs and correction history are retained under
`governance/evidence/s1-author-verification/`.

## A discrepancy found and corrected

The first fresh clone passed its tests but had a different source fingerprint:
identical files had ordinary 0664 permissions versus the transferred files'
0644. The original fingerprint used all permission bits.
The implementation now hashes paths, bytes and Git's executable bit, with
explicit algorithm identification and local-run schema 0.2. Regression tests
cover permission invariance and executable-bit changes. Corrected main and clone
fingerprints match. Earlier runs are retained and are not called reproducibility
acceptance; independent review of FIND-S1-001 is still pending.

One subsequent handoff run failed a negative-test fixture after the real S1
commit was recorded. The test now explicitly removes required commit/report
fields instead of depending on empty live metadata; its validation assertions
were strengthened. That failed run is also retained rather than discarded.

## Local-only governance decision

Your prohibition on hosted checks is effective immediately. AMD-001 proposes a
clean-checkout, exact-revision local acceptance procedure with raw logs,
independent replay and human approval, instead of hosted CI.

This is an explicit override: upstream tailoring says authoritative CI remains
mandatory, while its CI standard permits a charter-named alternative
([tailoring](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/tailoring.md),
[CI standard](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/standards/ci-cd-and-branch-protection.md)).
DEV-001 records drafting/scaffolding before formal charter ratification;
DEV-002 records this tailoring conflict. Neither was silently waived.

The current request authorized construction, not an invented signature on
unseen documents. Charter, amendment, formal scope and risk acceptance remain
pending. S1 implementation exists, but its formal adoption remains open;
S2-S4 and G0-G8 are not marked complete.

## Important limits

- **No operational analyzers:** solver/CAS/proof/LLM adapters are unavailable,
  not successful empty scans; inventory emits NOT_REVIEWED.
- **No hostile-code sandbox:** AST inventory is only for small trusted local
  inputs. No imports/evaluation occur, but byte limits are not a general parser
  resource-security guarantee.
- **No full runtime schema set:** seven foundation schemas exist; the validator
  supports only its declared closed vocabulary, not complete Draft 2020-12.
  Runtime model/proof/CAS/correspondence and SARIF schemas remain future work.
- **No authenticated immutability:** create-exclusive writes and SHA-256 detect
  corruption, but a same-user attacker can rewrite the host and manifests.
  No signing, SLSA level or supply-chain certification is claimed.
- **No benchmark conclusions:** no corpus accepted, labels adjudicated, thresholds
  chosen or experiment run. EXP-E0-E6 is separated from EV-E0-E6 terminology.
- **No fake reproducible environment:** real Nix/OCI/lockfiles and packaging
  verification are deferred. Design `.in` files are not advertised as runnable.
- **No inflated gate coverage:** Ruff, mypy, pytest/coverage, SCA/SBOM/secrets,
  Nix/OCI, Windows and all formal-backend conformance remain explicitly deferred.

The schema/evidence, security and provenance decisions were checked against
[JSON Schema](https://json-schema.org/draft/2020-12/json-schema-core),
[Python AST documentation](https://docs.python.org/3/library/ast.html),
[NIST SSDF](https://csrc.nist.gov/projects/ssdf) and
[versioned SLSA guidance](https://slsa.dev/spec/v1.1/levels).
The research document records source details, current/draft distinctions and gaps.

## Use the foundation

```sh
cd /home/themichael/PerplexityWorkspace/axiomlint
python3 tools/local_check.py
PYTHONPATH=src python3 -m axiomlint status
PYTHONPATH=src python3 -m axiomlint governance check --root .
PYTHONPATH=src python3 -m axiomlint inventory examples/absolute.py
python3 tools/local_check.py --require-clean
python3 tools/verify_local_run.py artifacts/gates/RUN-ID --check-current-source
```

No package install is needed. Replace RUN-ID with the run directory printed
by the local gate. The intentionally defective example is just inventory input;
its successful parse must never be mistaken for a clean review.

## Legitimate next actions

Review and ratify or amend the charter, AMD-001 and bootstrap scope deviation;
complete the formal S1 handoff; then use a different human or agent context for
read-only S2. A complete prompt is at `docs/user-guide/S2-AUDIT-PROMPT.md`.
Use S3 for findings only and S4 for real closure. Activate WP-002 only after
WP-001 actually closes; do not jump to backend implementations or benchmarks.
