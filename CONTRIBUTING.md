# Contributing to AxiomLint

Thank you for your interest in contributing to AxiomLint!

AxiomLint is a local-first, FOSS evidence-carrying review orchestrator for small,
deterministic, typed Python functions. To maintain evidentiary integrity and
formal assurance, the repository operates under strict governing standards.

## Core Rules of Engagement

1. **Local-first execution:**
   All builds, checks, and tests must run exclusively on a local environment
   (Python 3.12+ and Git). No hosted CI services, third-party cloud runners, or
   remote endpoints are used or permitted.

2. **Non-executing static foundation:**
   Never execute reviewed subject code, evaluate expressions, deserialize untrusted
   inputs, load arbitrary modules, or invoke external solvers directly in this
   foundation. Analysis is bounded to static inspection (e.g. AST parsing).

3. **Governed four-session lifecycle:**
   Capabilities are tracked through four formal, separated sessions:
   - **S1 (Implementation):** Code changes, positive/negative fixtures, and raw local logs.
   - **S2 (Independent Audit):** Independent verification against acceptance criteria.
   - **S3 (Remediation):** Addressing specific S2 findings without expanding scope.
   - **S4 (Closure & Documentation):** Documentation, registers, traceability, and acceptance.

4. **Preserve outcomes:**
   Never fabricate approvals, sign-offs, or pass states. Negative, failed, or
   contradictory outcomes must be preserved as evidence.

## Local Verification Baseline

Before submitting contributions or opening pull requests, verify all local checks pass:

```sh
# Run development checks
python3 tools/local_check.py

# Verify repository hygiene and syntax
python3 tools/hygiene_check.py
python3 tools/hygiene_check.py --syntax

# Verify acceptance-mode on a clean worktree
python3 tools/local_check.py --require-clean
```

## How to Propose Changes

- **Discussions:** Use [GitHub Discussions](https://github.com/Symbo-gif/axiomlint/discussions)
  for questions, architectural ideas, or general feedback.
- **Issues:** Use the structured issue templates for bug reports, work package
  proposals, or audit findings.
- **Pull Requests:** Ensure each pull request targets a specific work package or
  finding, adheres to clean commit boundaries, and references local verification
  evidence.
