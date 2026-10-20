# Local development and handoff

Run commands from the laptop project root. No install is needed.

```sh
python3 tools/local_check.py
python3 tools/verify_local_run.py artifacts/gates/RUN-ID --check-current-source
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m axiomlint status
PYTHONPATH=src python3 -m axiomlint inventory examples/absolute.py
PYTHONPATH=src python3 -m axiomlint governance check --root .
```

`inventory` is static metadata, not a defect detector. The deliberately faulty
example must not receive a NO_FINDING or proof claim merely because parsing works.

CLI exits: 0 means the selected operation completed (structural validity or
inventory only), 1 means governance/test check failure, 2 means usage/data error
or inventory parse diagnostics. No exit code means correctness.

Gate runs use unique directories under artifacts/gates. Each has a manifest and
raw per-command logs with digests. A failed run is retained. Avoid reusing a run
directory. Run with `--require-clean` only after committing source; it refuses a
dirty/unversioned tree and is still not an independent approval.

Do not use a shell pipe that hides the command's exit status. If displaying logs
with tee, use `set -o pipefail`. Source-tree fingerprints exclude Git-ignored
artifacts but include untracked nonignored files and file names. Credentials
and the complete host environment are never captured.

The verifier checks manifest/schema, raw log digests/sizes, exact command
inventory, exit/status consistency and nonempty test counts. With
`--check-current-source`, it also compares the current Git/source-tree identity.
It is a separate byte-integrity check, not a different reviewer or authenticated
signature. Historical evidence can be checked without current-source matching.

## Independent review

Hand the reviewer the S1 commit, full package contract, requirements, raw gate
directory and limitations. Reviewer starts a new context, reads actual contracts
and source, reproduces checks, records examined scope, then commits an S2 audit
report. This authoring session must not invent that review.

## Environment portability

Implemented/tested environment is to be recorded from actual laptop runs.
Windows support, fresh Linux checkout, locked environments, Nix/OCI and package
installation are deferred. The optional pre-commit configuration uses a local
hook but is not installed. No hosted workflow is present.
