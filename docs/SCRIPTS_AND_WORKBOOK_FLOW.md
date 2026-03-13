# Scripts and Workbook Flow

This document explains what each script does, how prompts are built, how pasted model responses are parsed, how correctness is decided, how SQLite is used, and how machine logs are synced into the workbook.

## High-level pipeline

1. `02_validate_spider2_layout.py` checks that the Spider2-Lite task file, gold folders, and local SQLite bundle are present.
2. `03_run_trajectory_manual.py` runs one manual Text-to-SQL trajectory.
3. The runner writes prompt, response, SQL, feedback, and JSONL log files under `output/`.
4. `04_sync_logs_to_workbook.py` copies the machine logs into the workbook and restores the formula columns.
5. `05_generate_analysis_tables.py` turns JSONL logs into CSV analysis files and a plot.
6. `06_run_stability_checks.py` re-executes a passing SQL answer and logs whether it remains a pass.
7. `09_repair_workbook.py` repairs workbook formulas/layout, fixes dashboard counters, removes template pilot rows, and can repopulate the `Tasks` sheet from a real Spider2-Lite checkout.
8. `11_reset_workbook_for_manual_entry.py` clears working sheets back to a blank operator-ready state.
9. `12_run_from_workbook.py` reads one `Run Plan` row, executes the manual trajectory, and syncs workbook fields automatically.

## Script-by-script purpose

### `scripts/01_setup_windows.ps1`
Creates a local Python virtual environment on Windows and installs the dependencies from `requirements.txt`.

### `scripts/01_setup_unix.sh`
Unix/macOS equivalent of the Windows setup script.

### `scripts/02_validate_spider2_layout.py`
Checks whether the supplied Spider2 root contains:
- `spider2-lite/`
- `spider2-lite.jsonl` or `spider2-lite.json`
- `spider2-lite/resource/databases/spider2-localdb/`
- `spider2-lite/evaluation_suite/gold/sql/`
- `spider2-lite/evaluation_suite/gold/exec_result/`

If `--show-local` is provided, it also prints the first available `local...` task IDs so you can choose valid SQLite tasks.

### `scripts/03_run_trajectory_manual.py`
Runs one iterative trajectory.

Inputs:
- model label (`gpt-5.1`, `gemini-2.5-pro`, etc.)
- task ID (`local002`, etc.)
- feedback condition (`F0`, `F1`, `F2`, `F3`)
- turn budget (`T_max`)
- Spider2 root
- output directory

Outputs:
- `output/prompts/*.txt`
- `output/responses/*.txt`
- `output/sql/*.sql`
- `output/feedback/*.txt`
- `output/logs/run_plan.jsonl`
- `output/logs/turn_log.jsonl`
- `output/runs/<RUN_ID>/summary.json`

### `scripts/04_sync_logs_to_workbook.py`
Reads the JSONL logs under `output/logs/` and writes them into:
- `Run Plan`
- `Turn Log`
- `Stability Checks`

It then rebuilds the formula columns in `Turn Log`, regenerates row formulas in `Run Summary`, and refreshes the `Dashboard` counters.

### `scripts/05_generate_analysis_tables.py`
Reads the raw JSONL logs and generates:
- `output/analysis/turn_log.csv`
- `output/analysis/transition_counts.csv`
- `output/analysis/state_distribution_by_turn.csv`
- `output/analysis/state_distribution_by_turn.png`
- `output/analysis/run_summary_from_logs.csv`
- `output/analysis/run_plan.csv`
- `output/analysis/run_plan_raw.csv`
- `output/analysis/stability_checks.csv`

This script now derives severity, improvements, regressions, and state changes directly from the logged states, and it deduplicates `run_plan.jsonl` so each run appears once in `run_plan.csv`.

### `scripts/06_run_stability_checks.py`
Only use this after a run reaches `Pass`.

The script:
1. finds the last passing turn for the selected `run_id`
2. loads the SQL file from that turn
3. executes it again on the same SQLite database
4. compares the result to the Spider2 oracle again
5. logs the repeated outcome into `output/logs/stability_checks.jsonl`

### `scripts/07_bootstrap_external_assets_windows.ps1`
Windows bootstrap for a fresh machine:
- create `.venv`
- install dependencies
- clone `Spider2`
- remove `Spider2/.git`
- download the official `local_sqlite.zip`
- extract it into `Spider2/spider2-lite/resource/databases/spider2-localdb`
- run layout validation

### `scripts/08_post_run_sync_and_commit_windows.ps1`
Convenience wrapper for the post-run steps:
- optional stability checks
- workbook sync
- analysis generation
- evidence copying into `docs/testing-evidence/`
- optional git add/commit/push

### `scripts/09_repair_workbook.py`
Repairs workbook logic without destroying your current experiment file.

It can:
- remove the template `PILOT-...` rows from the working sheets
- fix the dashboard formulas so blank formula rows do not count as hundreds of runs
- rebuild `Run Summary` formulas only for active run-plan rows
- optionally clear and repopulate `Tasks` from a real Spider2-Lite checkout

Recommended use:

```powershell
python scripts/09_repair_workbook.py --workbook .\workbook\Experiment_ProgLang_Error_Propagation_repo.xlsx --spider2-root .\Spider2 --populate-tasks
```



### `scripts/11_reset_workbook_for_manual_entry.py`
Resets the workbook to a blank manual-entry state:
- clears `Run Plan`
- clears `Turn Log`
- clears `Stability Checks`
- resets `Run Summary`
- refreshes `Dashboard`

Use this when you want to start a fresh batch without losing the reference sheets.

### `scripts/12_run_from_workbook.py`
Recommended execution entry point for the main study.

The script:
1. reads one row from `Run Plan`
2. validates that the row has at least `task_id`, `model_id`, `protocol_id`, `T_max`, and `replicate`
3. computes `run_id` if blank
4. captures the current Git commit if available
5. writes `In progress` back to `Run Plan`
6. launches the same manual prompt-response loop used by `03_run_trajectory_manual.py`
7. syncs the workbook after the run
8. optionally triggers re-execution stability checks if the run passed

This is the easiest way to keep the workbook and output logs aligned.

## How prompt creation works

The runner uses the text templates under `prompts/`.

### Turn 1 prompt
File: `prompts/turn1_sql.txt`

Placeholders:
- `{db_name}`
- `{schema_dump}`
- `{question}`

The runner loads the task from Spider2, resolves the `.sqlite` database path, introspects the database schema, and substitutes those values into the template.

### Revision prompts
Files:
- `prompts/revise_F0.txt`
- `prompts/revise_F1.txt`
- `prompts/revise_F2.txt`
- `prompts/revise_F3.txt`

Placeholders:
- `{previous_sql}`
- `{feedback_payload}`

The feedback payload is generated from the previous turn outcome.

## What happens when you paste a model response

The runner waits for your paste until it sees a line that contains only:

```text
END
```

You can also provide:

```text
FILE:path/to/response.txt
```

The response parser then tries to extract SQL in this order:
1. a fenced ```sql``` block
2. any fenced code block
3. a raw string starting with common SQL starters such as `SELECT` or `WITH`

If nothing extractable is found, the turn is labeled `FormatError`.

## How correctness is decided

### Step 1: execute the predicted SQL
The extracted SQL is executed on the resolved SQLite database file using Python's `sqlite3` module.

To avoid freezing the main process, execution runs in a child process with a timeout.

### Step 2: load the oracle answer
For the current task, the code looks for an oracle in this order:
1. a precomputed execution result in `spider2-lite/evaluation_suite/gold/exec_result/`
2. a gold SQL query in `spider2-lite/evaluation_suite/gold/sql/`

If only the gold SQL exists, the code executes the gold SQL on the same database to obtain the reference result.

### Step 3: compare prediction vs oracle
Both prediction rows and gold rows are normalized to strings.

If neither query explicitly uses `ORDER BY`, both row sets are sorted before comparison. This makes the comparison order-insensitive by default.

The comparison produces:
- exact-match result (`same`)
- predicted row count
- gold row count
- symmetric-difference row count
- sample gold rows
- sample predicted rows

### Step 4: classify the state
The turn state is assigned as follows:
- `FormatError`: no SQL could be extracted
- `Timeout`: SQL execution exceeded the timeout
- `Pass`: execution succeeded and output exactly matched the oracle
- `WrongResult`: execution succeeded but output did not match the oracle
- `SyntaxError`: execution failed with a syntax-like SQLite error
- `SchemaError`: execution failed with table/column/schema-like SQLite errors
- `RuntimeError`: execution failed for any other SQLite runtime reason

## How the feedback conditions differ

### `F0`
Minimal feedback. Only tells the model the previous attempt failed.

### `F1`
Includes SQLite engine error text when execution fails.

### `F2`
Includes output-difference feedback such as row counts and sample mismatched rows when execution succeeds but the result is wrong.

### `F3`
Same richer feedback as above, but the prompt also asks the model for a short diagnosis before returning the revised SQL.

## How the logs map into the workbook

### `output/logs/run_plan.jsonl`
One JSON object per run-plan event.

The runner writes one `In progress` entry at the start and one `Complete` entry at the end. The workbook sync deduplicates these by `run_id`, keeping the latest status row in the sheet.

### `output/logs/turn_log.jsonl`
One JSON object per executed turn.

Each row includes:
- prompt/response/SQL file paths
- execution timing
- predicted and gold row counts
- symmetric-difference row count
- SQLite error text
- execution state
- notes about the SQL-extraction mode

### `output/logs/stability_checks.jsonl`
One JSON object per re-execution or re-prompt stability check.

## Workbook sheet usage

### `Tasks`
Your experiment manifest of approved dataset questions.

Best practice now:
- populate this from the dataset using `09_repair_workbook.py --populate-tasks`
- use `approved_for_run?` and `designated_condition_set` as your manual planning columns

### `Run Plan`
One row per actual planned trajectory.

Use it for:
- `run_id`
- condition assignment
- operator
- planned date
- status
- notes

### `Turn Log`
One row per executed turn.

This is machine-filled by the sync script. Columns `R:Z` are formulas that compute severity and transition flags.

### `Run Summary`
One row per run, mapped to the corresponding `Run Plan` row. This sheet is formula-driven.

### `Stability Checks`
One row per re-execution or re-prompt stability event.

### `Dashboard`
A compact project tracker.

The dashboard formulas were repaired so the counters now use only genuinely non-empty rows. This fixes the earlier issue where formula-filled blank rows in `Run Summary` caused the workbook to show hundreds of logged runs.

## Why the workbook showed 300+ runs before

The previous workbook logic prefilled `Run Summary` formulas down to row 305, and the dashboard counted `Run Summary!A:A` with a non-empty criterion. In Excel, formula cells that display `""` can still be counted by that style of formula, so the dashboard counted many placeholder rows as real runs.

The repair script and updated sync logic fix that in two ways:
1. the dashboard now counts only rows whose displayed text length is greater than zero
2. `Run Summary` formulas are only maintained for active run-plan rows

## Suggested workflow after the repair

1. Run the workbook repair once:

```powershell
python scripts/09_repair_workbook.py --workbook .\workbook\Experiment_ProgLang_Error_Propagation_repo.xlsx --spider2-root .\Spider2 --populate-tasks
```

2. Run a real manual trajectory.
3. Sync the workbook.
4. If the run passes, run stability checks.
5. Sync again.
6. Generate analysis outputs.
7. Copy selected evidence into `docs/testing-evidence/`.
