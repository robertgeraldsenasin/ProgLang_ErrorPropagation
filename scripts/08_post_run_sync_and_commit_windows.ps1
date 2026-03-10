param(
  [string]$Workbook = ".\workbook\Experiment_ProgLang_Error_Propagation_repo.xlsx",
  [string]$OutDir = ".\output",
  [string]$Spider2Root = ".\Spider2",
  [string]$RunId = "",
  [int]$Repeats = 3,
  [switch]$RunStabilityChecks,
  [string]$EvidenceTag = "",
  [string]$CommitMessage = "",
  [switch]$Push
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
  Write-Host ""
  Write-Host "==> $Message" -ForegroundColor Cyan
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (!(Test-Path $VenvPython)) {
  throw "Could not find .venv\\Scripts\\python.exe. Run scripts/07_bootstrap_external_assets_windows.ps1 first."
}

if ($RunStabilityChecks) {
  if ([string]::IsNullOrWhiteSpace($RunId)) {
    throw "-RunStabilityChecks requires -RunId."
  }
  Write-Step "Running stability checks"
  & $VenvPython scripts/06_run_stability_checks.py --run-id $RunId --spider2-root $Spider2Root --out-dir $OutDir --repeats $Repeats
}

Write-Step "Syncing workbook"
Write-Host "Close Excel before running this step."
& $VenvPython scripts/04_sync_logs_to_workbook.py --workbook $Workbook --out-dir $OutDir

Write-Step "Generating analysis artifacts"
& $VenvPython scripts/05_generate_analysis_tables.py --out-dir $OutDir

if ([string]::IsNullOrWhiteSpace($EvidenceTag)) {
  $EvidenceTag = Get-Date -Format "yyyyMMdd-HHmmss"
}
$EvidenceDir = Join-Path $RepoRoot "docs\testing-evidence\$EvidenceTag"
New-Item -ItemType Directory -Force $EvidenceDir | Out-Null

Write-Step "Copying tracked evidence"
Copy-Item "$OutDir\analysis\*" $EvidenceDir -Force -ErrorAction SilentlyContinue
Copy-Item "$OutDir\logs\*" $EvidenceDir -Force -ErrorAction SilentlyContinue
$SummaryFiles = Get-ChildItem "$OutDir\runs" -Recurse -Filter summary.json -File -ErrorAction SilentlyContinue
foreach ($Summary in $SummaryFiles) {
  $DestName = "$($Summary.Directory.Name)_summary.json"
  Copy-Item $Summary.FullName (Join-Path $EvidenceDir $DestName) -Force
}

Write-Step "Git status"
git status --short

if (-not [string]::IsNullOrWhiteSpace($CommitMessage)) {
  Write-Step "Staging and committing"
  git add .
  git commit -m $CommitMessage
  if ($Push) {
    Write-Step "Pushing to origin/main"
    git push origin main
  }
}
else {
  Write-Host "No commit made. Re-run with -CommitMessage \"...\" to commit tracked changes."
}

Write-Step "Post-run workflow complete"
Write-Host "Evidence directory: $EvidenceDir"
