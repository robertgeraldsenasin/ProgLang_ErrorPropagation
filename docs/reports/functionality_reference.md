# Repository Functionality, Script Reference, and Correctness Pipeline

## Executive summary

This report explains how the repository works end to end: how prompts are created, how pasted browser responses are turned into SQL files, how SQL is executed and checked against Spider2-Lite oracles, how workbook rows are synchronized, and how analysis tables and graphs are generated.

## Architecture overview

The repository implements a **manual SELF-DEBUGGING-style generate–execute–revise loop** for Text-to-SQL. The logic is:

1. Load one Spider2-Lite task.
2. Resolve the correct SQLite database.
3. Dump the schema.
4. Load support documents referenced in `external_knowledge`.
5. Render a prompt file.
6. Wait for the operator to paste a model response.
7. Extract SQL from that response.
8. Execute the SQL on SQLite with a timeout.
9. Compare the returned rows to the oracle result.
10. Assign an error state.
11. Generate the next feedback payload if the run did not pass.
12. Log everything to machine-readable JSONL.
13. Sync the JSONL logs into the workbook.
14. Export analysis CSVs and PNG charts.

## Top-level repository folders

| Folder / file | What it should contain | Why it is tracked |
|---|---|---|
| `configs/` | Model suite, task pack, and protocol YAML files | Keeps the study design explicit and versioned |
| `prompts/` | The exact initial and revision prompt templates | Keeps prompting auditable |
| `scripts/` | User-facing automation entry points | Gives a one-command workflow |
| `src/errorprop_sql/` | Core implementation | Contains the actual experiment logic |
| `tests/` | Smoke tests and regression tests | Prevents workbook/script drift |
| `samples/mini_spider2/` | Tiny local fixture | Allows smoke tests without the full external dataset |
| `workbook/` | Final experiment notebook | Holds planning, logging, and interpretation surfaces |
| `docs/` | Workflow guides and final reports | Makes the repo usable on new devices |
| `assets/` and `references/` | Figures and PDF references | Supports paper writing and documentation |
| `Spider2/` | External dataset clone | **Local only; not tracked** |
| `output/` | Generated run artifacts | **Local only; not tracked** |

## Script-by-script reference

| Script | Purpose | Inputs | Outputs | When to run |
|---|---|---|---|---|
| `01_setup_windows.ps1` | Creates `.venv` and installs requirements on Windows | Python executable | Local environment | First-time local setup |
| `01_setup_unix.sh` | Unix/macOS equivalent of script 01 | Python executable | Local environment | First-time setup on Unix |
| `02_validate_spider2_layout.py` | Confirms that Spider2-Lite and local SQLite files exist | `--spider2-root` | Console validation report | Before any real run |
| `03_run_trajectory_manual.py` | Direct CLI runner for one task/model/protocol | model label, task ID, protocol, turn cap, Spider2 root | Prompt/response/SQL/feedback files plus JSONL logs | Use for smoke tests or advanced manual runs |
| `04_sync_logs_to_workbook.py` | Syncs machine logs into the workbook | workbook path, output dir | Updated workbook | After every run block |
| `05_generate_analysis_tables.py` | Builds CSV summaries and PNG charts | output dir | analysis CSVs and PNGs | After workbook sync |
| `06_run_stability_checks.py` | Re-executes the final passing SQL | run ID, Spider2 root, repeats | stability JSONL rows | Only after Pass |
| `07_bootstrap_external_assets_windows.ps1` | New-device bootstrap for venv + Spider2 + local DB + workbook seed | optional paths and refresh flags | Ready-to-run local setup | First run on a new Windows device |
| `08_post_run_sync_and_commit_windows.ps1` | Wraps stability checks, workbook sync, analysis, evidence copying, and optional Git commit | workbook, output, run ID | Updated workbook, docs/testing-evidence copies | After a run or batch |
| `09_repair_workbook.py` | Repairs formulas/layout and can repopulate tasks | workbook, optional Spider2 root | Repaired workbook | When workbook placeholders drift |
| `10_seed_workbook_reference_data.py` | Optional seeding of models, prompts, tasks, and planned runs | workbook, configs, optional Spider2 root | Preplanned workbook | Only if you want a seeded study pack |

## Core source modules

| Module | Main responsibility |
|---|---|
| `task_loader.py` | Loads Spider2-Lite tasks, finds the task file, resolves SQLite paths, validates layout |
| `schema_utils.py` | Dumps the SQLite schema into prompt-ready text |
| `prompt_context.py` | Resolves `external_knowledge` files and injects support docs into prompts |
| `runner.py` | Orchestrates the full manual trajectory loop and stability checks |
| `sql_extract.py` | Extracts SQL from fenced `sql` blocks, generic fences, or raw SQL output |
| `executor.py` | Executes SQLite queries with a timeout in a child process |
| `oracle.py` | Loads oracle results from `gold/exec_result` or executes `gold/sql` and compares rows |
| `states.py` | Classifies turn states and maps them to severity values |
| `feedback.py` | Builds F0/F1/F2/F3 feedback payloads |
| `metrics.py` | Generates analysis CSVs and PNG charts from JSONL logs |
| `workbook_sync.py` | Repairs workbook formulas and writes machine logs into sheets |
| `workbook_seed.py` | Seeds the workbook with models, prompts, tasks, and planned runs |
| `utils.py` | Shared helpers for JSONL, hashing, row normalization, directories, and safe file names |

## How prompt creation works

### Turn 1

The runner loads `prompts/turn1_sql.txt` and injects:

- `{db_name}`
- `{schema_dump}`
- `{supporting_context}`
- `{question}`

`schema_dump` comes from the actual SQLite file.  
`supporting_context` comes from `external_knowledge` files resolved by `prompt_context.py`.

### Revision turns

The runner loads `prompts/revise_F0.txt`, `revise_F1.txt`, `revise_F2.txt`, or `revise_F3.txt` depending on the protocol and injects:

- `{db_name}`
- `{schema_dump}`
- `{supporting_context}`
- `{question}`
- `{previous_sql}`
- `{feedback_payload}`

The revision prompts are self-contained so the browser model does not need earlier hidden chat context to understand the task.

## How the pasted response is processed

The runner waits for manual input until the operator enters either:

- a line containing only `END`, or
- `FILE:/path/to/model_reply.txt`

`sql_extract.py` then tries extraction in this order:

1. fenced ```sql``` block
2. generic fenced code block
3. raw SQL starting with `SELECT`, `WITH`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, or `DROP`

If none of these work, the turn is labeled `FormatError`.

## How the repository decides whether a query is correct

1. `executor.py` runs the extracted SQL against the target SQLite database with a timeout.
2. `oracle.py` loads the official oracle result:
   - first from `spider2-lite/evaluation_suite/gold/exec_result/<instance_id>.*` when available,
   - otherwise from `gold/sql/<instance_id>.sql`, which is executed locally.
3. The predicted result rows and oracle rows are normalized.
4. If neither query explicitly uses `ORDER BY`, rows are compared as sorted multisets.
5. If the rows match exactly, the turn is `Pass`.
6. If execution succeeds but the rows differ, the turn is `WrongResult`.
7. If execution fails, `states.py` pattern-matches the engine error into `SyntaxError`, `SchemaError`, or `RuntimeError`; timeout becomes `Timeout`.

This means correctness is **execution-grounded**, not inferred from the model’s own natural-language explanation.

## How the JSONL logs become workbook rows

- `03_run_trajectory_manual.py` appends rows to (and `12_run_from_workbook.py` wraps the same loop when you execute directly from the workbook):
  - `output/logs/run_plan.jsonl`
  - `output/logs/turn_log.jsonl`
- `06_run_stability_checks.py` appends rows to:
  - `output/logs/stability_checks.jsonl`
- `04_sync_logs_to_workbook.py` upserts those JSONL rows into:
  - `Run Plan`
  - `Turn Log`
  - `Stability Checks`

It then restores the formula columns in `Turn Log`, rebuilds `Run Summary`, and resets `Dashboard`.

## How analysis exports are produced

`05_generate_analysis_tables.py` reads the JSONL logs and writes:

- `turn_log.csv`
- `transition_counts.csv`
- `transition_matrix.csv`
- `state_distribution_by_turn.csv`
- `state_distribution_by_turn.png`
- `run_summary_from_logs.csv`
- `model_summary.csv`
- `protocol_summary.csv`
- `trajectory_summary.csv`
- `pass_rate_by_model.png`
- `run_plan.csv`
- `run_plan_raw.csv`
- `stability_checks.csv`
- `stability_summary.csv`

These artifacts are used for paper tables, plots, and evidence snapshots.

## How to test the repository properly

### Unit and regression tests

Run:

```bash
pytest -q
```

The package includes these checks:

| Test file | What it verifies |
|---|---|
| `test_sql_extract.py` | SQL extraction modes and failure cases |
| `test_sample_runner.py` | Sample fixture layout and basic pass/wrong-result behavior |
| `test_metrics.py` | CSV/PNG analysis export generation |
| `test_workbook_sync.py` | Workbook sync formulas and dashboard logic |
| `test_prompt_context.py` | External-knowledge document resolution |
| `test_workbook_seed.py` | Workbook seeding for lookups, prompts, tasks, and run plan |

### Smoke test without Spider2

Use the bundled sample fixture:

1. Run one manual trajectory against `samples/mini_spider2`.
2. Sync the workbook.
3. Run stability checks.
4. Generate analysis tables.

### Real dataset validation

Before any real trajectory, run:

```powershell
python scripts/02_validate_spider2_layout.py --spider2-root .\Spider2 --show-local
```

## New-device workflow

1. Clone your GitHub repo.
2. Run `scripts/07_bootstrap_external_assets_windows.ps1`.
3. Validate the local Spider2 layout.
4. Fill a `Run Plan` row and run `scripts/12_run_from_workbook.py` for the pilot tasks.
5. Run `scripts/08_post_run_sync_and_commit_windows.ps1` after each run or run block.

## References used in this report

1. Xinyun Chen, Maxwell Lin, Nathanael Schärli, and Denny Zhou. *Teaching Large Language Models to Self-Debug*. 2023.
2. XLANG Lab. *Spider2 repository*. 2026.
3. XLANG Lab. *Spider2-Lite README* and *Spider-Agent-Lite README*. 2026.