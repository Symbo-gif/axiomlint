# Local verification standard

Default tests execute on the user's laptop only. No hosted CI, automated
remote scan, network API, container pull, dependency resolver, model server,
or solver invocation is part of the foundation gate.

## Mandatory development checks

`python3 tools/local_check.py` runs governance consistency, repository hygiene,
compile-only source syntax checking, and standard-library unittest discovery.
Every command must run, all return codes must pass, and the test suite must
discover at least one test. Tests must not all be skipped. Capture stdout/stderr
and digest them; preserve failed run manifests as well as successes.
Use a sanitized child environment and run from the repository root.

Positive, negative, corruption, malformed input, disabled capability, path,
duplicate-key, schema-escape, dirty-state and governance-state cases belong in
the foundation suite. No numerical coverage percentage is claimed without a
coverage tool and recorded numerator/denominator.

The source fingerprint includes untracked nonignored files and paths using
Git's NUL-delimited listing. Refuse symlinks. Bind outputs to commit plus exact
tree digest and dirty state. Recheck source identity after commands; mutation
during the run fails the gate. Development runs can be dirty. A successful
development run does not pass acceptance.

## Acceptance and independent replay

Only after AMD-001 ratification, use `--require-clean` in a clean local checkout
at the exact acceptance revision. The same local command is reusable, but must
gain all future package-specific checks before those packages close.
Reviewer must inspect command inventory and deferred validation register.
Do not report a default stdlib-only gate as Ruff, mypy, coverage, SCA, SBOM,
signature, Nix, OCI or security-isolation validation.

Independent S2 is not provided by running the author's tests twice. It needs a
separate context, read-only source and a committed finding/verdict report.
Formal closure additionally needs requirement evidence, approvals and findings
verified, not merely a schema-valid CLOSED string.

## Explicit deferrals

Full JSON Schema engine, official SARIF schema, Linux fresh-checkout replay,
Windows checks, package build/install, locked dependency environment, Nix/OCI,
format/lint/type/coverage, secrets/SCA/SBOM/signing, hostile-runner probes and
all backend conformance remain tracked future work. Unavailable checks are
DEFERRED, never silently counted as passing.

