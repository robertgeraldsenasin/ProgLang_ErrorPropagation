# New device workflow (Windows / PowerShell)

## 1) Clone your main repo

```powershell
git clone <YOUR_GITHUB_REPO_URL>
cd .\<YOUR_REPO_FOLDER>
```

## 2) Bootstrap environment + Spider2 local assets

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\07_bootstrap_external_assets_windows.ps1
```

This script will:
- create `.venv` if needed
- install `requirements.txt`
- install `gdown`
- clone `Spider2` into `.\Spider2` if missing
- remove `.\Spider2\.git` so VS Code does not treat it as a separate repo
- download `local_sqlite.zip`
- extract `.sqlite` files into `.\Spider2\spider2-lite\resource\databases\spider2-localdb`
- validate the Spider2 layout

## 3) Prepare one Run Plan row, then run it

Reset the workbook if needed:

```powershell
python scripts/11_reset_workbook_for_manual_entry.py --workbook .\workbook\Experiment_ProgLang_Error_Propagation_repo.xlsx
```

Then fill one Run Plan row and execute it:

```powershell
python scripts/12_run_from_workbook.py --workbook .\workbook\Experiment_ProgLang_Error_Propagation_repo.xlsx --row 5 --spider2-root .\Spider2 --out-dir .\output --run-stability-on-pass
```

Paste the model answer into the terminal and finish with:

```text
END
```

## 4) After the run

### If the run passed and you want stability checks too

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\08_post_run_sync_and_commit_windows.ps1 -RunStabilityChecks -RunId "<EXACT_RUN_ID>" -EvidenceTag "real-run-01"
```

### If the run failed or you want to skip stability checks

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\08_post_run_sync_and_commit_windows.ps1 -EvidenceTag "failed-run-01"
```

## 5) Commit and push tracked changes

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\08_post_run_sync_and_commit_windows.ps1 -EvidenceTag "real-run-01" -CommitMessage "Update workbook and testing evidence" -Push
```

Because `.gitignore` keeps `Spider2/`, `.venv/`, and `output/` ignored, this will stage your repo code, workbook, and tracked evidence without trying to upload the local dataset.
