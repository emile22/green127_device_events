param([switch]$Recreate)
$ErrorActionPreference = "Stop"

$installRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $installRoot
$venv = Join-Path $PSScriptRoot ".venv"
$python = Join-Path $venv "Scripts/python.exe"
$requirements = Join-Path $PSScriptRoot "requirements-lock.txt"
$sourceRoot = Join-Path $repoRoot "allrun5/src"
$requiredDistro = "Ubuntu-22.04"

Write-Host "Checking Python 3.11..."
$pyVersion = & py -3.11 --version 2>&1
if ($LASTEXITCODE -ne 0 -or $pyVersion -notmatch "Python 3\.11\.") {
    throw "Python 3.11 is required. Install Python 3.11 and verify with 'py -0p'. No Python was installed automatically."
}
Write-Host "[PASS] $pyVersion"

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw "WSL is unavailable. An administrator must install/enable WSL separately; see install/README.md."
}
$distroList = @(& wsl.exe --list --quiet 2>$null | ForEach-Object { ($_ -replace "`0", "").Trim() })
if ($LASTEXITCODE -ne 0 -or -not ($distroList -contains $requiredDistro)) {
    throw "Required WSL distribution '$requiredDistro' is missing. Install it explicitly with 'wsl --install -d $requiredDistro'."
}
Write-Host "[PASS] WSL distribution $requiredDistro is installed."

if ($Recreate -and (Test-Path $venv)) {
    Remove-Item -Recurse -Force $venv
}
if (-not (Test-Path $python)) {
    & py -3.11 -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create $venv" }
}
$actualVersion = & $python --version 2>&1
if ($LASTEXITCODE -ne 0 -or $actualVersion -notmatch "Python 3\.11\.") {
    throw "The install venv is not Python 3.11: $actualVersion. Rerun with -Recreate."
}
Write-Host "[PASS] install-local interpreter: $actualVersion"

& $python -m pip install --disable-pip-version-check --requirement $requirements
if ($LASTEXITCODE -ne 0) { throw "Installing the pinned Python lock failed." }
$env:PYTHONPATH = $sourceRoot
& $python -c "import green, pytest, ncclient, pyang, lxml; print('GREEN, pytest, ncclient, pyang, lxml imports passed')"
if ($LASTEXITCODE -ne 0) { throw "Windows Python import verification failed." }

Write-Host "[PASS] Windows Python environment installed at $venv"
Write-Host "WSL native packages were not changed. Continue with install/wsl/install-wsl.sh inside $requiredDistro."
