# GREEN Environment Reproduction — Windows 11 + Ubuntu/WSL

Act as a senior Windows 11, PowerShell, Python, WSL, Ubuntu, NETCONF, Sysrepo, Netopeer2, libyang, and reproducible-build engineer.

Work in the currently opened local `green` repository.

## Purpose

Create a reproducible installation kit for the complete GREEN development/runtime environment used by the project.

The environment has two deliberately separate parts:

```text
Windows 11
----------
VS Code
Python 3.11 virtual environment
GREEN Python runtime
pytest
pyang / Python tooling
ncclient
controller/client-side tools

        |
        | localhost / NETCONF SSH
        v

Ubuntu under WSL
----------------
libyang
libnetconf2
Sysrepo
Netopeer2
yanglint
sysrepo tools
NETCONF server
installed YANG modules
```

The goal is to allow the same environment to be recreated on another Windows 11 machine with WSL.

Do NOT use Docker or containers.

Do NOT merge the Windows Python environment with the WSL native environment.

Do NOT blindly install "latest" versions.

First inspect the CURRENT WORKING MACHINE and freeze the versions/revisions that are actually being used.

---

# 1. Output directory

Store every file created by this task under:

```text
install/
```

Do not modify application code while performing this task.

Prefer this structure:

```text
install/
  README.md

  windows/
    requirements.txt
    requirements-dev.txt
    requirements-lock.txt
    install-windows.ps1
    verify-windows.ps1
    environment-windows.txt

  wsl/
    apt-packages.txt
    apt-packages-lock.txt
    source-versions.env
    install-wsl.sh
    verify-wsl.sh
    start-netopeer2.sh
    stop-netopeer2.sh
    status-netopeer2.sh
    environment-wsl.txt

  yang/
    install-yang-modules.sh
    yang-modules-manifest.txt

  verify/
    verify-end-to-end.ps1
    expected-capabilities.txt

  docs/
    architecture.md
    reproduction-notes.md
    troubleshooting.md
```

Adapt names only if the repository already has a clear convention.

---

# 2. Inspect before generating installation files

Before writing installation scripts, inspect and report the actual current environment.

## Windows 11 inspection

Capture at least:

```powershell
Get-ComputerInfo
$PSVersionTable
wsl --version
wsl --status
wsl -l -v
py -0p
python --version
python -c "import sys; print(sys.executable)"
pip --version
pip list
pip freeze
git --version
code --version
```

If a project `.venv` exists, inspect that interpreter specifically.

Record:

```text
Windows edition/build
PowerShell version
WSL version
installed WSL distributions
default WSL distribution
Python version
Python executable path
pip version
virtual-environment path
Git version
VS Code version
```

Do not expose personal usernames or machine-specific secrets in committed files.

Normalize user-specific absolute paths where practical.

## Ubuntu/WSL inspection

Run inside the actual WSL distribution used by the GREEN project:

```bash
cat /etc/os-release
uname -a
gcc --version
cmake --version
make --version
pkg-config --version
git --version

yanglint --version || true
sysrepoctl --version || true
sysrepocfg --version || true
netopeer2-server -V || true
netopeer2-cli -V || true
```

Also detect library versions with appropriate commands such as:

```bash
pkg-config --modversion libyang || true
pkg-config --modversion libnetconf2 || true
pkg-config --modversion sysrepo || true
```

Inspect the actual executables:

```bash
which yanglint
which sysrepoctl
which sysrepocfg
which netopeer2-server
```

Capture linked library information where useful:

```bash
ldd "$(command -v netopeer2-server)" || true
```

Record the current installation prefixes, for example `/usr` or `/usr/local`.

---

# 3. Determine how WSL native components were installed

For each of:

```text
libyang
libnetconf2
sysrepo
netopeer2
```

determine whether it came from:

```text
apt package
locally built source
Git clone/tag
Git commit
other package mechanism
```

Do not guess.

If source repositories remain available locally, capture:

```bash
git remote -v
git status --short
git describe --tags --always
git rev-parse HEAD
```

If they are no longer available, infer the installed version from binaries/pkg-config and document that the exact source commit could not be recovered.

Prefer exact Git commit hashes for reproduction.

---

# 4. Compatibility lock

Netopeer2 depends on compatible versions of:

```text
libyang
libnetconf2
sysrepo
```

Create:

```text
install/wsl/source-versions.env
```

containing exact versions and preferably exact commits/tags, for example:

```bash
LIBYANG_VERSION="..."
LIBYANG_COMMIT="..."

LIBNETCONF2_VERSION="..."
LIBNETCONF2_COMMIT="..."

SYSREPO_VERSION="..."
SYSREPO_COMMIT="..."

NETOPEER2_VERSION="..."
NETOPEER2_COMMIT="..."
```

The values MUST come from the current working installation or verified compatibility information.

Do not select unrelated "latest" releases independently.

Document the compatibility set in `install/README.md`.

---

# 5. Windows Python dependency files

Create:

```text
install/windows/requirements.txt
install/windows/requirements-dev.txt
install/windows/requirements-lock.txt
```

Use these semantics:

## requirements.txt

Only direct runtime dependencies needed by GREEN on Windows.

Examples may include, only if actually used:

```text
ncclient
lxml
rich
```

Do not add packages merely because they are installed globally.

## requirements-dev.txt

Direct development/test dependencies, for example where actually used:

```text
pytest
pytest-cov
pyang
```

## requirements-lock.txt

Fully pinned transitive environment sufficient to reproduce the working Python environment.

Prefer exact versions:

```text
package==x.y.z
```

Generate it from the project `.venv`, not from an unrelated global Python installation.

Avoid local absolute paths unless required.

If editable/local project installation exists, document it separately rather than embedding a machine-specific path.

---

# 6. Windows install script

Create:

```text
install/windows/install-windows.ps1
```

The script MUST:

1. verify Windows;
2. verify PowerShell;
3. check WSL availability;
4. report whether the required WSL distribution exists;
5. detect Python 3.11;
6. create or recreate the project virtual environment;
7. activate it;
8. upgrade pip only if compatible with the frozen environment;
9. install dependencies from the pinned requirements;
10. install the local GREEN project if required;
11. run basic Python import checks;
12. never silently modify WSL native packages.

Prefer:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r install\windows\requirements-lock.txt
```

Do not rely on an activated shell when an explicit interpreter path is safer.

If Python 3.11 is absent, fail with a clear installation instruction instead of installing an arbitrary Python version silently.

---

# 7. WSL bootstrap policy

The installer must support a machine where WSL is already installed and a machine where it is not.

Do NOT automatically perform privileged Windows feature installation without explicit user action.

In `install/README.md`, document the Windows administrator bootstrap separately, for example:

```powershell
wsl --install
```

or:

```powershell
wsl --install -d <required-distribution>
```

Use the actual distribution/version detected from the working machine.

If the current project uses a specific Ubuntu release, record it explicitly.

Do not silently switch to a different Ubuntu release.

---

# 8. WSL apt dependency manifests

Create:

```text
install/wsl/apt-packages.txt
install/wsl/apt-packages-lock.txt
```

## apt-packages.txt

Contain the minimal explicit Ubuntu build/runtime dependencies required to reproduce the current stack.

Determine these from:

- the current working environment;
- actual source build requirements;
- CMake configuration;
- package dependencies.

Typical categories include:

```text
compiler/build tools
cmake
pkg-config
Git
SSH development libraries
TLS/crypto libraries
PCRE libraries
systemd development support if used
test dependencies only if needed
```

Do not blindly dump every installed Ubuntu package.

## apt-packages-lock.txt

Record exact installed package versions for the explicit package set, using output such as:

```bash
dpkg-query -W -f='${Package}=${Version}\n'
```

This is an audit/lock record.

The install script may need to tolerate package-version availability differences across Ubuntu repositories; document that explicitly.

---

# 9. WSL source build script

Create:

```text
install/wsl/install-wsl.sh
```

Requirements:

- Bash with `set -euo pipefail`;
- idempotent where practical;
- no Docker;
- no interactive Git editor prompts;
- use the versions/commits from `source-versions.env`;
- install components in dependency order;
- use a predictable source/build directory;
- support a configurable installation prefix;
- run `ldconfig` when needed;
- verify every component after installation.

Build order MUST follow actual dependency requirements, normally:

```text
libyang
   ↓
libnetconf2
   ↓
sysrepo
   ↓
netopeer2
```

Do not assume this order without checking the current compatible stack.

For each source component:

1. clone the official repository if absent;
2. fetch tags/commit;
3. checkout the frozen commit;
4. create a clean build directory;
5. configure with recorded CMake options;
6. build;
7. install;
8. verify version.

Do not build from an unpinned branch such as `master` or `main`.

---

# 10. Capture CMake/build options

Reproducibility includes build options, not only versions.

Inspect current CMake caches or installation notes where available.

Record relevant options in:

```text
install/wsl/environment-wsl.txt
```

Examples:

```text
CMAKE_BUILD_TYPE
CMAKE_INSTALL_PREFIX
SYSREPO_GROUP
SYSREPO_UMASK
SYSTEMD integration
NACM-related options
test options
plugin options
```

Do not invent options not used by the current setup.

If an option cannot be recovered, state:

```text
NOT RECOVERABLE FROM CURRENT INSTALLATION
```

and select/document the minimal safe default separately.

---

# 11. Sysrepo runtime setup

Reproduce the current local Sysrepo runtime configuration.

Capture:

```text
repository path
plugin directory
module search paths
group/permission configuration
startup/factory state where relevant
```

Do not copy secrets.

Create only the minimum setup necessary for the GREEN simulator.

If a Sysrepo group is required, the install script may create it using `sudo`, but it MUST:

- explain the action;
- be idempotent;
- not broaden permissions unnecessarily.

---

# 12. Netopeer2 runtime setup

Reproduce:

```text
netopeer2-server binary
listening address
NETCONF SSH port
host-key expectations
test user assumptions
Sysrepo module requirements
```

Do not commit passwords or private host keys.

If host keys must be generated, generate them locally during installation.

Use environment variables for test credentials:

```text
NETCONF_HOST
NETCONF_PORT
NETCONF_USERNAME
NETCONF_PASSWORD
```

Do not hard-code production credentials.

---

# 13. GREEN YANG module manifest

Create:

```text
install/yang/yang-modules-manifest.txt
```

For every module required by the current GREEN runtime record:

```text
module filename
module name
revision
source path in repository
SHA256
required/imported-by
```

At minimum inspect:

```text
ietf-power-and-energy
ietf-hardware
all imported dependencies
GREEN controller modules if used
GREEN capability modules if used
experimental modules if the current run needs them
```

Do not silently download different revisions.

---

# 14. YANG installation script

Create:

```text
install/yang/install-yang-modules.sh
```

It MUST:

- use only repository-pinned YANG files;
- install modules in dependency-safe order;
- use `sysrepoctl`;
- detect modules already installed;
- verify revisions;
- refuse to silently replace a different revision;
- print a concise installed-module summary.

Do not modify upstream YANG files.

---

# 15. Windows verification script

Create:

```text
install/windows/verify-windows.ps1
```

Verify at least:

```text
Python expected major/minor version
correct interpreter is .venv
required imports
pytest
pyang
ncclient
WSL distribution reachable
NETCONF host/port reachable when server is running
```

Print PASS/FAIL per check.

Return a non-zero exit code on failure.

---

# 16. WSL verification script

Create:

```text
install/wsl/verify-wsl.sh
```

Verify:

```text
Ubuntu release
libyang version
yanglint
libnetconf2 version
Sysrepo version
sysrepoctl
sysrepocfg
Netopeer2 version
netopeer2-server
required YANG modules installed
NETCONF port listening
```

Print exact detected versus expected versions.

Return non-zero on mismatch unless explicitly configured as warning-only.

---

# 17. End-to-end verification

Create:

```text
install/verify/verify-end-to-end.ps1
```

This script runs from Windows and verifies the complete split environment:

```text
Windows Python
      |
      | ncclient
      v
localhost / WSL address fallback
      |
      v
Netopeer2 under WSL
      |
      v
Sysrepo
      |
      v
GREEN YANG operational data
```

At minimum:

1. verify WSL is running;
2. verify the required distribution;
3. invoke WSL-side verification;
4. determine `NETCONF_HOST`;
5. connect using `ncclient`;
6. issue NETCONF `<get>`;
7. retrieve `ietf-hardware`;
8. retrieve `ietf-power-and-energy`;
9. confirm expected module capabilities;
10. report PASS/FAIL.

Use `localhost` first when WSL localhost forwarding works.

If it fails, determine the WSL address dynamically.

Do not hard-code a WSL IP.

---

# 18. Environment reports

Generate sanitized audit reports:

```text
install/windows/environment-windows.txt
install/wsl/environment-wsl.txt
```

They MUST include enough version information to diagnose drift but MUST NOT include:

```text
passwords
tokens
private SSH keys
corporate secrets
personal home-directory contents
full environment-variable dumps
```

Redact or normalize usernames and user-specific absolute paths where possible.

---

# 19. Idempotence

Installation scripts should be safe to run again.

They should distinguish:

```text
already installed and correct
installed but wrong version
missing
```

For a wrong version:

- report the mismatch;
- do not destructively replace it without explicit script option or clearly documented action.

Support a flag where useful, for example:

```text
--force-rebuild
```

but do not make destructive behavior the default.

---

# 20. Reproduction README

Create:

```text
install/README.md
```

It MUST explain the complete sequence.

## Phase A — Windows prerequisites

Example structure:

```text
1. Install/verify WSL
2. Verify required Ubuntu distribution
3. Install/verify Python 3.11
4. Clone the GREEN repository
5. Run Windows Python setup
```

## Phase B — WSL native infrastructure

```text
1. apt prerequisites
2. libyang
3. libnetconf2
4. Sysrepo
5. Netopeer2
6. GREEN YANG modules
```

## Phase C — Verification

```text
1. WSL verification
2. Windows verification
3. start Netopeer2
4. end-to-end NETCONF verification
5. project tests
```

Include exact commands.

---

# 21. Reproduction commands

The final README should make the common clean-machine workflow approximately:

```powershell
# Windows PowerShell
.\install\windows\install-windows.ps1
```

then:

```powershell
wsl -d <actual-distro> -- bash -lc "cd <repo-path-visible-to-wsl> && ./install/wsl/install-wsl.sh"
```

then:

```powershell
wsl -d <actual-distro> -- bash -lc "cd <repo-path-visible-to-wsl> && ./install/yang/install-yang-modules.sh"
```

then:

```powershell
wsl -d <actual-distro> -- bash -lc "cd <repo-path-visible-to-wsl> && ./install/wsl/start-netopeer2.sh"
```

then:

```powershell
.\install\verify\verify-end-to-end.ps1
```

Do not hard-code a specific user's Windows profile path.

---

# 22. Requirements generation discipline

Do NOT simply run:

```text
pip freeze > requirements.txt
```

and call the task complete.

Instead:

- `requirements.txt` = direct runtime dependencies;
- `requirements-dev.txt` = direct test/development dependencies;
- `requirements-lock.txt` = fully pinned resolved environment.

Likewise, do NOT use:

```text
dpkg --get-selections
```

as the only WSL dependency definition.

Instead:

- `apt-packages.txt` = explicit dependencies;
- `apt-packages-lock.txt` = exact observed versions;
- `source-versions.env` = source stack compatibility lock.

---

# 23. Drift detection

Verification MUST detect drift between expected and installed:

```text
Python
pip dependencies
Ubuntu release
libyang
libnetconf2
Sysrepo
Netopeer2
YANG module revisions
NETCONF capabilities
```

Report drift explicitly.

Do not silently accept a different major version.

---

# 24. Current environment wins

If this prompt contains an example version that differs from the actual current working project:

```text
THE CURRENT WORKING PROJECT ENVIRONMENT WINS.
```

Record the detected version.

Do not "upgrade" the environment while documenting it.

The task is to reproduce the known-working environment first.

Modernization can be a separate task.

---

# 25. Do not alter application runs

This task is installation/reproducibility only.

Do not modify:

```text
minrun4/
allrun5/
ctrlrun1/
ctrlrun2/
gaprun1/
```

except to read them to determine dependencies.

Do not change event behavior or YANG semantics.

All task output stays under:

```text
install/
```

---

# 26. Final verification report

Create:

```text
install/reproduction-report.md
```

Report:

```text
Windows version
PowerShell version
WSL version
WSL distribution/release
Python version
pip version
Python direct dependency count
Python locked dependency count
libyang version/commit
libnetconf2 version/commit
Sysrepo version/commit
Netopeer2 version/commit
YANG module count and revisions
NETCONF host/port
end-to-end verification result
project test result if executed
known non-reproducible details
```

Do not fabricate values.

---

# 27. Acceptance criteria

The task is complete only when:

- all generated files are under `install/`;
- Windows and WSL environments are documented separately;
- Windows Python dependencies have direct and locked manifests;
- WSL apt dependencies have explicit and locked manifests;
- libyang/libnetconf2/Sysrepo/Netopeer2 versions are frozen compatibly;
- source commits/tags are recorded when recoverable;
- WSL build/install scripts are reproducible;
- YANG revisions and SHA256 values are recorded;
- scripts do not contain credentials;
- localhost plus WSL-IP fallback is supported;
- Windows verification works;
- WSL verification works;
- end-to-end ncclient -> Netopeer2 -> Sysrepo verification exists;
- current working versions are preserved rather than automatically upgraded;
- no containers are used;
- application run directories remain unchanged.

Stop after producing and validating the reproducible Windows 11 + WSL installation kit.
