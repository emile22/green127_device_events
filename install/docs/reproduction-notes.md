# Reproduction Notes

- Captured environment date: 2026-10-31.
- The current native stack is Ubuntu 22.04 apt-installed, not source-built. `dpkg -S` attributes the server/tools and shared libraries to Ubuntu packages.
- No native source checkouts were found under `/usr/local/src` or `/opt`; exact upstream Git commits are marked `NOT_RECOVERABLE_APT_INSTALL` rather than inferred.
- WSL package versions and current apt candidates matched for every package in `wsl/apt-packages-lock.txt` at inspection time. An apt repository snapshot was not available. The install script fails if the pinned package version is no longer a candidate.
- `libnetconf2` lacks pkg-config metadata in this installation; its exact package/library version is verified through dpkg/ldd.
- CMake is not installed and is not required by the current apt-based server stack or the Sysrepo provider build. The provider compiles with `cc`, `pkg-config`, Sysrepo headers, and libyang headers.
- Windows Python 3.11.9, pip 24.0, pytest 9.2.0, pyang 2.7.1, and ncclient 0.7.1 were observed in `allrun5/.venv`. The install kit creates its own venv under `install/windows/.venv` and uses the allrun5 source through a temporary `PYTHONPATH`; it does not edit app directories or embed the private editable VCS URL.
- The observed allrun5 venv's setuptools is 65.5.0 although the project build metadata asks for `setuptools>=68`. The install kit does not build/install an editable project; the source is used via `PYTHONPATH`, so the mismatch is not needed for this runtime.
- `python.exe` and `code` shell shims are blocked by local policy. `py -3.11`, explicit venv Python paths, and the VS Code executable version metadata are used instead.
- NETCONF host addresses are dynamic and must not be copied from `environment-wsl.txt`; localhost is preferred by the Windows client.
