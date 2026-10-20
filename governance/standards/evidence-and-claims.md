# Evidence, claims and record standard

The evidence ladder is a vocabulary, not an implemented promotion engine.

| Label | Necessary record | Permitted interpretation |
|---|---|---|
| EV-E0 | Candidate with provenance | Suspected, unverified |
| EV-E1 | Successful reproducible static analyzer run | Tool detected |
| EV-E2 | Saved input, executable oracle and concrete failing replay | Reproduced failure under recorded environment |
| EV-E3 | SMT-LIB/model, logic, assumptions, solver/version/status and replay | Result under this SMT model |
| EV-E4 | Exact symbolic query/result, domain, backend/version and replay | Symbolically established under explicit assumptions |
| EV-E5 | Theorem/axioms/imports, pinned Lean dependencies and clean kernel replay | Proved about this formal model |
| EV-E6 | EV-E5 plus independently reviewed source correspondence and two approvals | Established for this fragment within declared semantics |

These are not a total ranking of truth. A valid theorem about an irrelevant model
does not erase a source counterexample. Evidence does not imply severity or
calibrated probability. Candidates cannot self-assign accepted levels. The
foundation emits no EV-E1 through EV-E6 claims and no calibrated confidence.

## Required future runtime contract

Run: source Git revision and exact content digests, dirty state, reviewed diff,
task/spec IDs, OS/architecture/hardware and limits, runtime/tool versions,
dependency lock, allowlisted environment, seeds and command inventory.
Invocation: argv, exit and signal, wall/CPU time, peak memory, stdout/stderr
digests and byte sizes, timeout/resource reason and actual enforcement probes.
Finding: ID, location/taxonomy, failure/impact/remedy, severity separate from
confidence, assumptions, limitations, evidence and reproduction.
Evidence: candidate/corroboration/contradiction/remediation/closure links,
artifact sizes/digests, replay identity, TCB subset and correspondence status.

WP-005 must define the complete runtime schemas before any analyzer is enabled.
Current schemas are narrower foundation/governance/local-gate contracts; they
are not full proof, model, CAS, benchmark or SARIF schemas.

## Fail-closed interpretations

UNKNOWN, TIMEOUT, UNSUPPORTED, ERROR, CONFLICT, FAILED and NOT_RUN remain
first-class states. An empty successful scan can mean NO_FINDING only within
its configured scope; a failed, partial or nonexistent scan cannot.
SMT UNSAT is not Python correctness. Real algebra is not IEEE arithmetic.
Kernel acceptance does not validate a translation or a specification.
Generated tests whose oracle shares the claim generator are not independent.

## Serialization and retention

Native foundation JSON: UTF-8, sorted keys, compact separators, trailing LF,
no NaN/Infinity; duplicate object keys rejected. This is project canonicalization,
not a claim of RFC 8785 conformance. SHA-256 identifies bytes, not authenticity.
Artifact store writes use create-exclusive and verify preexisting content;
missing/corrupt/symlink artifacts fail closed. The API is append-only, but a
same-user attacker can change the directory or files. Store parent is trusted;
concurrent malicious filesystem mutation and partial-write crash recovery are
not solved. Quarantine partial/corrupt entries; never auto-overwrite them.

SARIF is future interchange, not the authoritative proof graph. Its
`executionSuccessful` and tool-execution notifications must preserve failed
execution separately from findings, as specified in
[SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html).

