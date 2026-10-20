# AxiomLint Individual Session Briefs

This planning expansion contains **144 individual briefs for all 36 work packages**.
Every package follows S1 implementation, S2 independent audit, S3 finding-only
remediation, and S4 documentation/closure; none has been executed or approved by
creating this catalogue. Existing live states and pending ratifications remain unchanged.

Planning baseline: `083f21c4b12a60c8556138d26d0aee516eb24d2b`. Begin with [the four-session protocol](PROTOCOL.md)
and the actual declaration, not a later-stage prompt chosen out of order.
The [consolidated masterbook](../../docs/planning/axiomlint-session-briefs-masterbook.md) contains the
same full briefs. [Source/design rationale](../../docs/research/session-brief-design.md)
explains technical and experimental distinctions.

## How to use a brief

Read current authority/state, verify entry/dependency approval, pin a real
revision and owner/context, then instantiate a live record only for the
authorized session. Freeze the approved brief revision in that record.
Use a different context for S2 and independent S3 delta review. A no-findings S2
still requires an S3 no-change verification and separate commit.

The user requested planning, not activation or charter ratification. All future
briefs are DRAFT_NOT_AUTHORIZED. WP-001's open S1 is supplemented, not recreated.
Do not overwrite historical records with the draft catalogue.

## Navigation

| Package | Subject | Implementation | Independent audit | Remediation | Documentation/closure |
|---|---|---|---|---|---|
| [WP-001](../work-packages/WP-001.md) | Charter and authority | [S1](WP-001/S1.md) | [S2](WP-001/S2.md) | [S3](WP-001/S3.md) | [S4](WP-001/S4.md) |
| [WP-002](../work-packages/WP-002.md) | Requirements and standards crosswalk | [S1](WP-002/S1.md) | [S2](WP-002/S2.md) | [S3](WP-002/S3.md) | [S4](WP-002/S4.md) |
| [WP-003](../work-packages/WP-003.md) | Threat model and trust case | [S1](WP-003/S1.md) | [S2](WP-003/S2.md) | [S3](WP-003/S3.md) | [S4](WP-003/S4.md) |
| [WP-004](../work-packages/WP-004.md) | Repository and environment bootstrap | [S1](WP-004/S1.md) | [S2](WP-004/S2.md) | [S3](WP-004/S3.md) | [S4](WP-004/S4.md) |
| [WP-005](../work-packages/WP-005.md) | Schemas and immutable evidence store | [S1](WP-005/S1.md) | [S2](WP-005/S2.md) | [S3](WP-005/S3.md) | [S4](WP-005/S4.md) |
| [WP-006](../work-packages/WP-006.md) | Safe runner | [S1](WP-006/S1.md) | [S2](WP-006/S2.md) | [S3](WP-006/S3.md) | [S4](WP-006/S4.md) |
| [WP-007](../work-packages/WP-007.md) | Intake and source model | [S1](WP-007/S1.md) | [S2](WP-007/S2.md) | [S3](WP-007/S3.md) | [S4](WP-007/S4.md) |
| [WP-008](../work-packages/WP-008.md) | Deterministic analyzer adapters | [S1](WP-008/S1.md) | [S2](WP-008/S2.md) | [S3](WP-008/S3.md) | [S4](WP-008/S4.md) |
| [WP-009](../work-packages/WP-009.md) | Finding fusion and reporting | [S1](WP-009/S1.md) | [S2](WP-009/S2.md) | [S3](WP-009/S3.md) | [S4](WP-009/S4.md) |
| [WP-010](../work-packages/WP-010.md) | Contract and property model | [S1](WP-010/S1.md) | [S2](WP-010/S2.md) | [S3](WP-010/S3.md) | [S4](WP-010/S4.md) |
| [WP-011](../work-packages/WP-011.md) | Hypothesis and mutation validation | [S1](WP-011/S1.md) | [S2](WP-011/S2.md) | [S3](WP-011/S3.md) | [S4](WP-011/S4.md) |
| [WP-012](../work-packages/WP-012.md) | CrossHair symbolic execution | [S1](WP-012/S1.md) | [S2](WP-012/S2.md) | [S3](WP-012/S3.md) | [S4](WP-012/S4.md) |
| [WP-013](../work-packages/WP-013.md) | SpecIR-to-SMT semantics | [S1](WP-013/S1.md) | [S2](WP-013/S2.md) | [S3](WP-013/S3.md) | [S4](WP-013/S4.md) |
| [WP-014](../work-packages/WP-014.md) | Z3 backend | [S1](WP-014/S1.md) | [S2](WP-014/S2.md) | [S3](WP-014/S3.md) | [S4](WP-014/S4.md) |
| [WP-015](../work-packages/WP-015.md) | Solver diversity | [S1](WP-015/S1.md) | [S2](WP-015/S2.md) | [S3](WP-015/S3.md) | [S4](WP-015/S4.md) |
| [WP-016](../work-packages/WP-016.md) | SymPy backend | [S1](WP-016/S1.md) | [S2](WP-016/S2.md) | [S3](WP-016/S3.md) | [S4](WP-016/S4.md) |
| [WP-017](../work-packages/WP-017.md) | Sage/Maxima diversity adapter | [S1](WP-017/S1.md) | [S2](WP-017/S2.md) | [S3](WP-017/S3.md) | [S4](WP-017/S4.md) |
| [WP-018](../work-packages/WP-018.md) | Dimensional and numerical analysis | [S1](WP-018/S1.md) | [S2](WP-018/S2.md) | [S3](WP-018/S3.md) | [S4](WP-018/S4.md) |
| [WP-019](../work-packages/WP-019.md) | Lean project and proof policy | [S1](WP-019/S1.md) | [S2](WP-019/S2.md) | [S3](WP-019/S3.md) | [S4](WP-019/S4.md) |
| [WP-020](../work-packages/WP-020.md) | SpecIR-to-Lean translation | [S1](WP-020/S1.md) | [S2](WP-020/S2.md) | [S3](WP-020/S3.md) | [S4](WP-020/S4.md) |
| [WP-021](../work-packages/WP-021.md) | Proof construction and replay | [S1](WP-021/S1.md) | [S2](WP-021/S2.md) | [S3](WP-021/S3.md) | [S4](WP-021/S4.md) |
| [WP-022](../work-packages/WP-022.md) | Source correspondence pilot | [S1](WP-022/S1.md) | [S2](WP-022/S2.md) | [S3](WP-022/S3.md) | [S4](WP-022/S4.md) |
| [WP-023](../work-packages/WP-023.md) | LLM reviewer adapter | [S1](WP-023/S1.md) | [S2](WP-023/S2.md) | [S3](WP-023/S3.md) | [S4](WP-023/S4.md) |
| [WP-024](../work-packages/WP-024.md) | Evidence-guided review planner | [S1](WP-024/S1.md) | [S2](WP-024/S2.md) | [S3](WP-024/S3.md) | [S4](WP-024/S4.md) |
| [WP-025](../work-packages/WP-025.md) | Calibrated verdict engine | [S1](WP-025/S1.md) | [S2](WP-025/S2.md) | [S3](WP-025/S3.md) | [S4](WP-025/S4.md) |
| [WP-026](../work-packages/WP-026.md) | Corpus policy and taxonomy | [S1](WP-026/S1.md) | [S2](WP-026/S2.md) | [S3](WP-026/S3.md) | [S4](WP-026/S4.md) |
| [WP-027](../work-packages/WP-027.md) | Seed corpus and oracle creation | [S1](WP-027/S1.md) | [S2](WP-027/S2.md) | [S3](WP-027/S3.md) | [S4](WP-027/S4.md) |
| [WP-028](../work-packages/WP-028.md) | Benchmark harness | [S1](WP-028/S1.md) | [S2](WP-028/S2.md) | [S3](WP-028/S3.md) | [S4](WP-028/S4.md) |
| [WP-029](../work-packages/WP-029.md) | Metrics and statistics | [S1](WP-029/S1.md) | [S2](WP-029/S2.md) | [S3](WP-029/S3.md) | [S4](WP-029/S4.md) |
| [WP-030](../work-packages/WP-030.md) | Internal component validation | [S1](WP-030/S1.md) | [S2](WP-030/S2.md) | [S3](WP-030/S3.md) | [S4](WP-030/S4.md) |
| [WP-031](../work-packages/WP-031.md) | Ablation campaign | [S1](WP-031/S1.md) | [S2](WP-031/S2.md) | [S3](WP-031/S3.md) | [S4](WP-031/S4.md) |
| [WP-032](../work-packages/WP-032.md) | Leading-system comparison | [S1](WP-032/S1.md) | [S2](WP-032/S2.md) | [S3](WP-032/S3.md) | [S4](WP-032/S4.md) |
| [WP-033](../work-packages/WP-033.md) | Robustness and adversarial campaign | [S1](WP-033/S1.md) | [S2](WP-033/S2.md) | [S3](WP-033/S3.md) | [S4](WP-033/S4.md) |
| [WP-034](../work-packages/WP-034.md) | Security and supply-chain hardening | [S1](WP-034/S1.md) | [S2](WP-034/S2.md) | [S3](WP-034/S3.md) | [S4](WP-034/S4.md) |
| [WP-035](../work-packages/WP-035.md) | Usability and integration | [S1](WP-035/S1.md) | [S2](WP-035/S2.md) | [S3](WP-035/S3.md) | [S4](WP-035/S4.md) |
| [WP-036](../work-packages/WP-036.md) | Release candidate and independent audit | [S1](WP-036/S1.md) | [S2](WP-036/S2.md) | [S3](WP-036/S3.md) | [S4](WP-036/S4.md) |

## Validation

```sh
python3 tools/check_session_briefs.py
python3 tools/local_check.py
```

Per-package suites are planned and must be implemented by their authorized S1:
`python3 tools/run_wp_tests.py WP-NNN` deliberately refuses empty/all-skipped
selections. Do not run nonexistent future tool suites just to obtain a zero exit.
No hosted CI, push, installation or subject/backend execution is part of this task.

## Decisions before execution

Ratify charter/AMD-001 and bootstrap scope first. Resolve WP-025 calibration
data versus corpus-order dependency without leaking later holdouts. Obtain
separate host provisioning approval where required. Keep remote comparison arms
and public publication disabled unless separately authorized.
EXP-E2 independent protocol review happens before measurement within S1; the
later S2 is not a retroactive substitute.

## Integrity and revision policy

`catalog.json` records every brief digest, package-contract digest, global
predecessor/successor and input hashes. Source contract changes or manual brief
edits fail reproducibility checks. Review and rebaseline plans deliberately;
do not regenerate accepted or executed history. Draft status is not a waiver.
