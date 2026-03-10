param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path ".venv")) {
  & $Python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Environment ready."
Write-Host "Activate with: .\.venv\Scripts\Activate.ps1"
