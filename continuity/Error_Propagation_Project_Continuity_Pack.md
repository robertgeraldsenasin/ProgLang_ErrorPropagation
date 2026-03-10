
# Project Continuity Pack
## Error Propagation in Iterative GenAI Text-to-SQL Refinement

This file is a complete handoff for the current project so a new chat can resume without reconstructing the full conversation.

## 1. Final project direction
- Current paper topic: **Error Propagation in Iterative GenAI Text-to-SQL Refinement**
- Main experimental dataset: **Spider2-Lite**, restricted to the **SQLite / local subset**
- Main methodological anchor: **SELF-DEBUGGING**
- Supporting references for debugging / regression / evaluation framing:
  - **DebugBench**
  - **QuixBugs / Codex-on-QuixBugs lineage**
  - **Spider2 / Spider2-Lite**

### Why the scope changed
The project began as a broader “iterative GenAI code refinement” study, then was narrowed to **Text-to-SQL** because:
- it is easier to execute and score locally,
- Spider2-Lite provides a realistic benchmark,
- trajectory-level SQL errors are easy to label and analyze,
- this keeps the paper tighter and more defensible for an undergraduate CS project.

## 2. Core thesis of the paper
The paper studies whether iterative SQL refinement:
1. reduces errors monotonically,
2. oscillates between failure modes,
3. or introduces new regressions while trying to fix old ones.

The project now treats each turn as an observable **error state** rather than only “correct / incorrect”.

### Current error-state set
- FormatError
- SyntaxError
- SchemaError
- RuntimeError
- Timeout
- WrongResult
- Pass

## 3. Current status of the paper
### Most relevant writing artifacts already created
- `main_v8.tex`
- `main_v8.pdf`
- `Overleaf_Project_Error_Propagation_v8.zip`
- `Error_Propagation_in_GenAI (2).pdf`

### Supporting deliverables already created
- `Experiment_Logbook_Template_v7.xlsx` ← current best workbook
- `spider2_sqlite_starter_kit_manual.zip` ← current best starter kit for free web-model testing
- `Testing_Start_Guide_and_Logbook_Explanation.pdf`
- `Spider2Lite_Experiment_Playbook.pdf`

### Paper status
Already drafted / revised:
- title and scope
- abstract
- introduction
- related work
- research questions
- materials and methods direction
- feedback protocols
- metric definitions
- testing workflow

Still pending after experiments:
- actual results
- tables/figures from logs
- threats to validity grounded in observations
- conclusion based on measured outcomes

## 4. Finalized experimental design
### Experimental unit
A single run is a **trajectory**:
(task_id, model_label, feedback_condition, replicate_id)

### Iteration budget
- Current working recommendation: **T_max = 5**
- Stop early when the state becomes **Pass**

### Feedback conditions
- **F0** Minimal: PASS / FAIL only
- **F1** Engine error feedback: PASS / FAIL + SQLite engine error text
- **F2** Output-diff feedback: PASS / FAIL + row-count mismatch + sample rows
- **F3** SELF-DEBUG-style diagnosis: short diagnosis first, then revised SQL

### Metrics
#### Per-turn
- error_state
- severity
- runtime_ms
- predicted_row_count
- gold_row_count
- symmetric_difference_rows
- regression_flag

#### Per-trajectory
- Pass@T
- time_to_first_pass
- number_of_state_changes
- number_of_regressions
- divergence rate
- stability rate

### Stability tests
If a run reaches Pass:
- re-execute the final SQL multiple times,
- optionally re-prompt under a tiny perturbation,
- check whether it remains Pass.

## 5. Current recommended model set
### Practical models for free/manual testing
- `chatgpt-free-gpt-5.2`
- `gemini-web-2.5-pro`
- `deepseek-web-chat`

These are **labels for logging**, not guaranteed API snapshot IDs. If the UI shows a more precise model name, record it exactly.

### Why these models were chosen
- SELF-DEBUGGING uses GPT-family models as iterative debugging references.
- Spider2 reports modern strong baselines such as GPT-4o, Claude-3.5-Sonnet, and DeepSeek-V3.
- Gemini is relevant from recent Text-to-SQL evaluation work.
- Free web versions are realistic for the current budget.

## 6. Dataset and folder decisions
### Main dataset file
- `Spider2/spider2-lite/spider2-lite.jsonl`

### Which tasks to use
Use only **local / SQLite tasks** whose `instance_id` begins with `local...`.

### Example task already used in planning
- `local056`
- database id: `sqlite-sakila`

Important clarification:
- `sqlite-sakila` is **not a separate dataset**.
- It is the **database id** of a Spider2-Lite SQLite instance.

### Canonical local DB folder
- `Spider2/spider2-lite/resource/databases/spider2-localdb/`

## 7. Best current workflow for the team
Because the team plans to use the **free web versions** of ChatGPT, Gemini, and DeepSeek, the cleanest workflow is:

### Local side (VS Code + Python)
The local scripts handle:
- task loading,
- schema extraction,
- prompt generation,
- SQL extraction,
- SQLite execution,
- error-state labeling,
- metric logging.

### Browser side (manual)
The browser is used only to:
- paste the prompt into the model,
- collect the model reply,
- paste the reply back into the terminal.

This avoids API costs and still keeps the experiment traceable.

## 8. Exact Windows setup flow
### Install first
- Git for Windows
- Python 3.11
- VS Code
- Optional: SQLite CLI

### Setup command from the starter-kit root
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\01_setup_windows.ps1
```

Common mistake that happened:
```powershell
git .\scripts\01_setup_windows.ps1
```
That is wrong because the script is a PowerShell script, not a Git command.

### Activate the virtual environment (from starter-kit root)
```powershell
.\Spider2\.venv\Scripts\Activate.ps1
```

If the prompt already shows `(.venv)`, the environment is already active.

### If `pandas` is missing
Use:
```powershell
.\Spider2\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
python -c "import pandas; print(pandas.__version__)"
```

## 9. Path rules that caused confusion
### If you are in the starter-kit root
Example:
`C:\Users\dell\Downloads\spider2_sqlite_starter_kit>`

Use:
- scripts → `.\scripts\...`
- Spider2 root → `.\Spider2`
- output → `.\output`

### If you are inside the `Spider2` folder
Example:
`C:\Users\dell\Downloads\spider2_sqlite_starter_kit\Spider2>`

Use:
- scripts → `..\scripts\...`
- Spider2 root → `.`
- output → `..\output`

### If PowerShell shows `>>`
That means multi-line continuation mode.
Fix:
- press **Ctrl + C**
- run one command at a time

## 10. Exact commands to resume from the latest troubleshooting point
From the **starter-kit root**:

```powershell
.\Spider2\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
python -c "import pandas; print(pandas.__version__)"
python .\scripts\03_run_trajectory_manual.py --model-label "chatgpt-free-gpt-5.2" --instance-id local056 --condition F1 --t-max 5 --spider2-root .\Spider2 --out-dir .\output
```

What happens next:
1. the script creates a prompt file,
2. you open it in VS Code,
3. copy the prompt into ChatGPT / Gemini / DeepSeek,
4. copy the model reply,
5. paste it back into the terminal,
6. the script executes the SQL and labels the turn,
7. if not Pass, it builds the next prompt automatically.

## 11. Prompt templates currently in use
### Turn 1
```text
You are a data analyst. Produce a single SQLite-compatible SQL query that answers the question.
Rules:
- Output ONLY the SQL query inside one ```sql``` code block.
- Do not include explanations.
- Use only tables/columns that exist in the provided schema.

Database: {db_name}
Dialect: SQLite

Schema:
{schema_dump}

Question:
{question}

Return ONE SQL query only.
```

### Turn k (revision)
```text
Previous SQL:
```sql
{previous_sql}
```

Execution feedback:
{feedback_payload}

Revise the SQL to correctly answer the question.
Return ONE SQL query only (SQLite).
```

### Feedback payload patterns
#### F1
```text
Execution failed.
SQLite error:
{error_message}
```

#### F2
```text
Query executed but output is incorrect.
Gold row_count = {gold_n}
Pred row_count = {pred_n}
Example gold rows: ...
Example predicted rows: ...
```

#### F3
```text
First write 2–4 bullet points diagnosing why the SQL is wrong.
Then output the corrected SQL only.
```

## 12. Workbook usage
### Current best workbook
- `Experiment_Logbook_Template_v7.xlsx`

### Key sheets
- `START HERE`
- `Setup Checklist`
- `Tasks`
- `Prompt Library`
- `Run Plan`
- `Turn Log`
- `Run Summary`
- `Stability Checks`
- `Metrics Dictionary`
- `Dashboard`

### Minimum fields that must always be logged
- task_id
- db_name
- model_label
- condition
- replicate
- turn_index
- prompt_file
- raw_response_file
- extracted_sql_file
- error_state
- runtime_ms
- predicted_row_count
- gold_row_count
- pass_flag

## 13. Common troubleshooting already encountered
### Git works in normal PowerShell but not in VS Code
Cause:
- VS Code launched before PATH updated.

Fix:
- restart VS Code, or
- run setup from normal PowerShell.

### Wrongly prefixing scripts with `git`
Wrong:
```powershell
git .\scripts\01_setup_windows.ps1
```
Correct:
```powershell
.\scripts\01_setup_windows.ps1
```

### Activating from the wrong folder
If already inside `Spider2`, use:
```powershell
.\.venv\Scripts\Activate.ps1
```
not:
```powershell
.\Spider2\.venv\Scripts\Activate.ps1
```

### `pandas` missing
Cause:
- venv not active, or requirements not installed.

### PowerShell `>>`
Cause:
- incomplete pasted block.

## 14. Most important files to keep using
### Paper / writing
- `main_v8.tex`
- `main_v8.pdf`
- `Overleaf_Project_Error_Propagation_v8.zip`
- `Error_Propagation_in_GenAI (2).pdf`

### Testing / methods
- `spider2_sqlite_starter_kit_manual.zip`
- `Experiment_Logbook_Template_v7.xlsx`
- `Testing_Start_Guide_and_Logbook_Explanation.pdf`
- `Spider2Lite_Experiment_Playbook.pdf`

### References
- `2304.05128v2.pdf` ← SELF-DEBUGGING
- `2024.findings-acl.247.pdf` ← DebugBench
- `3674805.3690758.pdf` ← QuixBugs / debugging support lineage

## 15. Resume instructions for a new chat
If this project is resumed elsewhere, upload at least:
1. this continuity pack,
2. `main_v8.tex` or `Overleaf_Project_Error_Propagation_v8.zip`,
3. `Experiment_Logbook_Template_v7.xlsx`,
4. `spider2_sqlite_starter_kit_manual.zip` if testing needs to continue.

Then say:

> Resume the Error Propagation in Iterative GenAI Text-to-SQL Refinement project from this continuity pack. Use Spider2-Lite SQLite, the manual runner workflow, and the current Materials and Methods direction.

