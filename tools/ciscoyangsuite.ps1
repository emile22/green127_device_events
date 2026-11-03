$ErrorActionPreference = 'Stop'

$distribution = 'Ubuntu-22.04'
$linuxUser = 'emile'
$port = 8480
$url = "http://localhost:$port"
$wsl = Join-Path $env:WINDIR 'System32\wsl.exe'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$linuxScript = Join-Path $repositoryRoot 'validation\yangsuite\scripts\start_yangsuite.sh'

if (-not (Test-Path -LiteralPath $linuxScript)) {
    throw "YANG Suite start script not found: $linuxScript"
}

function Test-YangSuitePort {
    return (Test-NetConnection -ComputerName 'localhost' -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue)
}

if (-not (Test-YangSuitePort)) {
    $wslPath = (& $wsl -d $distribution --user $linuxUser --exec wslpath -a $linuxScript 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($wslPath)) {
        throw "Could not resolve the launcher path in WSL. Check that $distribution is healthy and available."
    }

    $quotedPath = '"' + $wslPath.Replace('"', '\"') + '"'
    $arguments = "-d $distribution --user $linuxUser --exec bash $quotedPath"
    $serverProcess = Start-Process -FilePath $wsl -ArgumentList $arguments -PassThru

    $attemptsRemaining = 120
    while ($attemptsRemaining -gt 0) {
        if (Test-YangSuitePort) {
            break
        }
        if ($serverProcess.HasExited) {
            throw 'The WSL YANG Suite process exited before port 8480 opened. Check the WSL terminal output.'
        }
        Start-Sleep -Milliseconds 500
        $attemptsRemaining -= 1
    }

    if (-not (Test-YangSuitePort)) {
        throw 'YANG Suite did not open port 8480 within 60 seconds. Check the WSL terminal output.'
    }
}

Start-Process $url
Write-Host "Cisco YANG Suite is available at $url"