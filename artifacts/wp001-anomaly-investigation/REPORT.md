# File-Truncation Anomaly Investigation Report

- **Date:** 2026-10-21
- **Investigator Context ID:** `72128125-7e51-4832-93b2-09822b20cfb9`
- **Scope:** Root cause investigation of file truncation (0 bytes) and content reversion occurring ~25s after git commits in `/home/themichael/PerplexityWorkspace/axiomlint`.

## 1. Incidents Overview

### Incident 1 (S2 -> S3 transition)
- **Commit:** `63bd5f8bc6e66803cd4d5a06c92b6701b1ac09f6` ("audit: record independent S2 audit for WP-001 foundation")
- **Commit Time:** 2026-10-21 01:46:33 -03:00
- **Anomaly Detection:** S3 remediator entry. Four newly created files found truncated to 0 bytes:
  - `governance/audits/WP-001/S2-findings.json`
  - `governance/audits/WP-001/S2-report.md`
  - `governance/execution/WP-001/S2/handoff.md`
  - `governance/execution/WP-001/S2/record.json`
- **Anomaly Mtime:** ~01:47:45 -03:00 (~72s after commit).

### Incident 2 (S3 remediation -> independent delta review transition)
- **Commit:** `b40f5071f8af0e857d35a59102eb10246daf04d6` ("docs: record WP-001 S3 remediation session, delta self-check and handoff")
- **Commit Time:** 2026-10-21 02:08:10 -03:00
- **Anomaly Detection:** Independent delta reviewer entry. Eight files corrupted:
  - 4 newly created files found truncated to 0 bytes:
    - `governance/audits/WP-001/S3-delta-review.md`
    - `governance/execution/WP-001/S3/handoff.md`
    - `governance/execution/WP-001/S3/record.json`
    - `governance/findings/WP-001/closure-table.md`
  - 4 modified files reverted toward pre-remediation (`63bd5f8`) state:
    - `governance/registers/findings.json` (1911 bytes)
    - `src/axiomlint/schema.py` (7364 bytes)
    - `tests/test_schema.py` (7969 bytes)
    - `tools/verify_local_run.py` (5288 bytes)
- **Anomaly Mtime:** 02:08:35 -03:00 (~25s after commit).

## 2. Evidence and Findings

### Smoking Gun 1: VS Code Local History in Devin Desktop
Devin Desktop (`devin-desktop`, an Electron/VS Code build) was actively running with workspace folder `file:///home/themichael/PerplexityWorkspace/axiomlint` registered under workspace storage ID `1ef9dd6a23ad249f1013abffa5d642f3`.

Inspection of `/home/themichael/.config/Devin/User/History` revealed entries recorded under VS Code's Local History feature. Every single file affected in Incident 1 and Incident 2—and NO other files from `axiomlint`—has a Local History entry with `source: "Workspace Edit"` matching the exact incident timestamps:

#### Incident 1 (01:47:45 -03:00):
- `2be59d0c/entries.json` -> `governance/execution/WP-001/S2/handoff.md`: `Cn7z.md`, 2026-10-21 01:47:45.477 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `3bda80d0/entries.json` -> `governance/audits/WP-001/S2-report.md`: `l14s.md`, 2026-10-21 01:47:45.475 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `46c8e70b/entries.json` -> `governance/audits/WP-001/S2-findings.json`: `DhDx.json`, 2026-10-21 01:47:45.473 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `-5d11d822/entries.json` -> `governance/execution/WP-001/S2/record.json`: `Fovy.json`, 2026-10-21 01:47:45.479 -03:00, `source: "Workspace Edit"`, 0 bytes.

#### Incident 2 (02:08:35 -03:00):
- `-6e8ed1a1/entries.json` -> `governance/execution/WP-001/S3/record.json`: `VGyx.json`, 2026-10-21 02:08:35.674 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `4f46e268/entries.json` -> `governance/findings/WP-001/closure-table.md`: `qBJS.md`, 2026-10-21 02:08:35.674 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `3397426b/entries.json` -> `governance/execution/WP-001/S3/handoff.md`: `yGHS.md`, 2026-10-21 02:08:35.674 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `4cd9c718/entries.json` -> `governance/audits/WP-001/S3-delta-review.md`: `0Z4f.md`, 2026-10-21 02:08:35.673 -03:00, `source: "Workspace Edit"`, 0 bytes.
- `-47333965/entries.json` -> `governance/registers/findings.json`: `161Q.json`, 2026-10-21 02:08:35.680 -03:00, `source: "Workspace Edit"`, 1911 bytes.
- `-644fa209/entries.json` -> `tools/verify_local_run.py`: `bF2S.py`, 2026-10-21 02:08:35.751 -03:00, `source: "Workspace Edit"`, 5288 bytes.
- `-e49a20c/entries.json` -> `src/axiomlint/schema.py`: `r6a6.py`, 2026-10-21 02:08:35.680 -03:00, `source: "Workspace Edit"`, 7364 bytes.
- `3e357e12/entries.json` -> `tests/test_schema.py`: `DCjb.py`, 2026-10-21 02:08:35.749 -03:00, `source: "Workspace Edit"`, 7969 bytes.

### Smoking Gun 2: Extension Host and ACP Bridge Logs
In `/home/themichael/.config/Devin/logs/20261021T011716/`:
1. In `3-Devin ACP devin-cli.log`:
   - At 04:47:44 UTC (01:47:44 local): exactly four `cognition.ai/document/didChangeDirty` notifications arrived in rapid succession.
   - At 05:08:34 UTC (02:08:34 local): exactly eight `cognition.ai/document/didChangeDirty` notifications arrived in rapid succession.
2. In `6-Antigravity LS.log`:
   - The Antigravity extension in the IDE was managing diff previews via `SetFileDiffs` (RPC `/gemini_coder.agent_ui_toolkit.iframe.AntigravityApi/SetFileDiffs`).
   - Immediately prior to 02:08:35, active diffs in the editor model were cleared (fileDiffs count decremented from 7 to 0).
3. In `vscode.git/Git.log`:
   - Rapid bursts of `git status -z -uall` occurred immediately as the files were modified on disk by the editor.

### Mechanism of Truncation / Reversion
In `/home/themichael/.config/Devin/User/settings.json`, `"files.autoSave": "afterDelay"` was configured.
When external agent tools edited/created files on disk and git commits occurred outside VS Code:
1. Devin Desktop's editor held in-memory document buffers for open/tracked files.
2. For newly created files, the in-memory buffer initially created was empty (0 bytes).
3. For modified files, the in-memory buffer held the pre-edit content.
4. When the session completed and the IDE diffs/state were dismissed or auto-save timer elapsed (~25-70s delay), VS Code executed a `Workspace Edit`, auto-saving the stale in-memory buffers back to disk and overwriting the committed on-disk files.

## 3. Remediation and Monitoring

### Remediation Applied
In `/home/themichael/.config/Devin/User/settings.json`:
- Changed `"files.autoSave": "afterDelay"` to `"files.autoSave": "off"`.
- This prevents VS Code from automatically flushing stale editor models to disk over external changes.

### Monitoring Safeguard
- Check `git status --porcelain` immediately after every commit.
- Spot-check governance and code files to verify non-zero size before and after session transitions.
