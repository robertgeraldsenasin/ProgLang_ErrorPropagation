# Workbook input guide

This guide matches `workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx`.

## Recommended mode

The default workbook in this repo is a **manual-entry workbook**:
- `Tasks` stays as the task manifest.
- `Run Plan` starts blank.
- `Turn Log` and `Stability Checks` are machine-filled.
- `Run Summary` and `Dashboard` are formula-driven.
- The preferred execution path is `scripts/12_run_from_workbook.py`.

## Minimal workflow

1. Reset the workbook if needed:
   - `python scripts/11_reset_workbook_for_manual_entry.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx`
2. Validate Spider2 and list valid local task IDs:
   - `python scripts/02_validate_spider2_layout.py --spider2-root ./Spider2 --show-local`
3. Fill one `Run Plan` row with at least:
   - `task_id`
   - `model_id`
   - `protocol_id`
   - `T_max`
   - `replicate`
4. Run from the sheet:
   - `python scripts/12_run_from_workbook.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx --row 5 --spider2-root ./Spider2 --out-dir ./output`
5. If the run passes, either rerun with `--run-stability-on-pass` or use `scripts/06_run_stability_checks.py`.

## Sheet-by-sheet

### Tasks
This is the task manifest, not the result log.

### Run Plan
One row = one planned trajectory.

Machine-derivable fields:
- `run_id`
- `db_name`
- `artifact_folder`
- `commit_hash` (if Git is available)
- `status`

Manual or optional audit fields:
- `operator`
- `planned_date`
- `record_file`
- `notes`

### Turn Log
Most fields are machine-filled from execution logs.
Manual add-ons:
- `screenshot_file`
- `notes`
- `review_flag`

### Run Summary
Formula-driven roll-up. Do not type over formula cells.

### Stability Checks
Machine-filled after a pass.

### Dashboard
Formula-driven study summary.

## Why the audit fields matter

- `temperature`: captures controllable randomness if the UI exposes it.
- `operator`: tells you who actually ran the loop.
- `planned_date`: time anchor for batching and free-tier limits.
- `record_file`: points to video/screenshot evidence.
- `commit_hash`: ties results to a specific repo version.
- `status`: distinguishes planned rows from completed trajectories.

## Rule of thumb

- Plan in the workbook.
- Execute with `scripts/12_run_from_workbook.py`.
- Let sync scripts fill the machine fields.
- Add only the evidence notes the machine cannot know.
