param([switch]$RequireNetconf)
$ErrorActionPreference = "Continue"
$installRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $installRoot
$python = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
$sourceRoot = Join-Path $repoRoot "allrun5/src"
$failures = 0

function Show-Check([string]$Name, [bool]$Passed, [string]$Detail) {
    if ($Passed) { Write-Host "[PASS] $Name`: $Detail" }
    else { Write-Host "[FAIL] $Name`: $Detail"; $script:failures++ }
}

$versionOutput = if (Test-Path $python) { & $python --version 2>&1 } else { "install venv not found" }
Show-Check "Python 3.11" ($versionOutput -match "Python 3\.11\.") $versionOutput
Show-Check "Project venv interpreter" (Test-Path $python) $python

if (Test-Path $python) {
    $previousPythonPath = $env:PYTHONPATH
    $env:PYTHONPATH = $sourceRoot
    $imports = & $python -c "import green, pytest, ncclient, pyang, lxml; print('imports ok')" 2>&1
    $importPassed = $LASTEXITCODE -eq 0
    Show-Check "Python imports" $importPassed (($imports | Out-String).Trim())
    $pyangVersion = & $python -m pyang --version 2>&1
    Show-Check "pyang" ($LASTEXITCODE -eq 0) (($pyangVersion | Out-String).Trim())
    if ($null -eq $previousPythonPath) { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue }
    else { $env:PYTHONPATH = $previousPythonPath }
}
else {
    Show-Check "Python imports" $false "install the pinned environment first"
    Show-Check "pyang" $false "install the pinned environment first"
}

$distroList = @(& wsl.exe --list --quiet 2>$null | ForEach-Object { ($_ -replace "`0", "").Trim() })
Show-Check "WSL distribution" ($LASTEXITCODE -eq 0 -and $distroList -contains "Ubuntu-22.04") "Ubuntu-22.04"

$port = 830
$reachable = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
$hostUsed = "localhost"
if (-not $reachable) {
    $connectionFile = Join-Path $installRoot "runtime/netconf/connection.env"
    if (Test-Path $connectionFile) {
        $fallbackHost = (Get-Content $connectionFile | Where-Object { $_ -match '^NETCONF_HOST=' } | Select-Object -First 1) -replace '^NETCONF_HOST=', ''
        if ($fallbackHost) {
            $reachable = Test-NetConnection -ComputerName $fallbackHost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            $hostUsed = $fallbackHost
        }
    }
}
if ($reachable) { Show-Check "NETCONF TCP port" $true "$hostUsed`:$port" }
elseif ($RequireNetconf) { Show-Check "NETCONF TCP port" $false "start Netopeer2; tried localhost and configured WSL address on port $port" }
else { Write-Host "[SKIP] NETCONF TCP port`: service is not running (use -RequireNetconf to make this a failure)." }

if ($failures -gt 0) { exit 1 }
exit 0
