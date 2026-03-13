# Error Propagation in Iterative GenAI Text-to-SQL Refinement

A runnable research repo for **manual, zero-budget or low-budget iterative Text-to-SQL testing** on the **Spider2-Lite SQLite subset** with:

- a **manual trajectory runner** for ChatGPT, Gemini, DeepSeek, and Claude browser workflows,
- a **workbook sync and seeding pipeline** so every run is documented cleanly,
- **analysis scripts** for propagation, regressions, stability, and model-level summaries,
- a **sample fixture** so the repo can be smoke-tested without downloading Spider2 first,
- the current project PDFs, continuity pack, and workbook bundled for continuity.

## What this repo is for

This project studies whether iterative SQL refinement:

1. reduces errors monotonically,
2. oscillates between failure modes,
3. or introduces regressions while trying to fix earlier mistakes.

Each executed turn is labeled as one of:

- `FormatError`
- `SyntaxError`
- `SchemaError`
- `RuntimeError`
- `Timeout`
- `WrongResult`
- `Pass`

## Recommended zero-budget model lineup

For the **main free-model comparison**, use the visible web labels:

- **OpenAI:** `GPT-5.3` on ChatGPT Free
- **Google:** `Gemini 2.5 Pro` in Google AI Studio
- **DeepSeek:** `DeepSeek-V3.2` on web/app
- **Anthropic:** `Claude Sonnet 4.6` on Claude Free

See:
- `configs/free_model_suite.yaml`
- `configs/task_pack_zero_budget.yaml`
- `configs/study_protocol_zero_budget.yaml`
- `docs/reports/comparison_report.md`
- `docs/reports/functionality_reference.md`
- `docs/reports/workbook_guide.md`

## Recommended study structure

- **Pilot pack:** 4 SQLite tasks × 4 models = 16 trajectories
- **Main pack:** 8 SQLite tasks × 4 models = 32 trajectories
- **Optional holdout pack:** 4 SQLite tasks × 4 models = 16 trajectories
- **Main turn cap:** `T_max = 4`
- **Stability checks:** 3 re-execution checks per passing run

The seeded workbook and configs in this repo are aligned to that plan.

## Repo layout

```text
.
├── configs/
├── continuity/
├── docs/
├── output/
├── paper/
├── prompts/
├── references/
├── samples/
├── scripts/
├── src/errorprop_sql/
├── tests/
└── workbook/
```

## Quick start

### Option A — smoke test with the included sample fixture

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest
```

### Option B — set up the real Spider2-Lite SQLite workflow

1. Clone the official Spider2 repo into `./Spider2`.
2. Download the local SQLite bundle into:
   `Spider2/spider2-lite/resource/databases/spider2-localdb/`
3. Validate your layout:
   ```bash
   python scripts/02_validate_spider2_layout.py --spider2-root ./Spider2 --show-local
   ```
4. Reset the workbook to a clean manual-entry state if needed:
   ```bash
   python scripts/11_reset_workbook_for_manual_entry.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx
   ```
5. Fill one `Run Plan` row with `task_id`, `model_id`, `protocol_id`, `T_max`, and `replicate`.
6. Run directly from the workbook row:
   ```bash
   python scripts/12_run_from_workbook.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx --row 5 --spider2-root ./Spider2 --out-dir ./output
   ```
7. Generate analysis tables:
   ```bash
   python scripts/05_generate_analysis_tables.py --out-dir ./output
   ```

If you still prefer the direct CLI runner, you can use:

```bash
python scripts/03_run_trajectory_manual.py \
  --model-label "gpt53-free" \
  --model-snapshot "GPT-5.3" \
  --instance-id local008 \
  --condition F2 \
  --t-max 4 \
  --spider2-root ./Spider2 \
  --out-dir ./output
```

## Manual runner workflow

The manual runner is designed for **browser-based testing** when you do not want to pay for APIs.

For each turn it will:

1. create the prompt file,
2. tell you where the prompt was saved,
3. wait for you to paste the model response,
4. extract the SQL,
5. execute it on SQLite,
6. label the turn state,
7. generate the next prompt if the run has not passed.

You finish a pasted response with a line containing only:

```text
END
```

You can also type:

```text
FILE:/path/to/model_reply.txt
```

to load the response from a file.

## Workbook usage

The workbook lives at:

- `workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx`

The main sheets are:

- `START HERE`
- `Data Entry Guide`
- `Setup Checklist`
- `Lookups`
- `Prompt Library`
- `Tasks`
- `Run Plan`
- `Turn Log`
- `Run Summary`
- `Stability Checks`
- `Metrics Dictionary`
- `Example Run`
- `Dashboard`

Use these scripts around the workbook:

- `scripts/09_repair_workbook.py` repairs formulas and refreshes `Tasks`
- `scripts/10_seed_workbook_reference_data.py` is optional if you want a preplanned study pack
- `scripts/11_reset_workbook_for_manual_entry.py` resets the workbook to blank run sheets
- `scripts/12_run_from_workbook.py` reads one Run Plan row, runs the trajectory, and syncs the workbook automatically
- `scripts/04_sync_logs_to_workbook.py` syncs logs into `Run Plan`, `Turn Log`, and `Stability Checks`
- `scripts/05_generate_analysis_tables.py` exports the CSV and PNG analysis outputs


## Final report set

The polished documentation bundle is included in:

- `docs/reports/comparison_report.pdf`
- `docs/reports/functionality_reference.pdf`
- `docs/reports/workbook_guide.pdf`

Markdown source for those reports is also included beside each PDF.

## Included continuity assets

This repo also bundles the current project material so you can keep writing and testing from one place:

- project continuity pack
- current PDFs
- SELF-DEBUGGING reference PDF
- current workbook template
- SELF-DEBUGGING figure image

## Notes

- This repo is intentionally centered on the **SQLite / local** part of Spider2-Lite because it is the cleanest path for a local undergraduate workflow.
- The scripts do **not** bundle the full official Spider2 dataset. You still need to clone and download it separately.
- The included sample fixture is only for smoke tests and CI.
- Log the **exact visible model label** shown by the UI. Do not silently remap browser labels to API identifiers.
