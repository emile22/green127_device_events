# GREEN Windows 11 + WSL Reproduction Kit

This kit recreates the current GREEN development/runtime environment in two separate layers: Windows Python 3.11 for the GREEN client/runtime and ncclient, and native Ubuntu/WSL packages for libyang, libnetconf2, Sysrepo, and Netopeer2. It uses no containers and does not change application code.

## Captured Environment

See [environment-windows.txt](windows/environment-windows.txt), [environment-wsl.txt](wsl/environment-wsl.txt), and [reproduction-report.md](reproduction-report.md). The working host is Windows 11 Enterprise 24H2 (build 26100.9445), PowerShell 5.1.26100.9444, WSL 3.0.1.0, Ubuntu-22.04 on WSL 2, and Python 3.11.9.

The native stack is currently apt-owned under `/usr`: libyang 2.0.112, libnetconf2 2.0.24, Sysrepo 2.0.53, and Netopeer2 2.0.35. See [source-versions.env](wsl/source-versions.env). No upstream source checkouts were found, so source commit hashes are explicitly marked unrecoverable; the install pins the observed Ubuntu package versions instead. The apt candidate versions matched at capture time. If they drift, installation fails unless `--force-package-install` is explicitly supplied.

Six exact allrun5 YANG files are hashed in [yang-modules-manifest.txt](yang/yang-modules-manifest.txt). Their revisions and baseline source paths are in the manifest; these are the validated copies from `allrun5/yang/` and are not downloaded or modified by this kit.

## Windows Prerequisites

WSL feature installation is deliberately separate and may require an elevated PowerShell and restart. The kit does not install Windows features automatically. If WSL is not already available, an administrator can use:

```powershell
wsl --install
wsl --install -d Ubuntu-22.04
```

Python 3.11 must be available to the Python launcher (`py -0p`). The observed bare `python` and `code` CLI shims are restricted by local group policy; commands below use the Python launcher or explicit venv interpreter. VS Code executable version is 1.143.1.

## Installation Sequence

From the repository root in PowerShell:

```powershell
.\install\windows\install-windows.ps1
.\install\windows\verify-windows.ps1
```

This creates an isolated environment at `install/windows/.venv` and installs the pinned Python lock. The GREEN source is exposed via a temporary `PYTHONPATH` pointing at `allrun5/src`; no editable install or private repository URL is needed. Runtime dependencies are standard-library only; pytest, pyang, and ncclient are development/verification dependencies.

In Ubuntu-22.04 under WSL, from the repository root:

```bash
sudo bash install/wsl/install-wsl.sh
sudo bash install/yang/install-yang-modules.sh
sudo bash install/wsl/start-netopeer2.sh
sudo bash install/wsl/verify-wsl.sh
```

`install-wsl.sh` checks exact installed/candidate package versions, installs only missing pinned packages, and builds the copied allrun5 C provider into `install/wsl/plugins/`. CMake is not required by this apt-based installation. `install-yang-modules.sh` checks module SHA256 and revisions, refuses silent replacement, then installs the explicit RFC 8348 hardware hierarchy.

Start Netopeer2 only after both native packages and YANG modules are installed. The smoke-user credentials are written to `install/runtime/netconf/connection.env` with restrictive permissions; they are not printed by scripts. Runtime data and traces remain under `install/runtime/` and `install/logs/`.

## Verification

With Netopeer2 running, return to Windows PowerShell at the repository root:

```powershell
.\install\verify\verify-windows.ps1 -RequireNetconf
.\install\verify\verify-end-to-end.ps1
```

The end-to-end script generates an operational snapshot using the allrun5 source and the install-local venv, tries `localhost` first, falls back to the current WSL address when needed, connects with ncclient, checks NETCONF base and YANG module visibility, performs read-only `<get>` for RFC 8348 hardware and GREEN Energy Objects, and validates parseable XML. It does not send `<edit-config>` or power-control requests.

Project tests can be run with:

```powershell
$connection = Get-Content .\install\runtime\netconf\connection.env
foreach ($line in $connection) {
	$key, $value = $line -split "=", 2
	Set-Item -Path "Env:$key" -Value $value
}
$env:PYTHONPATH = (Resolve-Path .\allrun5\src).Path
$env:GREEN_NETCONF_STATE_FILE = (Resolve-Path .\install\runtime\operational.json).Path
$env:GREEN_NETCONF_TRACE_FILE = Join-Path (Resolve-Path .\install\logs).Path "netconf-trace.log"
$env:PYTHONDONTWRITEBYTECODE = "1"
\.\install\windows\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp .\install\runtime\pytest-tmp --deselect=allrun5/tests/test_trace.py::test_trace_mode_logs_all_group_a_runtime_snapshots -q .\allrun5\tests
```

The trace-mode test is deselected because it writes snapshots under the read-only `allrun5/runtime` directory; the command keeps test state and temporary files under `install/`.

Validate YANG models independently from Windows:

```powershell
.\install\windows\.venv\Scripts\python.exe -m pyang -p .\allrun5\yang .\allrun5\yang\ietf-power-and-energy@2026-07-02.yang .\allrun5\yang\ietf-hardware@2018-03-13.yang
```

`pyang` validates schemas, not arbitrary JSON instances. WSL `verify-wsl.sh` uses `yanglint` for the generated snapshot.

## Service Lifecycle

From WSL:

```bash
sudo bash install/wsl/status-netopeer2.sh
sudo bash install/wsl/stop-netopeer2.sh
sudo bash install/wsl/start-netopeer2.sh
```

Stopping services retains YANG modules, local host keys, and generated install runtime files. `start-netopeer2.sh` requires modules already installed and does not reinstall them on each run. To regenerate the test credential, remove `install/runtime/netconf/connection.env` and restart.

## Directory Guide

- `windows/`: Python dependency locks and Windows setup/verification.
- `wsl/`: apt package locks, native provider build, and server lifecycle/verification.
- `yang/`: exact module manifest, hashes, and RFC 8348 hierarchy config.
- `verify/`: expected protocol/module capabilities and end-to-end client test.
- `docs/`: architecture, reproduction caveats, and troubleshooting.

The current reproduction cannot recover native upstream Git commits because the WSL installation is package-managed and source checkouts are absent. It records exact apt package versions instead. See [reproduction-notes.md](docs/reproduction-notes.md).
