# Local VS Code + GitHub workflow

## 1) Open the repo in VS Code
1. Extract the ZIP.
2. Open VS Code.
3. Go to **File -> Open Folder**.
4. Select the extracted repo folder.
5. Open **Terminal -> New Terminal**.

## 2) Create the Python environment
Recommended Python: **3.11**.

### Windows PowerShell
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3) Point VS Code to the right interpreter
Use **Python: Select Interpreter** and choose `.venv`.

Verify:
```bash
python --version
python -c "import pandas, openpyxl, matplotlib, yaml; print('deps ok')"
```

## 4) Smoke test the repo
```bash
python -m pytest -q
```

## 5) Run one local dry run with the included sample fixture
Use the direct runner for the smoke test:

```bash
python scripts/03_run_trajectory_manual.py \
  --model-label "sample-gpt" \
  --instance-id local001 \
  --condition F1 \
  --t-max 4 \
  --spider2-root ./samples/mini_spider2 \
  --out-dir ./output
```

When the terminal asks for the model reply, paste the model output and end with `END`, or use:
```text
FILE:/absolute/or/relative/path/to/reply.txt
```

## 6) For real runs, prefer the workbook-driven workflow
1. Reset the workbook if needed:
```bash
python scripts/11_reset_workbook_for_manual_entry.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx
```
2. Fill one `Run Plan` row.
3. Execute that row:
```bash
python scripts/12_run_from_workbook.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx --row 5 --spider2-root ./Spider2 --out-dir ./output
```

## 7) Run stability checks after a passing run
```bash
python scripts/06_run_stability_checks.py \
  --run-id LOCAL001-GPT-5-1-F1-R1 \
  --spider2-root ./samples/mini_spider2 \
  --out-dir ./output \
  --repeats 3
```

Then sync the workbook again.

## 8) Generate analysis outputs
```bash
python scripts/05_generate_analysis_tables.py --out-dir ./output
```

## 9) Move to the real Spider2-Lite SQLite subset
Validate first:
```bash
python scripts/02_validate_spider2_layout.py --spider2-root ./Spider2
```

Run a real task from the workbook:
```bash
python scripts/12_run_from_workbook.py --workbook ./workbook/Experiment_ProgLang_Error_Propagation_repo.xlsx --row 5 --spider2-root ./Spider2 --out-dir ./output --run-stability-on-pass
```

## 10) Commit and push to GitHub
```bash
git init
git branch -M main
git add .
git commit -m "Initial local setup and tested repo"
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## 11) Important note on documentation files
The repo currently ignores most of `output/`.
If you want screenshots, analysis plots, or notes on GitHub, save them under a tracked folder such as:
- `docs/testing-evidence/`
- `docs/screenshots/`
- `docs/notes/`
