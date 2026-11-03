# Reproduction Report

Captured on 2026-10-31 from the current Windows/WSL environment.

## Host

- Windows: Microsoft Windows 11 Enterprise, 24H2, build 26100.9445, x64.
- PowerShell: 5.1.26100.9444.
- WSL: 3.0.1.0; kernel 6.18.40.1-1.
- WSL distribution: Ubuntu-22.04, Ubuntu 22.04.1 LTS, WSL 2 (default).
- Other WSL distribution detected: docker-desktop WSL2; not used by this kit.
- Python: 3.11.9 (Python launcher selects this version); pip 24.0.
- Git: 2.51.0.windows.2.
- VS Code executable: 1.143.1. The `code` CLI is blocked by local group policy.

## Windows Python

- allrun5 baseline venv: Python 3.11.9, pip 24.0, 16 external packages in its pip freeze; `green-allrun5==0.1.0` was editable from a private VCS URL and is intentionally not copied into a requirements file.
- Direct runtime dependencies: none beyond the Python standard library.
- Direct development/test dependencies: pytest 9.2.0, pyang 2.7.1, ncclient 0.7.1.
- Locked third-party packages: 16, plus pinned pip/setuptools tool versions in `windows/requirements-lock.txt`.
- The reproduction venv is install-local at `install/windows/.venv`; GREEN source is provided via a temporary `PYTHONPATH` to avoid touching app directories.

## WSL Native Stack

- Ubuntu: 22.04.1 LTS (Jammy Jellyfish).
- GCC: 11.4.0-1ubuntu1~22.04.3; Make: 4.3; pkg-config: 0.29.2-1ubuntu3.
- libyang: 2.0.112; apt package 2.0.112-6ubuntu2.
- libnetconf2: 2.0.24; apt package 2.0.24-3build1.
- Sysrepo: 2.0.53; apt package 2.0.53-6build1.
- Netopeer2: 2.0.35; apt package 2.0.35-1ubuntu1.
- Installed prefix: `/usr`; Sysrepo repository: `/etc/sysrepo`.
- Installed YANG modules: six exact project modules, listed with revisions in `yang/yang-modules-manifest.txt`.
- NETCONF host: generated dynamically. Current captured WSL fallback: 192.168.102.228 (informational only; not pinned).
- NETCONF port: 830.
- Source commits: not recoverable. All native executables/libraries are apt-owned and no source checkout was found under `/usr/local/src` or `/opt`.
- CMake: absent and unused by the apt-based native installation and provider build.

## Validation

- Windows setup: the install-local venv was populated from the pinned lock; GREEN, pytest, ncclient, pyang, and lxml imports passed.
- Windows verification: Python 3.11, required imports, pyang 2.7.1, Ubuntu-22.04 detection, and localhost TCP/830 passed.
- WSL setup: all 11 apt package versions matched the lock and the snapshot provider built under `install/wsl/plugins/`.
- YANG installation: all six pinned revisions were confirmed and the RFC 8348 hardware hierarchy was applied.
- WSL verification: package versions, six Sysrepo revisions, active services, and TCP/830 passed.
- End-to-end verification: `yanglint` accepted the generated snapshot; ncclient confirmed NETCONF base, both expected module revisions, RFC 8348 hardware data, and GREEN Energy Objects.
- allrun5 project suite: 79 passed with the trace-mode test deselected because it writes snapshots under read-only `allrun5/runtime`; test state and pytest temporary files were directed to `install/`.
- allrun5 runtime: 61 events across 14 Group A use cases; Group B reports 2 deferred.
- WSL services: started and verified on TCP/830; currently left running.
- NETCONF used localhost successfully; a dynamic WSL address fallback is configured. Credentials are stored in install runtime and are not recorded in this report.

## Known Limits

- Apt package candidate versions matched the installed versions at capture time. No apt repository snapshot was available; installation fails if the exact pin is unavailable rather than silently selecting a different version.
- `libnetconf2` has no pkg-config metadata in this environment; its version is verified through dpkg package ownership and linked library data.
- WSL native source commits/build options cannot be reconstructed because the native stack was installed from apt.
- Windows `python`/`code` command shims are policy-blocked; scripts use explicit venv interpreters, `py -3.11`, and executable metadata.
- The allrun5 trace-mode test writes into `allrun5/runtime`, so it is excluded from the documented read-only test command to preserve that run directory.
