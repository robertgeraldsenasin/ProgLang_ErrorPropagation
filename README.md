# Error Propagation in Iterative GenAI Text-to-SQL Refinement

A runnable research repo for **manual or low-cost iterative Text-to-SQL testing** on the **Spider2-Lite SQLite subset** with:

- a **manual trajectory runner** for ChatGPT / Gemini / DeepSeek web or API-assisted workflows,
- a **workbook sync pipeline** so every run is documented cleanly,
- **analysis scripts** for propagation, regressions, and stability,
- a **sample fixture** so the repo can be smoke-tested without downloading Spider2 first,
- the current project PDFs / continuity pack / workbook bundled for continuity.

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

## Recommended model lineup

For the **main paper run**, use stable, reproducible API identifiers where possible:

- **OpenAI:** `gpt-5.1`
- **Google:** `gemini-2.5-pro`
- **DeepSeek:** `deepseek-reasoner`

For **budget-sensitive replication / ablations**:

- **OpenAI:** `gpt-5-mini`
- **Google:** `gemini-2.5-flash-lite`
- **DeepSeek:** `deepseek-chat`

For **manual browser testing**, log the **exact UI label shown** at test time and store it in the workbook. Do not silently map web/app labels to API snapshot IDs.

See:

- `docs/MODEL_SELECTION.md`
- `configs/model_presets.yaml`

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

### Option B — use the real Spider2-Lite SQLite subset

1. Clone the official Spider2 repo.
2. Put the local SQLite bundle under:
   `Spider2/spider2-lite/resource/databases/spider2-localdb/`
3. Validate your layout:
   ```bash
   python scripts/02_validate_spider2_layout.py --spider2-root ./Spider2
   ```
4. Run a manual trajectory:
   ```bash
   python scripts/03_run_trajectory_manual.py \
     --model-label "gpt-5.1" \
     --instance-id local056 \
     --condition F1 \
     --t-max 5 \
     --spider2-root ./Spider2 \
     --out-dir ./output
   ```
5. Sync logs into the workbook:
   ```bash
   python scripts/04_sync_logs_to_workbook.py \
     --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx \
     --out-dir ./output
   ```
6. Generate analysis tables:
   ```bash
   python scripts/05_generate_analysis_tables.py --out-dir ./output
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

It includes:

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

The sync script fills `Run Plan`, `Turn Log`, and `Stability Checks` from machine logs.  
You still use the workbook to:

- plan batches,
- record operator / recording notes,
- review failed runs,
- maintain the dashboard as the live experiment notebook.

## Included project continuity assets

This repo also bundles the current project material so you can keep writing and testing from one place:

- project continuity pack
- current PDFs
- SELF-DEBUGGING reference PDF
- current workbook template
- SELF-DEBUGGING figure image

## Notes

- This repo is intentionally centered on the **SQLite / local** part of Spider2-Lite because it is the cleanest path for a local undergraduate workflow.
- The scripts do **not** bundle the full official Spider2 dataset. You still need to clone/download it separately.
- The included sample fixture is only for smoke tests and CI.

## Suggested GitHub repo name

`error-propagation-text2sql-refinement`
