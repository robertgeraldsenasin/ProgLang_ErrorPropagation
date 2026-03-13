# Workbook, Sheets, Variables, and Analysis Mapping

## Executive summary

The workbook is the **human-readable experiment notebook** for the repository. It is not the source of truth for raw execution; raw execution lives in JSONL logs under `output/logs/`. The workbook exists to keep the study understandable, reviewable, and paper-ready.

This package fixes the earlier placeholder issues by:

- seeding `Lookups`, `Prompt Library`, `Tasks`, and `Run Plan` from the real configs,
- clearing stale placeholder rows in the working sheets,
- rebuilding `Run Summary` from active `Run Plan` rows only,
- and simplifying dashboard formulas so planned runs and logged runs are counted correctly.

## What each sheet is for

| Sheet | Role | Who fills it |
|---|---|---|
| `START HERE` | Operating order for the full study | Template, manually read |
| `Data Entry Guide` | What is manual vs script-filled | Template |
| `Setup Checklist` | Pre-run readiness checklist | Template + manual checks |
| `Lookups` | State severities, protocol meanings, model roster | Script 10 |
| `Prompt Library` | Versioned prompt texts | Script 10 |
| `Tasks` | Fixed approved task manifest for the study | Script 10 (or script 09 from Spider2) |
| `Run Plan` | One row per planned trajectory | Script 10, then script 04 updates status |
| `Turn Log` | One row per executed turn | Script 04 |
| `Run Summary` | One row per run, computed from Turn Log and Stability Checks | Workbook formulas |
| `Stability Checks` | One row per re-execution or re-prompt check | Script 06 → script 04 |
| `Metrics Dictionary` | Definitions of metrics used in the study | Template (completed in this package) |
| `Example Run` | Worked example for orientation | Template (completed in this package) |
| `Dashboard` | Lightweight top-sheet indicators | Workbook formulas |

## Why the workbook matters in this study

The repository studies **error propagation across turns**, not just final pass/fail. The workbook matters because it lets you inspect:

- whether a run improved or regressed,
- how quickly a model first passed,
- whether passing SQL stayed stable,
- and whether the planned run roster still matches what was actually executed.

## Sheet-level variable dictionary

### `Tasks`

| Variable | Why it matters | Populated by |
|---|---|---|| `task_id` | Stable Spider2-Lite instance identifier. The runner uses this to load the task and resolve the correct database/oracle. | Seeded by script 10 or repaired from Spider2 by script 09. |
| `dataset_split` | Marks the benchmark subset used in the study. | Seeded by script 10. |
| `db_name` | Logical database name, used to resolve the .sqlite file. | Seeded by script 10. |
| `db_path` | Expected local path to the SQLite database. | Seeded by script 10; validated by script 02. |
| `question` | Natural-language instruction sent to the model. | Seeded by script 10 from the curated task pack or Spider2. |
| `schema_hash / version` | Reserved field for future schema versioning or local checksum. | Manual/optional. |
| `oracle_result_file` | Gold exec-result or gold SQL file used for correctness checking. | Filled when Spider2 root is available. |
| `difficulty_band` | Optional annotation for reporting slices. | Manual/optional. |
| `pilot?` | Flags tasks used only for workflow shakedown. | Seeded by script 10. |
| `main?` | Flags tasks used in headline comparisons. | Seeded by script 10. |
| `recording_segment` | Lets you align tasks with video/audio recording segments. | Seeded by script 10; can be edited manually. |
| `notes` | Stores support-doc names or curator notes. | Seeded by script 10; editable. |

### `Run Plan`

| Variable | Why it matters | Populated by |
|---|---|---|| `run_id` | Unique trajectory ID; every artifact file, log row, and workbook row keys off this field. | Seeded by script 10; updated by script 04 if run rows are synced. |
| `batch_id` | Groups runs into pilot/main/holdout batches. | Seeded by script 10. |
| `task_id` | Links the trajectory to one row in Tasks. | Seeded by script 10. |
| `db_name` | Database associated with the task. | Seeded by script 10. |
| `model_id` | Stable study identifier for the model family and access mode. | Seeded by script 10. |
| `model_snapshot` | Exact visible UI label that the operator saw at test time. | Seeded by script 10; should be corrected manually if the provider UI changes. |
| `protocol_id` | Feedback condition used in the run: F0/F1/F2/F3. | Seeded by script 10. |
| `temperature` | Decoding temperature, kept at 0 for manual browser parity unless explicitly changed. | Seeded by script 10. |
| `reasoning_mode` | Manual-browser or other mode label for reproducibility. | Seeded by script 10. |
| `T_max` | Maximum number of turns allowed in the trajectory. | Seeded from the study protocol. |
| `replicate` | Replicate number for repeated trajectories. | Seeded by script 10. |
| `operator` | Human operator running the browser test. | Manual. |
| `planned_date` | Planned execution date. | Manual. |
| `record_file` | Optional recording filename if the session was screen-recorded. | Manual. |
| `artifact_folder` | Relative folder name for run artifacts. | Seeded by script 10. |
| `commit_hash` | Git commit used at run time. | Manual/recommended before release analysis. |
| `status` | Planned / In progress / Complete. | Seeded by script 10 and updated by script 03 + script 04. |
| `notes` | Planning notes, fallback events, UI changes, or exceptions. | Manual. |

### `Turn Log`

| Variable | Why it matters | Populated by |
|---|---|---|| `batch_id` | Inherited batch label so turns can be grouped without joining Run Plan. | Script 03 → script 04. |
| `run_id` | Primary key part 1 for turn-level logs. | Script 03 → script 04. |
| `turn_no` | Primary key part 2; chronological turn index. | Script 03 → script 04. |
| `task_id` | Task identifier repeated for easy filtering. | Script 03 → script 04. |
| `db_name` | Database name repeated for fast slicing. | Script 03 → script 04. |
| `model_id` | Model used for the trajectory. | Script 03 → script 04. |
| `protocol_id` | Feedback condition used on that run. | Script 03 → script 04. |
| `prompt_file` | Saved prompt text for this turn. | Script 03 → script 04. |
| `response_file` | Raw pasted browser response. | Script 03 → script 04. |
| `extracted_sql_file` | Extracted SQL query saved as .sql. | Script 03 → script 04. |
| `prompt_hash` | Content hash of the prompt, used for auditability. | Script 03 → script 04. |
| `exec_ms` | Execution runtime in milliseconds. | Script 03 → script 04. |
| `rows_pred` | Predicted result-table row count. | Script 03 → script 04. |
| `rows_gold` | Oracle result-table row count. | Script 03 → script 04. |
| `symdiff_rows` | Symmetric difference size between predicted and oracle rows. | Script 03 → script 04. |
| `sqlite_error` | Exact SQLite engine error when execution fails. | Script 03 → script 04. |
| `exec_state` | Turn label in {FormatError, SyntaxError, SchemaError, RuntimeError, Timeout, WrongResult, Pass}. | Script 03 → script 04. |
| `severity` | Numeric severity mapped from exec_state for transition analysis. | Workbook formula / script 04. |
| `helper_key` | run_id|turn_no helper key for formula lookups. | Workbook formula / script 04. |
| `helper_prev_key` | run_id|turn_no-1 helper key for formula lookups. | Workbook formula / script 04. |
| `prev_state` | Previous turn state for the same run. | Workbook formula / script 04. |
| `prev_severity` | Previous turn severity for the same run. | Workbook formula / script 04. |
| `state_change` | 1 if current state differs from previous state. | Workbook formula / script 04. |
| `improved` | 1 if severity decreased versus previous turn. | Workbook formula / script 04. |
| `regressed` | 1 if severity increased versus previous turn. | Workbook formula / script 04. |
| `pass_flag` | 1 if the turn reached Pass. | Workbook formula / script 04. |
| `feedback_file` | Saved feedback payload that seeded the next revision. | Script 03 → script 04. |
| `screenshot_file` | Optional screenshot evidence path. | Manual / script 04 if you populate it. |
| `recording_timestamp` | Timestamp within the operator recording. | Script 03 → script 04, editable. |
| `notes` | Free-form turn notes such as extraction mode. | Script 03 → script 04, editable. |
| `review_flag` | Manual QA marker for analyst review. | Manual. |

### `Run Summary`

| Variable | Why it matters | Populated by |
|---|---|---|| `run_id` | One-row-per-trajectory key copied from Run Plan. | Formula sheet. |
| `task_id` | Task identifier for summarization. | Formula sheet. |
| `model_id` | Model identifier for summarization. | Formula sheet. |
| `protocol_id` | Feedback condition for summarization. | Formula sheet. |
| `replicate` | Replicate ID. | Formula sheet. |
| `T_max` | Turn cap for the run. | Formula sheet. |
| `logged_turns` | How many turns were actually logged. | Formula sheet from Turn Log. |
| `first_pass_turn` | Earliest turn that reached Pass. | Formula sheet from Turn Log. |
| `final_turn` | Last turn executed. | Formula sheet from Turn Log. |
| `final_state` | Terminal state of the run. | Formula sheet from Turn Log. |
| `final_severity` | Severity of the terminal state. | Formula sheet from Turn Log. |
| `improvements` | Count of severity-improving transitions. | Formula sheet from Turn Log. |
| `regressions` | Count of severity-worsening transitions. | Formula sheet from Turn Log. |
| `oscillations` | Count of state changes across turns. | Formula sheet from Turn Log. |
| `pass_within_T` | Yes/No flag for whether the run ever passed within the cap. | Formula sheet. |
| `reexec_passes` | How many stability re-executions stayed Pass. | Formula sheet from Stability Checks. |
| `reprompt_passes` | Reserved for later reprompt stability checks. | Formula sheet from Stability Checks. |
| `status` | Planned/In progress/Complete mirror from Run Plan. | Formula sheet. |
| `analyst_note` | Manual interpretation note for paper writing. | Manual. |

### `Stability Checks`

| Variable | Why it matters | Populated by |
|---|---|---|| `run_id` | Passing trajectory being checked. | Script 06 → script 04. |
| `pass_turn` | Turn number where the original run first passed. | Script 06 → script 04. |
| `check_type` | Re-execution or Re-prompt. | Script 06 → script 04. |
| `repeat_no` | Repeat index for the stability check. | Script 06 → script 04. |
| `outcome_state` | State after rerunning the supposedly passing SQL. | Script 06 → script 04. |
| `stable_pass?` | Yes if the rerun still passes. | Script 06 → script 04. |
| `evidence_file` | SQL file used in the stability check. | Script 06 → script 04. |
| `notes` | Optional analyst note about the stability event. | Manual. |

### `Lookups` and `Prompt Library`

| Area | Why it matters | Populated by |
|---|---|---|| `exec_state / severity` | Maps each symbolic state to an ordinal severity used by workbook formulas and analysis exports. | Seeded by script 10. |
| `protocol_id / description` | Defines what F0, F1, F2, and F3 mean. | Seeded by script 10. |
| `model_id / provider / recommended_use / status` | Reference roster of approved model labels. | Seeded by script 10. |
| `yes_no / owners` | Small helper lists for validation and ownership. | Template / script 10. |
| `template_id` | Stable identifier such as T1_SQL or REV_F2. | Seeded by script 10. |
| `used_when` | Operational use of the prompt. | Seeded by script 10. |
| `version` | Prompt revision tag. In this package, v2 means the prompt includes supporting_context. | Seeded by script 10. |
| `template_text` | The exact tracked prompt text. | Seeded by script 10 from files in prompts/. |
| `required_variables` | Fields the runner must inject before sending the prompt to a model. | Seeded by script 10. |
| `notes` | Traceability note pointing back to the source file. | Seeded by script 10. |

## Which script touches which sheet

| Script | Sheets affected |
|---|---|
| `09_repair_workbook.py` | Repairs formulas/layout, can repopulate `Tasks` |
| `10_seed_workbook_reference_data.py` | Optional: `Lookups`, `Prompt Library`, `Tasks`, `Run Plan`, `Dashboard` |
| `11_reset_workbook_for_manual_entry.py` | Clears `Run Plan`, `Turn Log`, `Stability Checks`, `Run Summary`, and refreshes `Dashboard` |
| `12_run_from_workbook.py` | Reads one `Run Plan` row, runs the trajectory, and then syncs workbook fields automatically |
| `03_run_trajectory_manual.py` | Direct CLI alternative; creates JSONL logs and run artifacts |
| `06_run_stability_checks.py` | No direct workbook write; creates stability JSONL |
| `04_sync_logs_to_workbook.py` | `Run Plan`, `Turn Log`, `Stability Checks`, `Run Summary`, `Dashboard` |
| `05_generate_analysis_tables.py` | No workbook write; creates analysis CSVs/PNGs from logs |

## Why the key variables matter analytically

- `exec_state` and `severity` make turn-level failures numerically comparable.
- `prev_state`, `state_change`, `improved`, and `regressed` let you quantify oscillation and regression.
- `first_pass_turn` measures how fast a model stabilizes on a correct query.
- `rows_pred`, `rows_gold`, and `symdiff_rows` tell you whether a wrong result was “close” or structurally far from the oracle.
- `model_snapshot` prevents silent browser-model changes from contaminating comparisons.
- `prompt_hash` lets you prove that two runs actually used the same prompt text.
- `reexec_passes` separates fragile passes from robust passes.

## How graphs are documented and tested

The workbook is not where the repository computes analysis plots. Instead:

- `05_generate_analysis_tables.py` computes the CSV and PNG outputs from machine logs.
- `state_distribution_by_turn.png` visualizes how failure states evolve across turns.
- `pass_rate_by_model.png` summarizes headline performance by model.
- `transition_counts.csv` and `transition_matrix.csv` support propagation-path analysis.
- `model_summary.csv`, `protocol_summary.csv`, and `trajectory_summary.csv` support paper tables.
- `stability_summary.csv` supports the stability section.

The workbook dashboard is therefore a **tracking surface**, while the `output/analysis/` files are the **publication-analysis surface**.

## Proper workbook workflow

1. Reset the workbook to a clean manual-entry state before you start a new batch, or optionally seed a preplanned study pack if you want one.
2. Treat `Tasks` and `Run Plan` as fixed once the main comparison starts.
3. Run trajectories with script 03.
4. Sync with script 04 after each run or batch.
5. Run script 06 only for runs that passed.
6. Run script 05 after workbook sync to regenerate analysis files.
7. Copy selected evidence into `docs/testing-evidence/` before committing.

## What was fixed in this package

The previous workbook version mixed placeholders and live rows, which caused inflated counts. This package fixes that by:

- seeding real models, real prompts, and a real task pack,
- clearing stale working rows when reseeding,
- rebuilding `Run Summary` only from active `Run Plan` rows,
- and using simpler, stable dashboard formulas.

## References used in this report

1. Xinyun Chen, Maxwell Lin, Nathanael Schärli, and Denny Zhou. *Teaching Large Language Models to Self-Debug*. 2023.
2. XLANG Lab. *Spider2 repository*. 2026.
3. XLANG Lab. *Spider2-Lite README* and *Spider-Agent-Lite README*. 2026.