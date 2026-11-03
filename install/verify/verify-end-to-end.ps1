param([switch]$SkipRuntimeSnapshot)
$ErrorActionPreference = "Stop"
$installRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $installRoot
$python = Join-Path $installRoot "windows/.venv/Scripts/python.exe"
$sourceRoot = Join-Path $repoRoot "allrun5/src"
$connectionFile = Join-Path $installRoot "runtime/netconf/connection.env"
$snapshotFile = Join-Path $installRoot "runtime/operational.json"
$traceFile = Join-Path $installRoot "logs/netconf-trace.log"
$runtimeLog = Join-Path $installRoot "logs/end-to-end-runtime.log"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $snapshotFile), (Split-Path -Parent $traceFile) | Out-Null

if (-not (Test-Path $python)) { throw "Install Windows dependencies first: install/windows/install-windows.ps1" }
if (-not (Test-Path $connectionFile)) { throw "Start Netopeer2 first; missing $connectionFile" }

Write-Host "Checking WSL services and YANG modules..."
$wslScript = (Join-Path $installRoot "wsl/verify-wsl.sh").Replace('\', '/')
$wslPath = (& wsl.exe -d Ubuntu-22.04 -- wslpath -a $wslScript).Trim()
$wslScriptResult = & wsl.exe -d Ubuntu-22.04 -- bash $wslPath
if ($LASTEXITCODE -ne 0) { throw "WSL verification failed; see output above." }

if (-not $SkipRuntimeSnapshot) {
    Write-Host "Generating a fresh allrun5 snapshot under install/runtime..."
    $previousPythonPath = $env:PYTHONPATH
    $previousStatePath = $env:GREEN_NETCONF_STATE_FILE
    $previousTracePath = $env:GREEN_NETCONF_TRACE_FILE
    try {
        $env:PYTHONPATH = $sourceRoot
        $env:GREEN_NETCONF_STATE_FILE = $snapshotFile
        $env:GREEN_NETCONF_TRACE_FILE = $traceFile
        & $python -m green --auto --interval 0 *> $runtimeLog
        if ($LASTEXITCODE -ne 0) { throw "allrun5 snapshot generation failed; see $runtimeLog" }
    }
    finally {
        if ($null -eq $previousPythonPath) { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue }
        else { $env:PYTHONPATH = $previousPythonPath }
        if ($null -eq $previousStatePath) { Remove-Item Env:GREEN_NETCONF_STATE_FILE -ErrorAction SilentlyContinue }
        else { $env:GREEN_NETCONF_STATE_FILE = $previousStatePath }
        if ($null -eq $previousTracePath) { Remove-Item Env:GREEN_NETCONF_TRACE_FILE -ErrorAction SilentlyContinue }
        else { $env:GREEN_NETCONF_TRACE_FILE = $previousTracePath }
    }
}

$wslRepo = (& wsl.exe -d Ubuntu-22.04 -- wslpath -a $repoRoot.Replace('\', '/')).Trim()
$yanglintCommand = "cd '$wslRepo' && yanglint -p allrun5/yang allrun5/yang/iana-hardware@2018-03-13.yang allrun5/yang/ietf-hardware@2018-03-13.yang allrun5/yang/iana-power-and-energy@2026-07-02.yang allrun5/yang/ietf-power-and-energy@2026-07-02.yang install/runtime/operational.json"
& wsl.exe -d Ubuntu-22.04 -- bash -lc $yanglintCommand
if ($LASTEXITCODE -ne 0) { throw "yanglint rejected the generated operational snapshot." }
Write-Host "[PASS] yanglint validated install/runtime/operational.json"

Write-Host "Checking ncclient -> Netopeer2 -> Sysrepo operational data..."
& $python (Join-Path $PSScriptRoot "verify-netconf.py") $connectionFile
if ($LASTEXITCODE -ne 0) { throw "End-to-end NETCONF verification failed." }
Write-Host "End-to-end verification passed."
