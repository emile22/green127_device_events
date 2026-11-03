# Cisco YANG Suite — Native Python/WSL Installation and GREEN `allrun51` Validation

Act as a senior Python, Linux/WSL, NETCONF, YANG, Cisco YANG Suite, Sysrepo, Netopeer2, and IETF GREEN integration engineer.

Work in the currently opened `green` repository.

The goal is to install and configure **Cisco YANG Suite natively with Python under Ubuntu/WSL**, without Docker, and use it as an external NETCONF/YANG validation tool for the existing GREEN implementation:

```text
allrun51/
```

The installation must remain separate from the `allrun51` runtime and Python environment.

Do not modify `allrun51` implementation code unless a validation result proves an actual bug and the user explicitly asks for that fix later.

---

# 1. Objectives

Create a reproducible native WSL installation of Cisco YANG Suite that can validate:

```text
Windows browser
      |
      | http://localhost:8480
      v
Ubuntu/WSL
  Cisco YANG Suite
      |
      | NETCONF/SSH
      v
  Netopeer2
      |
      v
  Sysrepo
      |
      v
  allrun51 operational provider
```

Use Cisco YANG Suite for:

- NETCONF connection validation;
- NETCONF `<hello>` inspection;
- YANG module discovery;
- YANG tree inspection;
- `<get>` generation;
- subtree-filtered `<get>`;
- raw XML inspection;
- RFC 8348 hardware validation;
- `ietf-power-and-energy` validation;
- Energy Object validation;
- relationship validation;
- event-to-event operational-state validation.

Do not use Docker.

Do not make YANG Suite an `allrun51` dependency.

---

# 2. Environment assumptions

The development environment is:

```text
Windows 11
VS Code
PowerShell

WSL2
Ubuntu-22.04

Sysrepo + Netopeer2 run natively in WSL
allrun51 provider runs against Sysrepo/Netopeer2

Windows Python/ncclient is used separately for automated GREEN testing
```

Before changing anything, inspect the actual environment and report:

```text
WSL distribution
Linux release
Python versions available
default python3 version
pip version
Netopeer2 version
Sysrepo version
libyang version
NETCONF listening address/port
current allrun51 status
```

Do not assume versions.

Do not upgrade the GREEN stack.

---

# 3. Installation location

Install Cisco YANG Suite outside `allrun51`.

Preferred location:

```text
~/tools/yangsuite/
```

Use:

```text
~/tools/yangsuite/.venv/
~/tools/yangsuite/data/
~/tools/yangsuite/logs/
```

Repository documentation/scripts created by this task must be placed under:

```text
validation/yangsuite/
```

Create this directory if it does not exist.

Do not put Cisco YANG Suite packages inside:

```text
allrun51/.venv
```

or another GREEN implementation virtual environment.

---

# 4. Native Python installation only

Use a Python virtual environment.

Do not use:

```text
Docker
docker-compose
Podman
containers
system-wide pip installs
```

Prefer the Python version recommended/supported by the installed Cisco YANG Suite release.

The existing Ubuntu-22.04 Python 3.10 environment is a likely candidate, but verify compatibility before installation.

If multiple Python versions exist, select an explicitly supported version and document the reason.

---

# 5. Linux prerequisites

Inspect Cisco's current native/PIP requirements and install only necessary Ubuntu packages.

Typical prerequisites may include packages such as:

```text
python3
python3-pip
python3-venv
python3-lxml
git
openssh-client
iputils-ping
sqlite3
snmp
```

Do not blindly install unnecessary packages.

Record every installed apt package in:

```text
validation/yangsuite/apt-packages.txt
```

Also record package versions where practical.

---

# 6. Create the isolated environment

Create:

```bash
mkdir -p ~/tools/yangsuite
cd ~/tools/yangsuite

python3 -m venv .venv
source .venv/bin/activate
```

Then upgrade only packaging tools required for installation:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install the latest **stable** Cisco YANG Suite release compatible with the selected Python version.

Do not use pre-release packages unless the stable release cannot provide the required NETCONF functionality.

Do not use:

```bash
pip install --pre
```

without a documented reason.

---

# 7. Install only required YANG Suite functionality

The initial validation target is NETCONF/YANG.

Install the core YANG Suite components required for:

```text
device profiles
YANG repositories/file management
YANG tree browsing
NETCONF
```

Do not add optional protocol plugins such as:

```text
gNMI
RESTCONF
gRPC telemetry
```

unless required by a dependency.

After installation run:

```bash
pip list
pip check
```

and record:

```text
yangsuite
yangsuite-netconf
yangsuite-devices
yangsuite-filemanager
yangsuite-yangtree
ncclient, if installed
paramiko or other SSH transport packages
Django
```

Do not assume package names or versions if the actual release differs.

---

# 8. Determine whether YANG Suite uses `ncclient`

This is an important validation point.

Inspect the installed Python dependency graph.

Use tools such as:

```bash
pip show yangsuite
pip show yangsuite-netconf
pip show ncclient
pip check
```

Optionally install `pipdeptree` inside the YANG Suite venv and inspect:

```bash
pipdeptree
```

Determine whether the live YANG Suite NETCONF plugin directly or indirectly depends on `ncclient`.

Document the result in:

```text
validation/yangsuite/netconf_stack.md
```

Classify YANG Suite as either:

```text
A. independent NETCONF protocol implementation
```

or:

```text
B. independent GUI/schema/RPC workflow using ncclient underneath
```

Do not claim full NETCONF-stack independence unless verified from the installed environment.

---

# 9. Freeze the working Python environment

After successful installation, create:

```text
validation/yangsuite/requirements.lock.txt
```

using:

```bash
pip freeze
```

Also create:

```text
validation/yangsuite/version-report.txt
```

containing at least:

```text
Linux distribution
Python version
pip version
YANG Suite version
YANG Suite NETCONF plugin version
Django version
ncclient version if installed
paramiko/SSH dependency version
installation date
```

Do not include credentials.

---

# 10. Initial YANG Suite configuration

Start YANG Suite from:

```bash
cd ~/tools/yangsuite
source .venv/bin/activate
```

Use the actual supported command provided by the installed version.

Configure:

```text
data directory:
~/tools/yangsuite/data

web port:
8480

remote/external access:
disabled unless required
```

Prefer localhost-only access.

The expected Windows browser URL is:

```text
http://localhost:8480
```

If WSL localhost forwarding does not work, diagnose it without hard-coding a permanent WSL IP.

Do not expose YANG Suite publicly.

---

# 11. Netopeer2 target

Verify that Netopeer2 is actually running before configuring YANG Suite.

Check:

```bash
ss -ltnp
```

and identify the NETCONF SSH listener.

Expected conventional NETCONF SSH port:

```text
830
```

but use the actual configured port.

Verify the service independently with the existing GREEN test path or:

```text
netopeer2-cli
```

before blaming YANG Suite for connection failures.

---

# 12. YANG Suite device profile

Create a device profile for the existing Netopeer2 instance.

Suggested logical name:

```text
allrun51-netopeer2
```

Use:

```text
host:
127.0.0.1
```

when YANG Suite and Netopeer2 run in the same WSL distribution.

Use the actual NETCONF port and existing Netopeer2 credentials.

Do not store real passwords or private keys in repository files.

Document only placeholders such as:

```text
<NETCONF_USER>
<NETCONF_PASSWORD>
<SSH_KEY_PATH>
```

---

# 13. Validate NETCONF `<hello>`

Connect with YANG Suite and inspect the server `<hello>`.

Record:

```text
NETCONF base capabilities
YANG Library capability if advertised
NETCONF monitoring capability if advertised
other relevant Netopeer2 capabilities
```

Save a sanitized report in:

```text
validation/yangsuite/netconf_hello.md
```

Do not confuse NETCONF protocol capabilities with GREEN power-state capability discovery.

Explicitly document:

```text
NETCONF <hello> capability
  = NETCONF/server protocol functionality

RFC 9196 / power-state capability discovery
  = modeled operational capability data
```

---

# 14. Retrieve YANG schemas from Netopeer2

If supported by the current server configuration, use YANG Suite to retrieve the device schema/module list.

Create a YANG repository in YANG Suite conceptually named:

```text
allrun51-from-device
```

Retrieve/download the advertised modules when supported.

At minimum inspect whether the device advertises the expected revisions of:

```text
ietf-hardware
ietf-power-and-energy
```

and all required dependencies.

Record the observed module/revision list in:

```text
validation/yangsuite/server-yang-modules.md
```

---

# 15. Compare source YANG versus server-advertised YANG

Create a second YANG Suite repository/set based on the actual source modules from:

```text
allrun51/yang/
```

Conceptual name:

```text
allrun51-source
```

Compare:

```text
allrun51/yang/
```

with:

```text
modules actually advertised/downloaded from Netopeer2
```

Check for:

```text
revision mismatches
missing imports
missing includes
unexpected modules
wrong module revisions
Sysrepo installation mismatch
```

Document results in:

```text
validation/yangsuite/yang_source_vs_server.md
```

Do not silently replace source modules.

---

# 16. Create a GREEN YANG set

Create a YANG Suite YANG set conceptually named:

```text
GREEN-allrun51
```

containing the required modules and dependencies.

At minimum include:

```text
ietf-hardware
ietf-power-and-energy
```

Inspect the YANG tree.

Verify important schema details, including:

```text
hardware/component
component/name
component/uuid if present in the deployed revision

energy-objects
energy-object
source-component-id
power-state/oper
power/energy leaves
relationship structures
```

The actual YANG schema is authoritative if prose documentation conflicts.

---

# 17. Validate `source-component-id`

Use the YANG tree and live NETCONF data to verify that:

```text
energy-object/source-component-id
```

resolves to the intended RFC 8348 component identity according to the deployed schema.

For each tested Energy Object record:

```text
device-id
energy-object-id
source-component-id
matching hardware component
hardware UUID
```

Keep these identities distinct:

```text
device_id
hardware_component_name
hardware_component_uuid
energy_object_id
relationship_peer_id
```

Do not collapse UUID and component name.

---

# 18. Validate the six canonical topologies indirectly

`allrun51` defines these human-facing topology identifiers:

```text
T1 CORE       Fixed Network
T2 AIR        WLAN / PoE
T3 POWER      Power Infrastructure
T4 BACKHAUL   Wireless Transport
T5 EDGE       Edge / Compute
T6 CITY       ISAC / Smart City
```

YANG Suite is not expected to display these nicknames unless they are explicitly modeled in standard YANG data.

The validation objective is instead:

> Can an external NETCONF/YANG client observe the RFC 8348 hardware, Energy Objects, mappings, relationships, and dynamic state from which the expected canonical topology can be reconstructed?

Do not add custom YANG leaves merely to make YANG Suite display `T1 CORE`, `T2 AIR`, etc.

---

# 19. Test full NETCONF `<get>`

Using YANG Suite's NETCONF interface, perform and preserve evidence for:

```text
full <get>
```

against the target device.

Inspect:

```text
XML namespaces
hardware inventory
Energy Object inventory
source-component-id
Power leaves
State leaves
relationships
```

Save sanitized representative XML under:

```text
validation/yangsuite/evidence/
```

Use descriptive filenames.

Do not save passwords, SSH keys, session secrets, or sensitive host information.

---

# 20. Test subtree-filtered `<get>`

Create model-driven subtree-filtered requests for at least:

```text
RFC 8348 hardware/components

all Energy Objects

one individual Energy Object

one hardware component

power-state/oper

representative relationship data
```

Record the request and reply pairs.

Prefer requests generated/constructed through YANG Suite rather than copying the existing `ncclient` test filters.

This helps identify assumptions in the current Python tests.

---

# 21. Energy Object observability validation

This is a mandatory GREEN 5.1 validation.

Inspect representative Energy Objects from all six topologies.

For each important object verify:

```text
Energy Object ID
source component
Power leaf present/absent
Power value when present
State leaf present/absent
State value when present
relationships
```

Remember `allrun51` display semantics:

```text
UNKNOWN
  applicable but unavailable/not observed

N/A
  intentionally not applicable

0
  actual modeled/measured zero
```

The raw NETCONF XML MUST preserve valid YANG typing.

Do not expect literal:

```text
UNKNOWN
N/A
```

inside numeric YANG leaves.

If the simulator says `UNKNOWN`, verify that the corresponding typed leaf is omitted rather than incorrectly emitted as zero or as a string.

Create:

```text
validation/yangsuite/energy_object_validation.md
```

---

# 22. Relationship validation

Validate representative instances of all four GREEN relationship families:

```text
METERING / METERED-BY
AGGREGATING / AGGREGATED-BY
POWERING / POWERED-BY
ENABLING / ENABLED-BY
```

Use examples from the canonical topology where available, such as:

```text
T1 CORE:
switch-fabric ENABLING linecard

T2 AIR:
PoE port POWERING AP
PoE port METERING AP
baseband ENABLING radio

T3 POWER:
PDU POWERING router

T6 CITY:
energy aggregator AGGREGATING roadside units
```

Validate:

```text
direction
inverse semantics
peer identity
absence of self-reference
absence of unintended duplicates
```

---

# 23. Event-to-event validation

Use YANG Suite to validate dynamic changes.

Procedure:

1. place `allrun51` at a known event;
2. perform the same NETCONF `<get>`;
3. save reply A;
4. advance exactly one simulator event;
5. perform the identical `<get>`;
6. save reply B;
7. compare.

Verify that stable inventory remains stable:

```text
device IDs
hardware component names
hardware UUIDs
hardware hierarchy
Energy Object IDs
source-component-id mappings
stable structural relationships
```

Verify that only expected dynamic values change:

```text
Power
Energy
power-state/oper
dynamic relationships where applicable
observability where applicable
```

Record at least one event-transition test for:

```text
T1 CORE
T2 AIR
T3 POWER
```

---

# 24. UC 2.13 validation

Perform a dedicated test for:

```text
UC 2.13 — Double Accounting Open issue
```

Validate the distinction between:

```text
actual topology
```

and:

```text
controller-visible / observable topology
```

Capture a state where measurements are available but topology knowledge is incomplete.

Then capture the `TOPOLOGY_DISCOVERED` state.

Verify that the NETCONF-visible information changes in the expected way without incorrectly implying that the physical topology itself was created at discovery time.

Document in:

```text
validation/yangsuite/uc213_validation.md
```

---

# 25. YANG Suite versus current ncclient tests

Compare the YANG Suite queries and responses with existing:

```text
allrun51/tests/netconf/
```

Do not rewrite tests merely because YANG Suite formats XML differently.

Compare semantically:

```text
namespaces
filter scope
returned objects
leaf values
identityrefs
relationship direction
missing-leaf behavior
```

Document meaningful differences in:

```text
validation/yangsuite/yangsuite_vs_ncclient.md
```

---

# 26. Generated Python artifacts

If the installed YANG Suite version can export NETCONF RPCs/scripts as Python:

- export at least one representative `<get>` test;
- store it only under:

```text
validation/yangsuite/generated/
```

- treat it as external validation evidence;
- do not automatically copy it into `allrun51`;
- compare its RPC/filter construction with the existing ncclient test.

Do not modify production code based solely on formatting differences.

---

# 27. Scripts to create

Create repository-side helper scripts under:

```text
validation/yangsuite/scripts/
```

At minimum provide:

```text
install_yangsuite_wsl.sh
start_yangsuite.sh
check_yangsuite.sh
check_netopeer2.sh
freeze_yangsuite_env.sh
```

Requirements:

- Bash;
- `set -euo pipefail`;
- clear errors;
- idempotent where practical;
- no credentials;
- no hard-coded WSL IP;
- no Docker;
- no modifications under `allrun51`;
- do not auto-upgrade already working GREEN dependencies.

`install_yangsuite_wsl.sh` should install/configure only YANG Suite prerequisites and its isolated venv.

`start_yangsuite.sh` should activate the correct venv and launch the installed version using its actual supported command.

`check_yangsuite.sh` should print versions and verify the local web service.

`check_netopeer2.sh` should verify the NETCONF listener without altering server state.

`freeze_yangsuite_env.sh` should refresh the lock/version reports.

---

# 28. Documentation to create

Create:

```text
validation/yangsuite/README.md
validation/yangsuite/apt-packages.txt
validation/yangsuite/requirements.lock.txt
validation/yangsuite/version-report.txt
validation/yangsuite/netconf_stack.md
validation/yangsuite/netconf_hello.md
validation/yangsuite/server-yang-modules.md
validation/yangsuite/yang_source_vs_server.md
validation/yangsuite/energy_object_validation.md
validation/yangsuite/uc213_validation.md
validation/yangsuite/yangsuite_vs_ncclient.md
```

The README must include this architecture:

```text
Windows 11 browser
        |
        | http://localhost:8480
        v
WSL Ubuntu-22.04
  Cisco YANG Suite
        |
        | NETCONF/SSH
        v
  Netopeer2
        |
        v
  Sysrepo
        |
        v
  allrun51
```

Also state clearly:

```text
Cisco YANG Suite is an external validation tool.
It is not part of allrun51 runtime.
It is not required for pytest.
It does not change the GREEN YANG schemas.
```

---

# 29. Security requirements

Never commit:

```text
passwords
private keys
SSH secrets
NETCONF credentials
session tokens
```

Use placeholders in documentation.

Keep YANG Suite bound to localhost unless there is a justified need for wider access.

Do not disable SSH host/security checks globally merely to make a test pass.

Do not alter system-wide SSH security configuration.

---

# 30. Acceptance tests

The work is complete only if all applicable checks pass:

```text
YANG Suite installed in isolated WSL Python venv
YANG Suite starts successfully
Windows browser can reach the local UI
Netopeer2 listener is reachable
YANG Suite NETCONF connection succeeds
server <hello> is visible
YANG schema/module list is obtainable where supported
ietf-hardware is visible
ietf-power-and-energy is visible
source versus server YANG revisions compared
full <get> works
subtree-filtered <get> works
hardware components visible
Energy Objects visible
source-component-id validated
Power missing/value semantics validated
State data validated
all four relationship families inspected
event-to-event update validated
UC 2.13 observability transition validated
installed Python environment frozen
dependency on ncclient classified
allrun51 remains unmodified
no Docker used
no credentials committed
```

If server-side schema download is unsupported by the current Netopeer2 capabilities, report that accurately and continue with the remaining tests.

Do not fabricate support.

---

# 31. Final report

At completion report:

```text
WSL distribution
Python version
YANG Suite version
YANG Suite NETCONF plugin version
whether ncclient is in the YANG Suite NETCONF dependency path

YANG Suite URL
NETCONF target host/port
NETCONF connection result

server advertised module count
ietf-hardware revision
ietf-power-and-energy revision

full <get> result
subtree <get> result
Energy Object validation result
relationship validation result
event-transition result
UC 2.13 result

files created under validation/yangsuite
allrun51 modification status
remaining issues/blockers
```

Do not claim a command or GUI validation was successful unless it was actually performed.

Stop after the native Python/WSL Cisco YANG Suite installation and GREEN `allrun51` external NETCONF validation environment is working and documented.
