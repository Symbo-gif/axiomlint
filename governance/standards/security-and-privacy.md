# Safety, privacy, licensing and dependency standard

## Default posture

No subject-code execution, no model calls, no telemetry, no inherited credentials,
no remote checks, no dependency installation during tests. The local test gate
executes repository-maintainer test code, not arbitrary review targets; these are
different trust domains. A test runner is not a safe hostile-code runner.

The AST inventory accepts small maintainer-controlled regular UTF-8 files,
rejects final symlinks and oversized inputs, never imports or executes source,
and reports NOT_REVIEWED. It is not a purity verifier, PyRS classifier, or
hostile-input sandbox. Byte limits do not guarantee resistance to parser
stack/CPU/memory exhaustion; Python documents these limitations for AST processing
([Python AST documentation](https://docs.python.org/3/library/ast.html)).

## Future safe-runner entry criteria

Before enabling any dynamic adapter: approved WP-006, independent threat-model
review, rootless nonprivileged isolation, no network, read-only source,
private bounded scratch, dropped capabilities, no-new-privileges, deterministic
locale/timezone, credential-free allowlisted environment, CPU/wall/memory/PID/
output/file-size limits, process-group cleanup, syscall policy, mount and
symlink/traversal protection, and executable probes proving each control.
Unavailable kernel/cgroup/runtime controls must cause refusal, not best-effort
assurance. A Containerfile alone proves none of this. Hostile escape/fork-bomb
tests run only inside independently inspected containment, not naked on the laptop.

Podman documents these controls and rootless/cgroup limitations; their
availability is platform-dependent, not automatic
([Podman run reference](https://docs.podman.io/en/latest/markdown/podman-run.1.html)).

## Supply chain and licensing

Mandatory dependencies and fetched rules must have exact version/source digest,
OSI-compatible license, transitive inventory, vulnerability review and approved
update procedure. Default stack is stdlib-only. Build metadata's setuptools
requirement is not pinned; packaging is therefore deferred and not exercised.
Do not run pip install, uv sync, Nix or an OCI build as part of default checks.
Adding a dependency requires a declared package, license review and local lock.

Semgrep registry rules are not assumed FOSS. CodeQL or Wolfram engines cannot be
mandatory. Model weights and dataset redistribution rights need separate review.
Record generated-artifact licenses; exclude credentials and restricted source
from public history. The source document and research references are not a
blanket license grant for external material.

## Incident and exception controls

Stop affected capability on evidence tampering, secret exposure, sandbox escape,
misleading assurance or benchmark leakage. Preserve restricted raw evidence
locally; share only a redacted derivative. Record incident, owner, risk, finding,
fix, regression, independent verification and invalidated downstream claims.
Waivers need owner, scope, reason, approval, expiry and compensating controls.
No waiver authorizes fabricated evidence, D1/D2 closure or secret publication.

