# Zero-Budget Free-Model Comparison and Final Study Design

## Executive summary

This package finalizes the repository as a **manual browser-based, zero-budget Text-to-SQL error-propagation study** on the **Spider2-Lite SQLite subset**. The recommended headline comparison uses four free-access browser models:

- GPT-5.3 on ChatGPT Free
- Gemini 2.5 Pro in Google AI Studio
- DeepSeek-V3.2 on the DeepSeek web/app
- Claude Sonnet 4.6 on Claude.ai Free

The repository is configured for a **4-task pilot**, an **8-task main comparison**, and an **optional 4-task holdout**, with a shared turn cap of **T_max = 4** and **3 re-execution stability checks** for every passing run.

## Why these free models are suitable

OpenAI currently states that ChatGPT Free users can send up to **10 GPT-5.3 messages every 5 hours**, after which chats automatically use a mini version. That makes GPT-5.3 usable for pilot and main manual testing, but it also makes it the tightest resource constraint in a zero-budget design.  
Source: OpenAI Help Center, “GPT-5.3 and GPT-5.4 in ChatGPT” (2026).

Google positions **Gemini 2.5 Pro** as its most advanced model for complex tasks and **Gemini 2.5 Flash-Lite** as the fastest and most budget-friendly 2.5 model. Google AI Studio documentation also states that usage is free of charge in supported regions. This makes Gemini 2.5 Pro the strongest free Google choice for the main comparison and Flash-Lite the natural fallback if rate limits or UI changes occur.  
Sources: Google Gemini models page; Google AI Studio pricing/availability pages (2026).

Anthropic states that **Claude Sonnet 4.6** is the default model on Free and Pro plans in Claude.ai. That makes it a suitable free browser baseline for iterative SQL revision.  
Source: Anthropic product announcement (2026).

DeepSeek advertises **free access to DeepSeek-V3.2** on web/app, and DeepSeek’s API documentation states that V3.2 is live on app, web, and API. That makes DeepSeek-V3.2 a strong zero-cost comparison point, although the web/app label should not be silently remapped to an API alias in the workbook.  
Sources: DeepSeek homepage; DeepSeek API docs (2026).

## Official dataset basis

The official Spider2 repository reports that **Spider 2.0-Lite contains 547 tasks total**, broken down into **214 BigQuery**, **198 Snowflake**, and **135 SQLite** tasks. The study in this package uses the **SQLite subset only** so the entire execution harness stays local and reproducible.  
Source: official Spider2 repository (2026).

The official Spider2-Lite README also requires a separate download of the **local SQLite bundle** into:

`Spider2/spider2-lite/resource/databases/spider2-localdb/`

and uses task records that include `instance_id`, `db`, `question`, and optional `external_knowledge` references.  
Sources: Spider2-Lite README; Spider-Agent-Lite README (2026).

## Final recommended study budget

### Planned run counts

- Pilot: 4 tasks × 4 models = 16 runs
- Main: 8 tasks × 4 models = 32 runs
- Main + pilot total: 48 runs
- Optional holdout: 4 tasks × 4 models = 16 extra runs

These counts are seeded directly into the workbook and mirrored in `configs/study_protocol_zero_budget.yaml`.

### Why the turn cap is 4

The SELF-DEBUGGING paper used a **maximum debugging budget of 10 turns**, but it also states that **successful debugging processes mostly ended within 3 turns**. Because this package is explicitly designed around free browser usage rather than paid APIs, the repository sets **T_max = 4**: one initial generation turn plus up to three repair turns. That preserves the self-debugging logic while staying realistic under free-tier limits, especially the ChatGPT Free GPT-5.3 cap.  
Source: Chen et al., *Teaching Large Language Models to Self-Debug*.

### Stability checks

Every run that reaches Pass should receive **3 re-execution stability checks**. This is enough to detect obvious brittle passes without making the free-model workflow too expensive.

## Final recommended model roster

| Provider | Workbook `model_id` | Visible label to log | Why it is in the final package | Main caution |
|---|---|---|---|---|
| OpenAI | `chatgpt-free-gpt-5.3` | GPT-5.3 | Strong mainstream baseline; easiest to explain in the paper | Free cap and silent mini fallback must be logged |
| Google | `gemini-2.5-pro-aistudio-free` | Gemini 2.5 Pro | Best free Google reasoning choice for SQL revision | If you switch to Flash-Lite, log it as a new row |
| DeepSeek | `deepseek-v3.2-web` | DeepSeek-V3.2 | Strong free-access reasoning/coding baseline | Web/app label should be logged exactly as seen |
| Anthropic | `claude-sonnet-4.6-free` | Claude Sonnet 4.6 | High-quality free browser reasoning baseline | Browser UI behavior may change over time |

## Curated task pack used by the package

The repository includes a curated zero-budget pack under `configs/task_pack_zero_budget.yaml`.

| Group | Task ID | Database | External knowledge |
|---|---|---|---|
| pilot | local002 | E_commerce | — |
| pilot | local003 | E_commerce | RFM.md |
| pilot | local004 | E_commerce | — |
| pilot | local007 | Baseball | — |
| main | local008 | Baseball | — |
| main | local009 | Airlines | haversine_formula.md |
| main | local010 | Airlines | haversine_formula.md |
| main | local015 | California_Traffic_Collision | — |
| main | local017 | California_Traffic_Collision | — |
| main | local018 | California_Traffic_Collision | — |
| main | local019 | WWE | — |
| main | local020 | IPL | — |
| holdout | local021 | IPL | — |
| holdout | local022 | IPL | — |
| holdout | local023 | IPL | — |
| holdout | local024 | IPL | — |
| reserve | local025 | IPL | — |
| reserve | local026 | IPL | — |
| reserve | local028 | Brazilian_E_Commerce | — |
| reserve | local031 | Brazilian_E_Commerce | — |

## Final protocol

1. Bootstrap the external assets with `scripts/07_bootstrap_external_assets_windows.ps1`.
2. Reset the workbook with `scripts/11_reset_workbook_for_manual_entry.py`, or use `scripts/10_seed_workbook_reference_data.py` only if you explicitly want a preplanned run pack.
3. Run the 4-task pilot under **F1** across all 4 models.
4. Confirm that prompts, SQL extraction, workbook sync, and stability checks behave correctly.
5. Run the 8-task main pack under **F2** across all 4 models.
6. For every passing run, execute **3 re-execution checks** with `scripts/06_run_stability_checks.py`.
7. Sync the workbook and generate analysis tables after every run block.
8. Use the optional holdout pack only after the main comparison is stable.

## What the GitHub repository should hold

### Tracked in GitHub

- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `.gitignore`
- `configs/` for model suites, study protocol, and task packs
- `prompts/` for tracked prompt templates
- `scripts/` for setup, running, syncing, repair, analysis, and seeding
- `src/errorprop_sql/` for the actual implementation
- `tests/` for smoke, metrics, workbook, and prompt-context tests
- `samples/mini_spider2/` for smoke tests without the full external dataset
- `workbook/` for the live experiment workbook
- `docs/` for workflow docs and the final report PDFs
- `assets/`, `references/`, `continuity/`, and `paper/` for continuity and reporting assets

### Not tracked in GitHub

- `Spider2/` (downloaded locally by the bootstrap script)
- `output/` raw generated artifacts and logs
- `.venv/`, IDE caches, SQLite WAL/SHM files

## Finished-paper interpretation

The package is suitable for an undergraduate or capstone paper that is explicit about scope:

- It is a **manual browser-based comparative trajectory study**, not a pure API benchmark.
- It emphasizes **trajectory behavior, regressions, and stability**, not just first-try accuracy.
- It uses a **curated SQLite subset** of Spider2-Lite for local reproducibility.
- It logs the **exact visible model label** seen in the browser at test time.

## References used in this report

1. Xinyun Chen, Maxwell Lin, Nathanael Schärli, and Denny Zhou. *Teaching Large Language Models to Self-Debug*. 2023.
2. OpenAI Help Center. *GPT-5.3 and GPT-5.4 in ChatGPT*. 2026.
3. Google. *Gemini models* and *AI Studio pricing / availability* pages. 2026.
4. Anthropic. *Claude Sonnet 4.6* announcement. 2026.
5. DeepSeek. *DeepSeek homepage* and *V3.2 API docs*. 2026.
6. XLANG Lab. *Spider2 / Spider 2.0 benchmark repository*. 2026.
7. XLANG Lab. *Spider2-Lite README* and *Spider-Agent-Lite README*. 2026.