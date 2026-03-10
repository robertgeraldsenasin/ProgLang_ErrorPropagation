# Workbook input guide

This guide matches `workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx`.

## Sheet-by-sheet

### START HERE
Read first. It gives the order of use.

### Data Entry Guide
Fast reference for what is manual vs. script-generated.

### Setup Checklist
Manual entry:
- owner
- status
- evidence / path
- checked on
- notes

### Lookups
Mostly fixed.
Update only if your official model roster changes.

### Prompt Library
Keep approved prompt templates here.
Version every prompt change.

### Tasks
Manual entry:
- task_id
- db_name
- db_path (if you want explicit path logging)
- question
- schema version
- oracle result file
- difficulty band
- pilot/main flags
- notes

### Run Plan
Manual or semi-manual entry before execution:
- run_id
- batch_id
- task_id
- db_name
- model_id
- model_snapshot
- protocol_id
- temperature
- reasoning_mode
- T_max
- replicate
- operator
- planned_date
- record_file
- artifact_folder
- commit_hash
- status
- notes

### Turn Log
Most of this can be filled by `scripts/04_sync_logs_to_workbook.py`.

Manual review fields after sync:
- notes
- review_flag
- optional screenshot path if you keep screenshots outside the output folder

### Run Summary
Formula-driven.
Add analyst notes if needed.

### Stability Checks
Can be machine-filled for re-execution checks.
Manual notes may still be useful for re-prompt checks.

### Dashboard
Formula-driven. Do not type into KPI cells.

## Rule of thumb

- Plan in the workbook.
- Execute with the scripts.
- Sync logs back into the workbook.
- Review in the workbook.
