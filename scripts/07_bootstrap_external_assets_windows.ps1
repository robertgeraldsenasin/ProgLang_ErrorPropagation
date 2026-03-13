param(
  [string]$Python = "python",
  [string]$Spider2Root = ".\Spider2",
  [string]$Spider2RepoUrl = "https://github.com/xlang-ai/Spider2.git",
  [string]$Spider2LocalDbDriveId = "1coEVsCZq-Xvj9p2TnhBFoFTsY-UoYGmG",
  [switch]$RefreshSpider2,
  [switch]$RefreshLocalDb,
  [switch]$SkipValidation,
  [string]$Workbook = ".\workbook\Experiment_ProgLang_Error_Propagation_repo.xlsx"
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
  Write-Host ""
  Write-Host "==> $Message" -ForegroundColor Cyan
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Step "Preparing Python environment"
if (!(Test-Path ".venv")) {
  & $Python -m venv .venv
}
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (!(Test-Path $VenvPython)) {
  throw "Could not find .venv\\Scripts\\python.exe."
}
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt
& $VenvPython -m pip install gdown

$Spider2RootResolved = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Spider2Root))
$Spider2LocalDbDir = Join-Path $Spider2RootResolved "spider2-lite\resource\databases\spider2-localdb"
$Spider2LocalZip = Join-Path $Spider2RootResolved "spider2-lite\resource\local_sqlite.zip"
$Spider2GitDir = Join-Path $Spider2RootResolved ".git"

Write-Step "Cloning or refreshing Spider2"
if ($RefreshSpider2 -and (Test-Path $Spider2RootResolved)) {
  Remove-Item -Recurse -Force $Spider2RootResolved
}
if (!(Test-Path $Spider2RootResolved)) {
  git clone $Spider2RepoUrl $Spider2RootResolved
}
if (Test-Path $Spider2GitDir) {
  Remove-Item -Recurse -Force $Spider2GitDir
}

Write-Step "Downloading Spider2 local SQLite bundle"
New-Item -ItemType Directory -Force (Split-Path $Spider2LocalZip -Parent) | Out-Null
if ($RefreshLocalDb -or !(Test-Path $Spider2LocalZip)) {
  & $VenvPython -m gdown "https://drive.google.com/uc?id=$Spider2LocalDbDriveId" -O $Spider2LocalZip
}

Write-Step "Extracting local SQLite bundle"
if ($RefreshLocalDb -and (Test-Path $Spider2LocalDbDir)) {
  Remove-Item -Recurse -Force $Spider2LocalDbDir
}
New-Item -ItemType Directory -Force $Spider2LocalDbDir | Out-Null
Expand-Archive -LiteralPath $Spider2LocalZip -DestinationPath $Spider2LocalDbDir -Force

# Normalize nested extraction layouts by moving .sqlite files to spider2-localdb root.
$RootPath = (Resolve-Path $Spider2LocalDbDir).Path
$SqliteFiles = Get-ChildItem -Path $Spider2LocalDbDir -Recurse -Filter *.sqlite -File -ErrorAction SilentlyContinue
foreach ($File in $SqliteFiles) {
  if ($File.DirectoryName -ne $RootPath) {
    $Destination = Join-Path $Spider2LocalDbDir $File.Name
    Move-Item -LiteralPath $File.FullName -Destination $Destination -Force
  }
}

$SqliteCount = @(Get-ChildItem -Path $Spider2LocalDbDir -Filter *.sqlite -File -ErrorAction SilentlyContinue).Count
if ($SqliteCount -le 0) {
  throw "No .sqlite files were found in $Spider2LocalDbDir after extraction."
}

if (-not $SkipValidation) {
  Write-Step "Validating Spider2 layout"
  & $VenvPython scripts/02_validate_spider2_layout.py --spider2-root $Spider2RootResolved --show-local
}

Write-Step "Repairing workbook template"
& $VenvPython scripts/09_repair_workbook.py --workbook $Workbook --spider2-root $Spider2RootResolved --populate-tasks

Write-Step "Seeding workbook reference data for the free-model study"
& $VenvPython scripts/10_seed_workbook_reference_data.py --workbook $Workbook --spider2-root $Spider2RootResolved

Write-Step "Bootstrap complete"
Write-Host "Spider2 root: $Spider2RootResolved"
Write-Host "SQLite files: $SqliteCount"
Write-Host "Next: run scripts/03_run_trajectory_manual.py with --spider2-root .\\Spider2"
