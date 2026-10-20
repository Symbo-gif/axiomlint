# Session-brief design and source verification

Research date: 2026-10-20. The deliverable is planning: 36 packages multiplied
by four stages, not execution, approval or package acceptance.
Normative prescriptions in the briefs are proposed project design choices;
external technical facts and upstream requirements are cited below.

## Upstream contract preserved

The source method requires approved S1 entry, independent read-only S2,
finding-only S3 with a no-change path, separate records/commits, and closed
S4 before the next S1
([pinned session cycle](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/work-package-session-cycle.md)).
Its brief template requires authority, entry gates, scope/non-goals, actions,
artifacts, verification commands, stop conditions, exit gates and handoff
([pinned session template](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/templates/session-brief.md)).
Design choice: every individual brief contains these sections and tailored
implementation, audit, remediation and closure prescriptions instead of merely
referring to a generic four-stage template.

The experimental method requires independent E2 before E3 execution, frozen
rules and retained unfavorable results, but does not itself specify how to
nest seven experiment checkpoints in four engineering sessions
([pinned experiment cycle](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/methodologies/experiment-cycle.md)).
Design choice: document that nesting explicitly; S2 after execution cannot
substitute for pre-execution EXP-E2.

The benchmark standard requires predeclared workload, uncertainty, timeouts and
outlier policy, immutable identities and retained raw negative/null observations
([pinned benchmark standard](https://github.com/Symbo-gif/Methodology-Workflow-Governance/blob/d8d1d0d513bef6484cef587fc58ca3fa16fb4f2a/standards/benchmarking-and-reproducibility.md)).
Design choice: campaign S3 cannot change frozen thresholds or use favorable retries.

## Technical details affecting package-specific acceptance

- **Hypothesis replay:** saved databases are caches; failure blobs have no
  cross-version compatibility guarantee and explicit examples provide durable
  concrete-input replay
  ([Hypothesis API](https://hypothesis.readthedocs.io/en/latest/reference/api.html)).
  WP-011 therefore requires saved concrete inputs and independent oracle identity,
  not seed-only or database-only reproduction.
- **CrossHair containment:** CrossHair executes contracted code, its side-effect
  protections are imperfect, and its no-counterexample exit is not a proof
  ([CrossHair contracts](https://crosshair.readthedocs.io/en/latest/contracts.html)).
  WP-012 therefore requires accepted external containment and concrete replay.
- **SMT status:** Z3 distinguishes satisfiable, unsatisfiable and unknown results
  over asserted formulas
  ([Z3 Python guide](https://microsoft.github.io/z3guide/programming/Z3%20Python%20-%20Readonly/Introduction/)).
  WP-013 through WP-015 separate translation, query status, model decoding,
  source replay and backend disagreement.
- **CAS domains:** SymPy's assumptions can be True, False or None, and identities
  such as square-root simplification depend on declared domains
  ([SymPy assumptions](https://docs.sympy.org/latest/guides/assumptions.html)).
  WP-016 through WP-018 preserve unknowns, singularities, branches and the
  exact-real/IEEE distinction rather than unconditional equivalence.
- **Lean trust:** transitive `#print axioms` reveals `sorryAx` and other
  assumptions; current native evaluation introduces dedicated axioms relying
  on the compiler, not only the kernel
  ([Lean axiom reference](https://lean-lang.org/doc/reference/latest/Axioms/)).
  WP-019 and WP-021 therefore inspect actual pinned axiom closure and reject
  unexpected native/custom assumptions for the proposed kernel-only baseline;
  a historical hardcoded blacklist is not sufficient.
- **SARIF failures:** executionSuccessful and error notifications distinguish
  failed/incomplete runs from complete empty result sets
  ([SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html)).
  WP-008/WP-009/WP-035 preserve that distinction.
- **Runtime controls:** rootless resource controls depend on actual cgroup/
  platform support and read-only roots can still have writable mounts
  ([Podman run](https://docs.podman.io/en/latest/markdown/podman-run.1.html)).
  WP-006 requires actual enforcement probes and refuses unsupported controls.
- **Schema claims:** dialects have declared required vocabularies; implementing
  a subset is not automatically full support for a dialect
  ([JSON Schema core](https://json-schema.org/draft/2020-12/json-schema-core)).
  WP-005 retains explicit subset/full-validator boundaries.
- **Supply-chain claims:** SLSA v1.1 separates unsigned provenance, hosted signed
  provenance and stronger isolated-build requirements
  ([versioned SLSA levels](https://slsa.dev/spec/v1.1/levels)).
  WP-034/WP-036 cannot label local hashes or replay as hosted-build assurance.
- **SSDF status:** NIST lists SSDF 1.1 as final, while the October 2026
  publication listing identifies 1.2 revision 1 as draft
  ([NIST SSDF](https://csrc.nist.gov/projects/ssdf),
  [NIST publication listing](https://csrc.nist.gov/publications/sp800)).
  WP-002 distinguishes final baseline guidance from draft mappings.

## Limits and unresolved decisions

References under latest URLs are contextual research, not pinned executable
materials. Actual tool/build/schema versions, licenses, APIs and command syntax
must be rechecked and pinned during each authorized S1; no future version or
capability is fabricated in a brief. No backend, dataset, statistical campaign,
hostile sandbox or release was executed for this planning task.

Original acceptance clauses remain visible in each brief and declaration.
Hosted-check language is explicitly overridden by the user's local-only
constraint and proposed AMD-001; ratification is still needed for authoritative
closure. The calibration/corpus order, provisioning, external comparison and
publication decisions are explicit blockers, not silent scope changes.

