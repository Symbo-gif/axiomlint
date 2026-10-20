# Foundation architecture

```text
Maintainer-approved contracts and task scope
    |
Nonexecuting local intake (trusted small files only)
    |
Explicit capability registry (all analyzers/backends unavailable)
    |
Future candidate -> SpecIR -> verifier -> independent replay
    |
Future finding fusion -> bounded report

Foundation governance + schema subset + artifact store
    |
Local engineering checks -> raw logs + exact tree manifest
    |
Independent S2 -> S3 -> S4 approval (not yet performed)
```

The installed CLI is not required: `PYTHONPATH=src python3 -m axiomlint` works
without package downloads. Schemas and governance are repository assets;
the distributable-package resource layout is deferred to WP-004/WP-005.

Trust boundaries: subject code is data, candidate reviewers advisory, verifier
outputs require replay, correspondence is separately reviewed, logs are not
approvals. No runtime plugin loading, arbitrary shell-config execution or
automatic evidence promotion is provided.

Future modules use data-only request/result contracts and explicit unavailable,
unknown/error/timeout states. Prefer immutable records, small pure transformations,
and adapter-specific exit semantics. Do not build a monolithic analyzer.

