# AxiomLint: Governance-Driven Plan for Evidence-Carrying Code Review

## Executive decision

**Project name: AxiomLint.** The name combines *axiom* (explicit assumptions and formally checkable claims) with *lint* (practical code review), and a GitHub repository-name search found no obvious exact-name collision at the time of research.

AxiomLint should be built as a **local-first, free/open-source evidence-carrying review orchestrator**, not as another monolithic analyzer. Its job is to normalize candidate findings from conventional review tools and LLM reviewers, escalate tractable claims to property testing, symbolic execution, SMT, computer algebra, or theorem proving, independently replay the evidence, and emit a bounded verdict that never overstates what was established.

The initial milestone is deliberately narrow: **auditing small, deterministic, typed Python functions and compact patches** under documented assumptions. Code generation, automatic patching, repair, repository-scale interprocedural analysis, and multi-language support are later campaigns and are non-goals for this plan.

## Governing profile

Adopt the repository's **Research profile** as the default and apply **High-assurance controls** to evidence validation, execution isolation, releases, and benchmark acceptance. The governance framework says tailoring may change cost but not declaration, evidence, audit, finding closure, or authoritative CI; its Research profile adds E0-E6 preregistration and permanent evidence, while High Assurance adds threat modelling, formal checks, independent review, and tamper-evident retention.

Every implementation work package follows S1 implementation, S2 independent read-only audit, S3 finding-only remediation, and S4 documentation/closure. Sessions may not be skipped, merged, or reordered; each must have a distinct state record and commit. Benchmark packages additionally follow E0 authorization through E6 synthesis, freezing hypotheses and analysis rules before execution and preserving unexpected, negative, null, and inconclusive outcomes.

## Product claims

AxiomLint may eventually claim only the following, each with explicit scope:

- **Finding claim:** a potential defect was detected with source location, failure mode, impact, evidence, and remedy.
- **Counterexample claim:** a concrete input violates a stated executable property under a pinned implementation and environment.
- **SMT claim:** a formula was satisfiable, unsatisfiable, or unknown under a declared logical model.
- **CAS claim:** a symbolic identity, simplification, exact result, or domain condition was obtained by a pinned computer-algebra backend.
- **Lean claim:** a theorem formalizing a declared model was accepted by the pinned Lean kernel without prohibited trust escapes.
- **Correspondence claim:** a separately reviewed translation connects a source fragment and formal model within an explicitly bounded semantic subset.
- **Review verdict:** findings are deduplicated and prioritized; `NO_FINDING` means only that configured checks found nothing, never that the program is correct.

The governance standard explicitly rejects authority by assertion and requires findings to be reproduced where feasible. Lean is appropriate for the highest evidence tier because it combines automated methods with fully specified axiomatic proofs, is open source under Apache 2.0, and checks formal claims within its proof framework.[^1]

## Authority hierarchy

Use this project-specific precedence:

1. Approved charter and amendments.
2. Normative AxiomLint safety, evidence, and benchmark standards.
3. Approved work-package and experiment declarations.
4. Versioned specifications and semantic-subset definitions.
5. Session briefs and implementation recipes.
6. Raw evidence, reports, logs, and generated artifacts.
7. LLM prompts, agent instructions, and model-generated explanations.

Conflicts fail closed. Baselines identify owner, scope, version or commit, approval, and replacement rules; performance thresholds, hypotheses, seeds, denominators, and analysis methods cannot be changed after affected execution begins. This applies the source framework's authority and baseline-control model directly to AxiomLint.

## System architecture

```text
Repository / patch / task contract
              |
       Intake and sandbox
              |
   Deterministic baseline analyzers
              |
 LLM candidate reviewer(s), untrusted
              |
 Finding normalizer + specification IR
       /          |           \
Property/Symbolic SMT/CAS     Lean proof
       \          |           /
     Evidence validation and replay
              |
 Deduplication, ranking, bounded verdict
              |
 SARIF + JSON + Markdown + provenance
```

### Core modules

| Module | Responsibility | Trust position |
|---|---|---|
| Intake | Pin source SHA, parse task contract, classify language/subset, copy into isolated workspace | Trusted boundary |
| Baseline adapters | Run lint, type, test, SAST, secret, dependency, and license checks | Tool outputs require validation |
| Candidate reviewer | Produce structured hypotheses, properties, and suspected findings | Untrusted/advisory |
| SpecIR | Typed intermediate representation for inputs, assumptions, invariants, postconditions, integer/real/float semantics, exceptions, and correspondence metadata | Security-critical |
| Z3 backend | Generate solver obligations and countermodels | Evidence-producing, not self-authorizing |
| CAS backend | Exact algebra, domain analysis, symbolic equivalence, limits, recurrence and combinatorial checks | Evidence-producing |
| Lean backend | Generate/check theorem statements and proofs for selected claims | Highest formal tier for model claims |
| Replay validator | Re-run tests, models, CAS queries, and proofs from clean artifacts | Trusted gate |
| Finding fusion | Normalize, deduplicate, relate corroborating/contradictory evidence, calibrate severity/confidence | Security-critical |
| Reporter | Emit JSON, SARIF, Markdown, manifests, digests, and reproduction commands | Must be deterministic |
| Benchmark harness | Randomize/counterbalance runs, enforce budgets, preserve raw output, score blinded results | Independent from product logic |

Use SARIF 2.1.0 as an interoperability output because it is an OASIS standard specifically designed to capture and exchange static-analysis results.[^2][^3] Retain a richer native JSON evidence schema because SARIF alone cannot encode the full proof/model/correspondence chain.

## Evidence model

### Evidence ladder

| Level | Label | Minimum evidence | Permitted wording |
|---|---|---|---|
| E0 | Hypothesis | LLM or heuristic explanation | “Suspected” |
| E1 | Static corroboration | Reproducible analyzer result | “Tool detected” |
| E2 | Dynamic counterexample | Failing regression/property test with minimized input | “Reproduced failure” |
| E3 | Solver result | Formula, assumptions, solver/version, model or UNSAT result, timeout status | “Under this SMT model” |
| E4 | Symbolic result | Exact expression, assumptions/domain, backend/version, replay | “Symbolically established under assumptions” |
| E5 | Kernel-checked theorem | Lean source, dependency lock, no prohibited declarations, clean replay | “Proved about this formal model” |
| E6 | Source-linked assurance | E5 plus reviewed translation/correspondence evidence for supported subset | “Established for this source fragment within the declared semantics” |

No evidence level automatically upgrades another. Solver `unknown`, timeout, unsupported syntax, translation failure, inconsistent CAS outcomes, and unproved Lean goals are first-class results and cannot be rewritten as success.

### Required record fields

Each run records:

- Run ID, source SHA, dirty-state check, task/specification ID, and reviewed diff.
- OS, architecture, CPU/GPU, memory limits, runtime/compiler, tool versions, dependency lock, environment allowlist, and seeds.
- Adapter command, exit code, wall and CPU time, peak memory, stdout/stderr digests, and timeout reason.
- Finding ID, location, taxonomy, severity, confidence, evidence level, assumptions, limitations, and reproduction command.
- Parent/child links among candidate, corroboration, contradiction, remediation, and closure records.
- Artifact sizes and cryptographic digests.

This directly implements the governance repository's reproducibility standard, which requires revision, environment, hardware, seeds, corpus identity, command, artifact manifest, workload protocol, uncertainty, timeout, and preserved raw observations.

## Free/open-source stack

### Required foundation

| Capability | Primary component | Role and rationale |
|---|---|---|
| Orchestration | Python 3, Typer/Click, Pydantic, asyncio/subprocess | Fastest route to adapters and typed records |
| Parsing | Python `ast`, LibCST | Semantic inspection plus source-preserving locations |
| Lint/format | Ruff | Deterministic baseline hygiene |
| Types | mypy and/or Pyright OSS | Type-contract defects and narrowing |
| Tests | pytest, coverage.py | Executable regressions and baseline correctness |
| Property testing | Hypothesis | Searches stated input domains for edge cases; its purpose is property-based testing rather than proof.[^4][^5] |
| Symbolic execution | CrossHair | Calls typed Python functions with symbolic inputs and uses SMT to seek counterexamples.[^6] |
| SMT | Z3 | Primary solver; MIT licensed, with Python bindings and broad verification use.[^7][^8] |
| SMT diversity | cvc5, later Bitwuzla | Independent cross-checks; cvc5 is BSD-licensed and broad-theory, Bitwuzla is MIT-licensed and strong for bit-vectors/floating point.[^9][^10] |
| Proof | Lean 4, Lake, mathlib | Kernel-checked formal claims; Apache 2.0 ecosystem.[^1] |
| CAS | SymPy | Default exact symbolic backend, pure Python and BSD licensed.[^11][^12] |
| Extended CAS | SageMath/Maxima, optional isolated adapter | Wider open mathematics capability; Sage integrates many FOSS packages under GPL and provides a Python-based interface.[^13][^14] |
| SAST | Bandit; Semgrep CE with only OSI-compatible/self-authored rules | Security patterns; the Semgrep engine is LGPL, but rule licensing must be verified rather than assumed.[^15][^16] |
| Secrets | Gitleaks CLI | Local scanning of source and history for credentials.[^17][^18] |
| SBOM/SCA | Syft + Grype or Trivy | SPDX/CycloneDX inventory and vulnerability/license scans.[^19][^20][^21] |
| Results | SARIF 2.1.0 + native JSON Schema | Interchange plus richer evidence model.[^2] |
| Reproducibility | Nix flake plus OCI image; ReproZip optional for campaigns | Declarative pinned environments, isolated builds, and portable experiment capture.[^22][^23][^24] |
| Provenance | in-toto/SLSA attestations, Sigstore Cosign | Link outputs to builder, recipe, source, and materials.[^25][^26] |
| Repository posture | OpenSSF Scorecard | Supply-chain practice feedback; it evaluates automated security heuristics, not code correctness.[^27] |

### Important exclusions

- **Wolfram Engine/API cannot be a mandatory backend** because the requested package must be entirely free/open source. Replace its core role with SymPy and optionally SageMath/Maxima. Preserve a generic `CASBackend` interface so users may install a proprietary Wolfram adapter separately, but do not ship, test-gate, or claim it as part of the FOSS baseline.
- **CodeQL CLI is not an unrestricted open-source dependency.** Its query repository is MIT-licensed, but the CLI/engine has separate terms and closed-source/private-repository limitations; therefore it should not be a required AxiomLint component.[^28][^29]
- **Semgrep registry rules require license review.** Strict FOSS mode must use self-authored or clearly OSI-licensed rules, not blindly import the full maintained ruleset.[^30][^15]
- **Commercial LLM APIs are benchmark subjects, not required dependencies.** The core must operate with no LLM or with an OpenAI-compatible local adapter. Record model weights/license, quantization, backend, sampling configuration, prompt hash, and context assembly.

## Missing components

The initial concept names Z3, Lean 4, Wolfram-style mathematics, and ordinary review, but a complete auditable package also needs the following.

### Semantic correspondence

The largest soundness risk is not the solver; it is mistranslating source behavior into mathematics. Add a formally documented **Python Review Subset (PyRS)** covering supported types, mutation, exceptions, integer semantics, recursion, collections, nondeterminism, and prohibited constructs. Every formal result carries a correspondence status: `DIRECT`, `TESTED_TRANSLATION`, `REVIEWED_TRANSLATION`, `UNSUPPORTED`, or `ASSUMED`.

### Specification lifecycle

Formal tools prove specifications, including bad ones. Add requirement IDs, assumption registers, ambiguity findings, specification mutation tests, and vacuity checks. Require at least one positive and one negative witness where meaningful, and test whether weakening/removing each key clause changes the obligation.

### Trust inventory

Maintain a machine-readable trusted-computing-base manifest covering Python, OS/container runtime, parser, translation code, solver binaries, Lean kernel/build, mathlib, CAS, native libraries, and benchmark scorer. Each assurance claim must identify which TCB subset it relies on.

### Differential validation

Run Z3 and cvc5 on portable SMT-LIB obligations when practical; compare SymPy with Sage/Maxima on selected exact mathematics; replay Lean artifacts in a clean environment. Disagreement lowers confidence and opens a finding rather than triggering majority voting.

### Sandbox and hostile-code policy

Analyzed code may be adversarial. Default to no network, read-only source, writable scratch only, non-root user, CPU/memory/process/file-size/time limits, sanitized environment, no host credentials, and explicit syscall/container policy. Static-only mode must be available when execution is unsafe.

### Benchmark corpus governance

Create a versioned corpus with clean controls, single-defect tasks, multi-defect tasks, ambiguous-spec tasks, unsupported-semantics tasks, and adversarial false-positive traps. Maintain private holdouts, provenance/license records, deduplication hashes, defect taxonomies, independent labels, and adjudication records.

### Calibration and abstention

Confidence must be empirically calibrated, not generated as prose. Add reliability curves/Brier score or equivalent, plus abstention reasons such as unsupported semantics, insufficient specification, conflicting evidence, timeout, or untrusted execution.

### Cost and operational telemetry

Even FOSS has resource costs. Record wall time, CPU time, peak RAM, solver calls, proof attempts, model tokens, energy proxy where available, cache hits, and artifact volume. Report accuracy against both latency and resource budgets.

### Privacy and licensing

Add source-redaction policies, offline mode, telemetry-off default, corpus license manifest, model/license allowlist, SBOM, vulnerability scanning, and generated-output licensing review. NIST SSDF treats secure development as practices integrated into the SDLC across preparation, protection, production, and vulnerability response.[^31][^32]

## Work-package rules

Every package uses the repository template fields: status, owner, approval, dependencies, objective, governing requirements, scope, non-goals, acceptance criteria with evidence, risks, test/evidence plan, documentation impact, rollback, and S1-S4 outputs. Only one package should normally be active; parallel work requires approval, disjoint scopes, distinct evidence, and separate audits.

Use these mandatory acceptance rules for every package:

- All changed behavior has tests.
- All machine-readable artifacts validate against pinned schemas.
- All negative and inconclusive paths are tested.
- Fresh-clone local gates and authoritative CI pass against the same commit.
- S2 is performed in a context independent from S1 and source remains read-only during audit.
- Every finding is fixed, formally amended, or explicitly carried under policy.
- Reproduction commands and artifact digests are committed before closure.

## Phase A: constitution

### WP-001 — Charter and authority

**Objective:** Establish the project charter, scope, assurance vocabulary, decision rights, licensing policy, and authority hierarchy.

**Scope:** Project purpose; PyRS-first boundary; FOSS-only core; Research/High-Assurance tailoring; human approver; prohibited claims; amendment process; release authority; independence definition.

**Non-goals:** Implementation and benchmark execution.

**Acceptance evidence:** Approved charter; authority map; license policy; claim glossary; amendment and exception rules; initialized decision/risk/finding/session registers; governance validator passing.

**Rollback:** Revert charter adoption before dependent packages activate; once dependent work starts, supersede only by approved amendment.

### WP-002 — Requirements and standards crosswalk

**Objective:** Convert goals into uniquely identified, testable requirements.

**Scope:** Functional, security, evidence, privacy, accessibility, reproducibility, performance, interoperability, and benchmark requirements; crosswalk to repository standards, NIST SSDF, SARIF, SLSA/in-toto, SPDX/CycloneDX, and optional OWASP ASVS for any future web surface. OWASP ASVS provides structured technical security requirements and machine-readable lists for web applications.[^33]

**Acceptance evidence:** Requirement register with source, rationale, verification method, owner, status, and bidirectional traceability; no orphan mandatory requirements; independent ambiguity audit.

**Rollback:** Restore previous requirement baseline and retain rejected drafts.

### WP-003 — Threat model and trust case

**Objective:** Model threats from hostile source, compromised dependencies/tools, prompt injection, evidence tampering, semantic mistranslation, benchmark leakage, and malicious artifacts.

**Scope:** Assets, actors, trust boundaries, abuse cases, TCB inventory, security invariants, mitigations, residual risks, and fail-closed behaviors.

**Acceptance evidence:** Threat model; attack-tree/data-flow diagrams; TCB manifest schema; mapped mitigations/tests; approved residual-risk register.

**Rollback:** Disable all execution and remote-model adapters, retaining static-only analysis.

## Phase B: reproducible skeleton

### WP-004 — Repository and environment bootstrap

**Objective:** Create deterministic development, test, and release environments.

**Scope:** `pyproject.toml`, lockfile, Nix flake, rootless OCI image, pre-commit, CI, branch protection documentation, pinned actions, conventional commit/release policy, governance subtree.

**Acceptance evidence:** Fresh Linux clone reproduces tool versions and test result; Windows compatibility documented and exercised where supported; environment manifest and SBOM generated; no undeclared network dependency during tests.

**Rollback:** Restore last pinned lock/environment definitions.

### WP-005 — Schemas and immutable evidence store

**Objective:** Define canonical records before analyzers produce data.

**Scope:** JSON Schemas for run manifest, tool invocation, finding, evidence, proof, model, CAS result, correspondence, benchmark task/result, adjudication, and closure; content-addressed artifact layout.

**Acceptance evidence:** Positive/negative schema fixtures; stable IDs; canonical serialization; SHA-256 verification; migration/version policy; corruption tests fail closed.

**Rollback:** Read-only compatibility adapter to the prior schema; never rewrite accepted evidence in place.

### WP-006 — Safe runner

**Objective:** Execute tools and subject code under resource and privilege controls.

**Scope:** Network deny, read-only source, isolated scratch, environment allowlist, timeout/process/memory/output caps, signal handling, deterministic locale/timezone, audit log.

**Acceptance evidence:** Escape/abuse tests; fork-bomb, excessive output, timeout, path traversal, symlink, environment-secret, and network-attempt fixtures; static-only mode; cleanup verification.

**Rollback:** Disable dynamic execution globally.

## Phase C: conventional review baseline

### WP-007 — Intake and source model

**Objective:** Ingest repositories, commits, diffs, and review contracts without ambiguity.

**Scope:** Git identity checks, clean-state enforcement, file classification, Python AST/CST parsing, line mapping, dependency graph seed, unsupported-file handling.

**Acceptance evidence:** Fixtures for renames, deleted lines, syntax errors, generated files, symlinks, submodules, dirty trees, and Unicode paths; exact reviewed SHA appears in every artifact.

**Rollback:** Reject unsupported intake modes and accept explicit local directories only.

### WP-008 — Deterministic analyzer adapters

**Objective:** Establish the non-LLM baseline.

**Scope:** Ruff, mypy/Pyright, pytest, coverage, Bandit, FOSS-safe Semgrep profile, Gitleaks, Syft/Grype or Trivy; adapter contract and exit semantics.

**Acceptance evidence:** Golden fixtures per tool; zero-findings only when a scan executed successfully; partial/tool-error states distinguished from clean; normalized locations and taxonomies; raw output preserved.

**Rollback:** Quarantine a faulty adapter without disabling the rest of the pipeline.

### WP-009 — Finding fusion and reporting

**Objective:** Combine tool outputs without erasing provenance or disagreement.

**Scope:** Deduplication, fingerprints, severity/confidence separation, evidence graph, suppression/waiver records, Markdown/native JSON/SARIF output.

**Acceptance evidence:** Stable output ordering; reversible links to raw evidence; contradictory findings represented; SARIF validates; reporter snapshots deterministic.

**Rollback:** Emit unfused per-tool reports plus native evidence.

## Phase D: executable specifications

### WP-010 — Contract and property model

**Objective:** Define a practical specification language for small Python units.

**Scope:** Preconditions, postconditions, invariants, frame conditions, exceptions, purity, input generators, mathematical domains, overflow/float policy, and requirement links.

**Acceptance evidence:** SpecIR schema; parser/type checker; examples for integers, rationals, floats, strings, lists, dictionaries, recursion, and exception behavior; invalid/contradictory specs rejected.

**Rollback:** Accept handwritten Hypothesis/CrossHair adapters while freezing SpecIR evolution.

### WP-011 — Hypothesis and mutation validation

**Objective:** Turn specifications and findings into minimized executable counterexamples and measure test adequacy.

**Scope:** Hypothesis generation/shrinking; regression-test exporter; mutation testing through mutmut or equivalent; deterministic replay controls.

**Acceptance evidence:** Seed-independent replay from saved examples; minimized inputs; pre-fix failure/post-fix pass protocol; mutation results never presented as correctness proof.

**Rollback:** Preserve generated tests but disable automatic generation.

### WP-012 — CrossHair symbolic execution

**Objective:** Explore typed Python paths with symbolic inputs for supported contracts.

**Scope:** CrossHair adapter, supported-syntax matrix, timeout/unknown handling, counterexample replay, symbolic-path telemetry.

**Acceptance evidence:** Known positive/negative fixtures; every symbolic counterexample reproduced concretely; unsupported constructs abstain; no “proved correct” wording. CrossHair describes itself as repeatedly invoking functions with symbolic inputs to find counterexamples using SMT.[^6]

**Rollback:** Remove from gates and retain advisory artifacts.

## Phase E: SMT assurance

### WP-013 — SpecIR-to-SMT semantics

**Objective:** Translate a bounded SpecIR subset to SMT-LIB with explicit semantics.

**Scope:** Booleans, mathematical integers, fixed-width bit-vectors, rationals/reals, arrays, finite sequences, uninterpreted functions, quantifier policy, exceptional conditions.

**Acceptance evidence:** Translation conformance suite; hand-reviewed mappings; metamorphic tests; model-to-source value decoder; unsupported semantics rejected.

**Rollback:** Restrict translation to quantifier-free integer/bit-vector fragments.

### WP-014 — Z3 backend

**Objective:** Produce replayable SAT/UNSAT/UNKNOWN evidence and concrete countermodels.

**Scope:** Pinned solver, per-query budgets, seeds, SMT-LIB archive, model extraction, unsat-core/proof artifacts where supported, assumption labels.

**Acceptance evidence:** Solver status and reason preserved; models concretely replayed; malformed/timeout/unknown cases covered; independent query replay command; no bare boolean verdicts.

**Rollback:** Retain emitted SMT-LIB and route to alternate solvers.

### WP-015 — Solver diversity

**Objective:** Detect backend-specific errors and modelling instability.

**Scope:** cvc5 adapter for shared SMT-LIB subset; optional Bitwuzla for bit-vectors/floating point; result reconciliation.

**Acceptance evidence:** Agreement matrix; expected-divergence corpus; disagreement opens a finding and blocks high-assurance wording; license/build variants recorded. cvc5 supports a broad SMT theory portfolio and is distributed under modified/BSD terms depending on build features; GPL-linked optional features must remain disabled unless deliberately approved.[^9][^34]

**Rollback:** Require Z3 only and label all solver results single-backend.

## Phase F: symbolic mathematics

### WP-016 — SymPy backend

**Objective:** Supply a fully FOSS exact-symbolic replacement for mandatory Wolfram capabilities.

**Scope:** Simplification/equivalence, solving, calculus, exact arithmetic, polynomial/rational identities, matrices, combinatorics, assumptions, domains, and conversion to/from SpecIR.

**Acceptance evidence:** Exact-result fixtures; domain restrictions retained; numerical spot checks are secondary; unevaluated/conditional results preserved; replayable scripts. SymPy represents mathematical objects exactly and is BSD-licensed open source.[^11]

**Rollback:** Restrict CAS to exact polynomial/rational operations.

### WP-017 — Sage/Maxima diversity adapter

**Objective:** Cross-check higher-risk CAS claims and cover capabilities beyond SymPy.

**Scope:** Isolated process adapter; canonical exchange format; selected algebra, number theory, combinatorics, and exact linear algebra cases.

**Acceptance evidence:** License-isolation decision; cross-backend corpus; disagreement workflow; no opaque notebook-only results. SageMath is a GPL FOSS system that unifies SymPy, Maxima, GAP, FLINT, NumPy, SciPy, and other packages through a common Python-oriented environment.[^14]

**Rollback:** Keep Sage/Maxima optional and mark CAS evidence single-backend.

### WP-018 — Dimensional and numerical analysis

**Objective:** Catch errors that pure algebraic equality misses.

**Scope:** Unit/dimension checks, conditioning warnings, cancellation, overflow, NaN/infinity, signed zero, tolerance semantics, interval/high-precision checks where applicable.

**Acceptance evidence:** Adversarial floating-point corpus; exact-versus-machine arithmetic distinctions; no transfer of real-number proof to IEEE behavior without an explicit bridge.

**Rollback:** Emit advisory numerical-risk findings only.

## Phase G: Lean certification

### WP-019 — Lean project and proof policy

**Objective:** Establish reproducible kernel-checked proof infrastructure.

**Scope:** Pinned Lean/Lake/mathlib; declaration policy; trusted axioms policy; scanner for `sorry`, `admit`, unsafe escapes, unexpected axioms, and unpinned dependencies; clean replay.

**Acceptance evidence:** Proof project builds offline from lock; deliberately unsound/incomplete fixtures fail; proof artifact records theorem statement, imports, axioms, and digest.

**Rollback:** Disable E5/E6 labels while keeping lower evidence tiers.

### WP-020 — SpecIR-to-Lean translation

**Objective:** Generate auditable Lean definitions and theorem statements for the bounded subset.

**Scope:** Integers/naturals, finite lists, pure recursion, algebraic data, pre/postconditions, selected arithmetic; source-map comments and requirement IDs.

**Acceptance evidence:** Translation golden suite; round-trip structural checks where possible; human-readable output; independent semantic review; every assumption visible in theorem context.

**Rollback:** Hand-author Lean models and retain SpecIR only as metadata.

### WP-021 — Proof construction and replay

**Objective:** Support manual, tactic, SMT/CAS-assisted, and optionally LLM-drafted proofs without confusing proof search with proof checking.

**Scope:** Proof job protocol; diagnostics loop; tactic allowlist; imported theorem provenance; proof minimization; replay worker.

**Acceptance evidence:** Only kernel-accepted artifacts reach E5; failed goals remain failed; proof search logs separated from accepted proof; fresh worker replay required.

**Rollback:** Permit manual proofs only.

### WP-022 — Source correspondence pilot

**Objective:** Earn the first E6 claim for a tiny source subset.

**Scope:** Pure Python functions over bounded integers/naturals/lists; translation contract; executable differential tests; reviewed simulation/refinement argument.

**Acceptance evidence:** Curated positive and mistranslation-negative cases; two-person approval for E6; proof and source pinned; explicit excluded language features.

**Rollback:** Downgrade all results to E5 “proved about model.”

## Phase H: review intelligence

### WP-023 — LLM reviewer adapter

**Objective:** Add model-generated hypotheses without making the model a trust anchor.

**Scope:** Local OpenAI-compatible endpoint first; immutable prompt templates; structured JSON output; context budget; injection resistance; model/license/config manifest; optional external benchmark adapters.

**Acceptance evidence:** Malformed-output, prompt-injection, data-exfiltration, nondeterminism, and refusal fixtures; tool cannot grant evidence levels; no hidden network calls.

**Rollback:** Run deterministic/formal stack with LLM disabled.

### WP-024 — Evidence-guided review planner

**Objective:** Select the cheapest appropriate verifier for each candidate claim.

**Scope:** Rule-based routing by defect class and semantics; budgets; escalation; abstention; contradictory-evidence handling.

**Acceptance evidence:** Routing decision trace; deterministic policy mode; budget exhaustion is inconclusive; fixtures prove no unsupported backend is selected.

**Rollback:** Run a fixed backend sequence.

### WP-025 — Calibrated verdict engine

**Objective:** Produce useful review reports while preserving epistemic boundaries.

**Scope:** Finding ranking, evidence weighting, severity, calibrated confidence, abstention, duplicate suppression, reviewer-facing explanation.

**Acceptance evidence:** Confidence calibrated only from held-out data; evidence level and severity never conflated; false-positive budget configurable; explanations link to raw replay.

**Rollback:** Remove aggregate confidence and display evidence/finding tables only.

## Phase I: benchmark construction

### WP-026 — Corpus policy and taxonomy

**Objective:** Define what “effective code review” means before selecting tasks.

**Scope:** Correctness, security, API misuse, concurrency where supported, numerical, performance traps, maintainability-with-impact, evidence-integrity, clean controls, unsupported cases; inclusion/exclusion and licensing.

**Acceptance evidence:** Taxonomy, scoring rules, corpus datasheet, leakage policy, clean-control ratio, deduplication method, private-holdout protocol, independent approval.

**Rollback:** Freeze corpus ingestion and retain only licensed audited tasks.

### WP-027 — Seed corpus and oracle creation

**Objective:** Build small-code review tasks with defensible ground truth.

**Scope:** Human-authored minimal cases, real fixed defects reduced to review units, clean twins, mutation-derived defects only when manually validated, ambiguous/inconclusive cases, provenance.

**Acceptance evidence:** Two independent labels plus adjudication; executable oracle or formal rationale; exact changed lines; task license and origin; hidden oracle separated from runner input.

**Rollback:** Quarantine disputed tasks without deleting records.

### WP-028 — Benchmark harness

**Objective:** Run all systems under matched device, code, prompt, context, budgets, and environmental conditions.

**Scope:** Randomized/counterbalanced order; cold/warm cache policy; repetition; timeout; model temperature/seeds; concurrency isolation; raw capture; blind scoring; resource telemetry.

**Acceptance evidence:** Harness self-tests; dummy systems expose scoring flaws; resume without duplication; manifest completeness enforced; scorer independent from AxiomLint.

**Rollback:** Invalidate affected runs and preserve them as excluded evidence with reason.

### WP-029 — Metrics and statistics

**Objective:** Predefine decision-relevant metrics and uncertainty.

**Scope:** Finding-level precision/recall/F1; task success; false positives per clean task/KLOC; severity-weighted recall; localization accuracy; evidence validity; calibration; abstention coverage; latency; CPU/RAM/tokens; paired comparisons; confidence intervals and multiplicity policy.

**Acceptance evidence:** Versioned analysis code tested against hand-calculated fixtures; no post-result metric changes; raw-to-table lineage; effect sizes reported with uncertainty.

**Rollback:** Mark analysis exploratory and rerun only under a new preregistration.

## Phase J: controlled evaluation

### WP-030 — Internal component validation

**Objective:** Establish that adapters and evidence replay work before comparative claims.

**Scope:** Per-backend conformance, failure injection, schema/provenance checks, repeated-run stability, resource limits.

**Acceptance evidence:** All high-severity harness defects closed; replay success target preregistered; no benchmark conclusions yet.

**Rollback:** Return failing component to its originating package.

### WP-031 — Ablation campaign

**Objective:** Measure which components add value.

**Arms:** Conventional only; LLM only; conventional+LLM; +Hypothesis/CrossHair; +Z3; +CAS; +Lean; all components; formal stack without LLM; alternate solver/CAS checks.

**Acceptance evidence:** E0-E6 campaign records; paired task assignments; preregistered stopping and exclusion rules; negative/null outcomes published; component value measured against added cost.

**Rollback:** None for results—accepted experiment records are immutable; corrections use errata.

### WP-032 — Leading-system comparison

**Objective:** Compare AxiomLint with selected leading LLMs and coding/review agents under same code, device where locally runnable, prompts/context, and budgets.

**Scope:** Matched-harness track for scientific comparability; native-agent track separately for ecological validity; model/version snapshots; contamination caveats.

**Acceptance evidence:** Fairness matrix; identical task visibility; no oracle leakage; external API/device differences explicitly stratified; blinded scoring; complete raw artifacts subject to license/privacy limits.

**Rollback:** Withdraw incomparable arms rather than normalize them misleadingly.

### WP-033 — Robustness and adversarial campaign

**Objective:** Test whether apparent gains survive hostile and shifted conditions.

**Scope:** Prompt injection in code/comments, misleading tests, inconsistent specs, dead code, renamed identifiers, formatting changes, larger functions, timeout pressure, poisoned dependencies, tool disagreement.

**Acceptance evidence:** Metamorphic invariance expectations preregistered; security failures receive D1/D2 treatment; performance degradation and abstention curves reported.

**Rollback:** Disable affected capability until a corrective package closes.

## Phase K: hardening and release

### WP-034 — Security and supply-chain hardening

**Objective:** Satisfy the governance repository's required SAST, SCA, secret, license, container/IaC, pinning, least-privilege, provenance, SBOM, and signing controls.

**Scope:** Threat-model retest; dependency review; Syft/Grype or Trivy; Gitleaks; FOSS rule scans; OpenSSF Scorecard; pinned CI; signed provenance and release artifacts.

**Acceptance evidence:** No unaddressed blocking security finding; SBOM and vulnerability report; signed/checkable provenance; release build from verified clean revision; incident response path.

**Rollback:** Revoke release, publish advisory/erratum, and restore last accepted build.

### WP-035 — Usability and integration

**Objective:** Make rigorous review usable from CLI and CI without weakening evidence.

**Scope:** Configuration profiles, baseline/suppression workflow, exit codes, GitHub/GitLab-neutral SARIF artifacts, documentation, sample repositories, accessibility of reports.

**Acceptance evidence:** End-to-end novice and expert walkthroughs; config validation; failure messages actionable; offline mode documented; no UI-only evidence.

**Rollback:** Support CLI/native JSON only.

### WP-036 — Release candidate and independent audit

**Objective:** Determine whether the code-review milestone is ready for a public versioned release.

**Scope:** Full requirements trace, clean-room install/replay, documentation audit, benchmark synthesis, security audit, license audit, known-limitations registry.

**Acceptance evidence:** Independent audit verdict; all D1/D2 findings closed; authoritative CI green on release SHA; signed release, SBOM, provenance, reproducibility instructions, and benchmark report; maintainer approval.

**Rollback:** No release; reopen failed requirement packages.

## Phase gates

| Gate | Required closure |
|---|---|
| G0 Constitution | WP-001 through WP-003 closed; charter, requirements method, and threat model approved |
| G1 Reproducible core | WP-004 through WP-006 closed; clean environment and safe runner independently reproduced |
| G2 Baseline reviewer | WP-007 through WP-009 closed; deterministic review emits validated evidence and SARIF |
| G3 Executable contracts | WP-010 through WP-012 closed; saved counterexamples replay and unsupported cases abstain |
| G4 Formal backend | WP-013 through WP-022 closed; E3-E5 operational and first narrowly scoped E6 pilot independently accepted |
| G5 Review intelligence | WP-023 through WP-025 closed; LLM remains optional/untrusted and verdicts calibrated/abstaining |
| G6 Benchmark ready | WP-026 through WP-029 closed before comparative data is inspected |
| G7 Effectiveness shown | WP-030 through WP-033 accepted under E0-E6 experiment governance |
| G8 Milestone release | WP-034 through WP-036 closed with independent audit and signed provenance |

A gate is evidence-based, not time-based. Packages may be split if they cease to be the smallest coherent advancement, but their acceptance criteria may not be diluted without an approved amendment.

## Benchmark protocol

### Primary question

Does the complete AxiomLint configuration increase defect detection and actionable precision over the strongest matched baseline while staying within preregistered false-positive, latency, and resource budgets?

### Secondary questions

- Which component produces the incremental gain?
- Does formal evidence improve reviewer trustworthiness or merely runtime?
- How often do SMT/CAS/Lean expose incorrect LLM claims versus confirm them?
- What task classes benefit, fail, or trigger abstention?
- Are results robust to formatting, naming, prompt injection, ambiguous specifications, and solver diversity?

### Required controls

- Clean tasks to estimate hallucinated findings.
- Unsupported tasks to test honest abstention.
- Conventional-only and no-LLM arms.
- Same task text, repository state, dependency cache policy, device allocation, concurrency, and resource budget.
- Separate local-model and remote-API strata rather than pretending devices are identical.
- Blinded adjudication and task-level paired comparisons.
- Private holdout not used for prompts, routing, calibration, or acceptance thresholds.

### Acceptance decision

The initial milestone passes only if all of the following preregistered conditions hold:

- The full system produces a practically meaningful, statistically supported gain over the strongest matched comparator on the primary metric.
- It remains within the false-positive and resource budgets.
- Every E2-E6 item selected for audit replays cleanly; any non-replayable high-assurance artifact is a blocking integrity finding.
- Clean-task performance does not degrade beyond the non-inferiority margin.
- Ablation evidence attributes the gain; the result is not solely prompt/model variance.
- Unsupported cases abstain at an acceptable rate rather than receiving fabricated assurance.
- No unresolved D1/D2 security, evidence-integrity, licensing, or benchmark-validity finding remains.

Exact thresholds must be specified in E1 preregistration after a pilot used solely to estimate variance; they must not be chosen after viewing confirmatory outcomes. The governing experiment cycle prohibits changing thresholds, seeds, denominators, exclusions, or decision rules during execution.

## Repository layout

```text
axiomlint/
  governance/
    charter/ requirements/ standards/ work-packages/
    sessions/ audits/ decisions/ risks/ findings/ experiments/
  src/axiomlint/
    intake/ runner/ adapters/ specir/ evidence/ fusion/ reporting/
    backends/{hypothesis,crosshair,z3,cvc5,sympy,sage,lean,llm}/
  schemas/
  lean/
    AxiomLint/ Generated/ Proofs/
  rules/
    bandit/ semgrep/
  benchmarks/
    corpus-manifest/ public/ harness/ scorer/ analysis/
  tests/
    unit/ integration/ conformance/ adversarial/ golden/ e2e/
  docs/
    architecture/ assurance-case/ supported-semantics/ user-guide/
  artifacts/
    .gitignore
  flake.nix
  pyproject.toml
  uv.lock
  Containerfile
```

Raw benchmark data should live in immutable release artifacts or content-addressed storage when too large for Git, with manifests and hashes committed. Secrets, proprietary benchmark answers, and restricted model outputs must not enter public history.

## Mandatory registers

- Requirement and traceability register.
- Work-package/session register.
- Finding/deviation register.
- Risk and assumption register.
- Decision/amendment register.
- Tool, model, dataset, and license register.
- Trusted-computing-base register.
- Corpus provenance and leakage register.
- Suppression/waiver register with expiry.
- Evidence and artifact manifest.
- Benchmark run and exclusion register.
- Release and errata register.

## Quality properties

### Soundness discipline

- Never conflate absence of a counterexample with proof.
- Never conflate an SMT UNSAT result with source correctness unless translation correspondence is justified.
- Never conflate exact-real algebra with IEEE floating-point behavior.
- Never let an LLM assign its own evidence level.
- Never discard unknown, timeout, conflict, unsupported, or negative outcomes.
- Never accept generated tests as independent evidence if the same model generated the claim and oracle without external validation.

### Audit independence

S2 must use a separate agent context or human reviewer with no unexamined reliance on S1 summaries. Benchmark labels and scorer logic must be isolated from product prompts and accessible only through controlled adjudication. The repository's audit standard requires reviewing the governing contract before the diff, pinning the reviewed head, and including location, failure mode, impact, reasoning/reproduction, and expected correction for every actionable finding.

### Reproducibility

Use both a Nix development environment and rootless OCI image initially. Nix offers declarative reproducible environments, isolated builds, auditability, and rollback, while ReproZip may later capture Linux command executions and dependencies into portable experiment bundles.[^23][^35] Record host constraints honestly; container equality is not hardware equality.

## Deferred roadmap

Only after G8 closes should new campaigns begin, one capability at a time:

1. **Suggestion-only:** propose non-mutating fixes, measure acceptance and correctness.
2. **Test generation:** generate regression/property tests, independently validate oracles.
3. **Patch generation:** produce patches but require full baseline/formal replay and human approval.
4. **Automated repair:** bounded iterative repair with rollback, patch minimization, and independent audit.
5. **Evidence-guided generation:** generate code from explicit contracts, then test and prove selected properties.
6. **Repository-scale analysis:** interprocedural/dataflow models, incremental caching, multiple languages.
7. **Higher assurance:** verified translators, proof-producing SMT paths, richer refinement proofs, and reproducible releases across independent builders.

Each step requires a new charter amendment or campaign authorization, new work packages, a benchmark extension, preregistered acceptance criteria, and proof that prior milestone quality does not regress.

## Immediate starting set

Activate only **WP-001** first. On closure, execute WP-002 and WP-003 sequentially, then bootstrap implementation. The first technical vertical slice should not attempt every backend: it should ingest one pure typed Python function, run deterministic checks, accept a hand-written contract, find/replay a Hypothesis or CrossHair counterexample, emit one Z3 model, verify one SymPy identity with domains, check one Lean theorem about the model, and produce native JSON/SARIF/Markdown plus a complete manifest.

That slice is successful only when a fresh independent environment can reproduce every artifact from the pinned revision and when the report accurately distinguishes counterexample, model result, theorem result, and source correspondence.

---

## References

1. [leanprover.github.io › theorem_proving_in_lean4Introduction - leanprover.github.io](https://leanprover.github.io/theorem_proving_in_lean4//Introduction/) - The Lean source code, and instructions for building Lean, are available at https://github.com/leanpr...

2. [docs.oasis-open.org › sarif › sarifStatic Analysis Results Interchange Format (SARIF) Version 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html) - This document defines a standard format for the output of
static analysis tools.

3. [Static Analysis Results Interchange Format (SARIF) ...](https://www.oasis-open.org/standard/sarifv2-1-os/) - SARIF (https://www.oasis-open.org/standard/sarifv2-1-os/) defines a standard format for the output o...

4. [hypothesis.readthedocs.io › en › latestHypothesis 6.168.3 documentation](https://hypothesis.readthedocs.io/en/latest/index.html) - Hypothesis is the property-based testing library for Python.
With Hypothesis, you write tests which ...

5. [hypothesis · PyPI](https://pypi.org/project/hypothesis/) - Hypothesis is the property-based testing library for Python.
With Hypothesis, you write tests which ...

6. [github.com › pschanely › CrossHairGitHub - pschanely/CrossHair: An analysis tool for Python ...](https://github.com/pschanely/CrossHair) - An analysis tool for Python that blurs the line between testing and
type systems.

7. [www.microsoft.com · en-us · researchZ3 - Microsoft Research: Tools](https://www.microsoft.com/en-us/research/project/z3-3/tools/) - Z3 can be built using Visual Studio, a Makefile or using CMake.

8. [Z3: an efficient SMT solver - Microsoft Research](https://www.microsoft.com/en-us/research/publication/z3-an-efficient-smt-solver/) - Z3 is a theorem prover from Microsoft Research.
It is licensed under the MIT license.

9. [CVC5 at the SMT Competition 2021](https://smt-comp.github.io/2021/system-descriptions/cvc5.pdf) - The source code of CVC5 is open and available to students, researchers, software companies, and ever...

10. [Bitwuzla ⋆ - Stanford Computer Science](https://cs.stanford.edu/~preiner/publications/2023/NiemetzP-CAV23.pdf) - Bitwuzla is available on GitHub [28] under the

11. [Introduction¶](https://docs.sympy.org/latest/tutorials/intro-tutorial/intro.html) - liberal BSD license, so you can modify the source code and even sell it if you

12. [SymPy](https://www.sympy.org/en/index.html) - - **Free:** Licensed under BSD, SymPy is free both as in speech and as in beer.

13. [Press Kit - SageMath](https://www.sagemath.org/library-press.html) - Its license is the well known GNU Public License (GPL) and everyone is allowed to download it, insta...

14. [SageMath - Open-Source Mathematical Software System](https://www.sagemath.org/) - SageMath is a free open-source mathematics software system licensed under the GPL. It builds on top ...

15. [Semgrep Community Edition in CI](https://docs.semgrep.dev/deployment/oss-deployment) - This setup uses only the **LGPL 2.1** Semgrep CLI tool.

16. [Licensing](https://docs.semgrep.dev/licensing) - Semgrep Community Edition (CE) The Semgrep CE engine is an open source project licensed under LGPL 2...

17. [About Us - Gitleaks](https://gitleaks.org/about-us/) - **Gitleaks** is a fast, flexible, and reliable secrets scanner designed to help developers and secur...

18. [Gitleaks - GitHub](https://github.com/gitleaks) - Gitleaks is a SAST tool for detecting and preventing hardcoded secrets like passwords, api keys, and...

19. [Grype by Anchore: The Open Source Vulnerability Scanner](https://anchore.com/grype/) - Syft first generates an SBOM, creating a complete inventory of all packages in containers, source co...

20. [Syft by Anchore: The Open Source SBOM Generator](https://anchore.com/syft/) - Grype is a vulnerability scanner that identifies and prioritizes known vulnerabilities from an SBOM,...

21. [trivy.dev › docs › latestSBOM scanning - trivy.dev](https://trivy.dev/docs/latest/guide/target/sbom/) - Trivy can take the following SBOM formats as an input and scan for vulnerabilities and licenses.
......

22. [NixOS/nix: Nix, the purely functional package manager](https://github.com/nixos/nix) - Nix is a powerful package manager for Linux and other Unix systems that makes package
management rel...

23. [nix.devWelcome to nix.dev — nix.dev documentation](https://nix.dev/) - nix.dev is the home of official documentation for the Nix ecosystem.

24. [Full computational reproducibility!](https://www.reprozip.org/) - The development of ReproZip has always been open source and free to use since the project began in 2...

25. [attestation/spec/predicates/provenance.md at main · in-toto/attestation](https://github.com/in-toto/attestation/blob/main/spec/predicates/provenance.md) - Type URI: https://slsa.dev/provenance
...
Please visit the SLSA Provenance spec for information on p...

26. [SLSA • Provenance](https://slsa.dev/spec/v0.1/provenance) - This document defines the following predicate type within the in-toto attestation framework:

27. [OpenSSF Scorecard - Security health metrics for Open ...](https://github.com/ossf/scorecard) - Scorecard is an automated tool that assesses a number of important heuristics

28. [CodeQL: the libraries and queries that power security ...](https://github.com/github/codeql) - This open source repository contains the standard CodeQL libraries and queries that power GitHub Adv...

29. [Intellisense](https://docs.github.com/en/enterprise-server@3.22/code-security/concepts/code-scanning/codeql/codeql-for-vs-code) - **License notice:** If you don’t have a license for GitHub Code Security then, by installing this pr...

30. [Important updates to Semgrep OSS](https://semgrep.dev/blog/2024/important-updates-to-semgrep-oss/) - Community Edition rules are Semgrep-maintained rules that are now governed by the **Semgrep Rules Li...

31. [Secure Software Development Framework (SSDF)](https://csrc.nist.gov/projects/ssdf) - NIST Special Publication (SP) 800-218, *Secure Software Development Framework (SSDF) Version 1.1: Re...

32. [SP 800-218, Secure Software Development Framework ...](https://csrc.nist.gov/pubs/sp/800/218/final) - by M Souppaya · 2022 · Cited by 266 — NIST SP 800-218. Secure Software Development Framework (SSDF) ...

33. [OWASP Application Security Verification Standard (ASVS)](https://owasp.org/projects/asvs) - The OWASP Application Security Verification Standard (ASVS) Project provides a basis for testing web...

34. [FM](https://cs.stanford.edu/~preiner/publications/2024/BarrettTBNPRZ-FM24.pdf) - cvc5 is distributed under the BSD 3-clause license.

35. [ReproZip’s Documentation¶](http://docs.reprozip.org/en/latest/) - ReproZip is a tool aimed at simplifying the process of creating reproducible experiments from *comma...

