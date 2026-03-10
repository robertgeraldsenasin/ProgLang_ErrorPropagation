# Testing workflow

## Core loop

1. Pick a task from `Tasks` / `Run Plan`.
2. Run the manual trajectory script.
3. Paste the model output back into the terminal.
4. Let the script execute the SQL and label the error state.
5. Repeat until `Pass` or `T_max`.
6. Sync logs to workbook.
7. Run analysis scripts.
8. If the run reached `Pass`, perform stability checks.

## Standard CLI

```bash
python scripts/03_run_trajectory_manual.py \
  --model-label "gemini-2.5-pro" \
  --instance-id local056 \
  --condition F2 \
  --t-max 5 \
  --spider2-root ./Spider2 \
  --out-dir ./output
```

## Feedback conditions

- `F0`: minimal PASS/FAIL only
- `F1`: execution error text when present
- `F2`: output-difference summary
- `F3`: self-debug style diagnosis + revision

## Output folders

The runner writes into:

```text
output/
├── prompts/
├── responses/
├── sql/
├── feedback/
├── logs/
└── analysis/
```

## Recommended sequence for a real study

1. Run pilot tasks first.
2. Freeze prompt templates.
3. Freeze task manifest.
4. Freeze main model set.
5. Only then start the main trajectories.

## Recording discipline

Save:
- prompt files,
- raw model outputs,
- extracted SQL,
- screenshots when useful,
- recording timestamp or screen recording filename.

That is what makes the trajectories auditable later.
