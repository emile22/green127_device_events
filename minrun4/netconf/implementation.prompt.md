# Minimal GREEN NETCONF Simulator — UC 2.13 Double Accounting, UC 2.10 Fixed Network Energy Saving, UC 2.1 Incremental GREEN Deployment, UC 2.14 Power Shortage / Resilience

Act as a senior NETCONF, YANG, Sysrepo, Netopeer2, and Python implementation engineer.

Work in the currently opened local `green` repository.

The project already contains:

- the GREEN Python runtime;
- UC 2.13 accounting;
- UC 2.10 event simulation;
- the YANG adapter;
- local YANG modules and validation.

This increment adds the **smallest real NETCONF device simulator** and extends the runtime with two additional GREEN use-case series.

Use the design patterns of:

- `notconf` for a lightweight Sysrepo + Netopeer2 based simulated device;
- `sysrepo-netopeer2-smoketests` for Python NETCONF integration tests.

Do not copy code blindly. Reuse their architecture and testing approach only where useful.

# Goal

Implement:

```text
GREEN simulator
      |
      v
Python/YANG adapter
      |
      v
Sysrepo
      |
      v
Netopeer2
      |
      | NETCONF over SSH
      v
ncclient test client
```

The simulator must expose four GREEN use-case series:

```text
SERIES 1 — UC 2.13 Double Accounting
SERIES 2 — UC 2.10 Fixed Network Energy Saving
SERIES 3 — UC 2.1 Incremental GREEN Deployment
SERIES 4 — UC 2.14 Power Shortage / Resilience
```

This first NETCONF increment is primarily **read-only operational data**.

Do not implement YANG Push, RESTCONF, capability discovery, or full NETCONF power-state control yet.

Do not redesign the existing GREEN accounting engine or simulator.

# 1. Preserve the existing runtime

Keep working:

```powershell
python -m green
python -m green --auto --interval 0
pytest -v
```

Keep:

```text
[ENTER] next event
a       automatically run all remaining events
r       restart the complete demo
q       quit
```

The NETCONF layer is an additional management interface.

The complete runtime order is:

```text
UC 2.13 Double Accounting
    ↓
UC 2.10 Fixed Network Energy Saving
    ↓
UC 2.1 Incremental GREEN Deployment
    ↓
UC 2.14 Power Shortage / Resilience
```

`a` MUST execute all remaining events across use-case boundaries.

`r` MUST reset all scenario state and restart at the first UC 2.13 event.

# 2. Event explanation requirement

Every runtime event MUST include one brief explanatory sentence.

Requirements:

- fewer than 20 words;
- exactly one sentence per event;
- deterministic;
- displayed immediately below the event identifier and name;
- explain purpose or operational effect;
- use plain language;
- do not present simulator behavior as standardized IETF behavior.

Format:

```text
[UC x.xx / EVENT-ID] EVENT_NAME
<brief explanatory sentence under 20 words>

State / measurements / accounting...
```

# 3. Target architecture

```text
                    NETCONF client
                     (ncclient)
                         |
                         | SSH / NETCONF
                         v
                  +---------------+
                  |   Netopeer2   |
                  | NETCONF server|
                  +-------+-------+
                          |
                  +-------v-------+
                  |    Sysrepo    |
                  | YANG datastore|
                  +-------+-------+
                          |
                     callbacks /
                  operational data
                          |
                  +-------v-------+
                  | GREEN adapter |
                  +-------+-------+
                          |
                  +-------v-------+
                  | GREEN runtime |
                  | simulator     |
                  +---------------+
```

Keep the accounting engine independent from Sysrepo and NETCONF.

Preferred flow:

```text
runtime event
      ↓
internal Python models
      ↓
existing YANG adapter
      ↓
Sysrepo-facing integration
      ↓
Sysrepo
      ↓
Netopeer2
      ↓
NETCONF <get>
```

# 4. Local installation strategy

Use local/native installations of:

```text
libyang
sysrepo
Netopeer2
```

Do not use Docker or any container technology.

Do not introduce:

```text
Dockerfile
docker-compose.yml
container startup scripts
container-specific configuration
```

Prefer Linux or WSL if required by the Sysrepo/Netopeer2 toolchain.

Keep the GREEN Python `.venv` separate from native NETCONF infrastructure.

Document installation, module installation, startup, shutdown, and status checks.

# 5. NETCONF scope

Implement primarily:

```xml
<get>
```

and, if straightforward:

```xml
<get-config>
```

Do not invent GREEN RPCs or notifications.

Do not implement `<edit-config>` power-state control yet.

NETCONF observes state; runtime drives scenario progression.

# 6. YANG modules

Install into Sysrepo the exact YANG modules already validated and stored in the repository.

At minimum:

```text
ietf-power-and-energy
ietf-hardware
```

plus dependencies.

Reuse exact revisions under `yang/`.

Do not silently substitute revisions.

Record module name, revision, source, and Sysrepo installation result.

# 7. Hardware data

Expose RFC 8348 hardware information for at least:

```text
upstream-meter
server-A
server-B
router-A
router-B
```

Add when needed:

```text
linecard-1
linecard-2
non-critical-port
```

Preserve:

```text
hardware component name
hardware UUID
```

Keep distinct:

```text
energy_object_id
hardware_component_name
hardware_component_uuid
```

# 8. GREEN Energy Objects

Expose operational `ietf-power-and-energy` data for scenario Energy Objects.

Only expose fields actually represented by the selected YANG modules.

Keep implementation-specific metadata outside the standard/draft YANG tree.

Likely metadata includes:

```text
event name
use-case event ID
accounting boundary
naive total
accounted total
baseline source
battery percentage if unsupported
service criticality if unsupported
```

# 9. SERIES 1 — UC 2.13 Double Accounting

Events:

```text
U13-0 RAW_MEASUREMENTS
U13-1 TOPOLOGY_DISCOVERED
U13-2 NEXT_MEASUREMENT_INTERVAL
U13-3 TOPOLOGY_INCOMPLETE
```

Topology when complete:

```text
upstream-meter
      |
    meters
      |
  +---+---+
  |       |
server-A server-B
```

## U13-0 — RAW_MEASUREMENTS

Sentence:

```text
Measurements exist, but missing topology prevents reliable de-duplication.
```

Measurements:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

Expected:

```text
naive_total     = 600 Wh
accounted_total = unavailable
topology_status = incomplete-topology
```

Do not guess 300 Wh.

## U13-1 — TOPOLOGY_DISCOVERED

Sentence:

```text
Metering relationships now reveal which downstream measurements are already represented upstream.
```

Measurements remain:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

Add:

```text
upstream-meter meters server-A
upstream-meter meters server-B
```

Expected:

```text
naive_total     = 600 Wh
accounted_total = 300 Wh
topology_status = complete
```

Topology, not numeric equality, drives de-duplication.

## U13-2 — NEXT_MEASUREMENT_INTERVAL

Sentence:

```text
New values prove de-duplication depends on topology rather than numerical equality.
```

Measurements:

```text
upstream-meter = 340 Wh
server-A       = 140 Wh
server-B       = 190 Wh
```

Expected:

```text
naive_total     = 670 Wh
accounted_total = 340 Wh
topology_status = complete
```

The 10 Wh difference may represent upstream overhead or losses.

Do not redistribute it silently.

## U13-3 — TOPOLOGY_INCOMPLETE

Sentence:

```text
A missing relationship makes the energy accounting boundary incomplete again.
```

Measurements:

```text
upstream-meter = 310 Wh
server-A       = 125 Wh
server-B       = 175 Wh
```

Keep only:

```text
upstream-meter meters server-A
```

Expected:

```text
naive_total     = 610 Wh
accounted_total = unavailable
topology_status = incomplete-topology
```

# 10. SERIES 2 — UC 2.10 Fixed Network Energy Saving

Events:

```text
U10-0 TRAFFIC_HIGH
U10-1 TRAFFIC_LOW
U10-2 COMPONENT_SLEEP
U10-3 TRAFFIC_BURST
```

## U10-0 — TRAFFIC_HIGH

Sentence:

```text
High traffic keeps both components active and produces the highest normal energy demand.
```

```text
server-A       = 120 Wh
server-B       = 180 Wh
upstream-meter = 300 Wh

naive     = 600 Wh
accounted = 300 Wh

server-A = active
server-B = active
```

Cumulative:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

## U10-1 — TRAFFIC_LOW

Sentence:

```text
Lower traffic reduces component activity and decreases measured energy consumption.
```

```text
server-A       = 60 Wh
server-B       = 90 Wh
upstream-meter = 150 Wh

naive     = 300 Wh
accounted = 150 Wh
```

Cumulative:

```text
upstream-meter = 450 Wh
server-A       = 180 Wh
server-B       = 270 Wh
```

## U10-2 — COMPONENT_SLEEP

Sentence:

```text
Low traffic allows server-B to enter low-power mode and reduce consumption.
```

```text
server-A       = 60 Wh
server-B       = 20 Wh
upstream-meter = 80 Wh

naive     = 160 Wh
accounted = 80 Wh

server-A = active
server-B = low-power
```

Cumulative:

```text
upstream-meter = 530 Wh
server-A       = 240 Wh
server-B       = 290 Wh
```

Do not implement real GREEN power-state control yet.

## U10-3 — TRAFFIC_BURST

Sentence:

```text
A sudden traffic burst wakes server-B and sharply increases energy consumption.
```

```text
server-A       = 150 Wh
server-B       = 210 Wh
upstream-meter = 360 Wh

naive     = 720 Wh
accounted = 360 Wh

server-A = active
server-B = active
```

Cumulative:

```text
upstream-meter = 890 Wh
server-A       = 390 Wh
server-B       = 500 Wh
```

# 11. SERIES 3 — UC 2.1 Incremental GREEN Deployment

Events:

```text
U1-0 LEGACY_BASELINE
U1-1 COMPONENT_GREEN_ENABLED
U1-2 DEVICE_GREEN_ENABLED
U1-3 NETWORK_MIXED_DEPLOYMENT
```

## U1-0 — LEGACY_BASELINE

Sentence:

```text
A legacy router has only reference power data and no GREEN telemetry.
```

```text
router-A
baseline power = 500 W
source = vendor-datasheet
GREEN telemetry = unavailable
```

Baseline is controller/runtime metadata.

Missing telemetry means `unknown`, never zero.

## U1-1 — COMPONENT_GREEN_ENABLED

Sentence:

```text
One component gains GREEN telemetry while the remainder of the router stays legacy.
```

```text
router-A
  linecard-1 = GREEN measured
  linecard-2 = legacy / unmeasured
```

Expose `linecard-1` through real operational YANG data.

Do not synthesize measurements for `linecard-2`.

## U1-2 — DEVICE_GREEN_ENABLED

Sentence:

```text
Device-wide GREEN measurements now allow comparison against the original legacy baseline.
```

```text
baseline power = 500 W
observed power = 420 W
delta          = -80 W
reduction      = 16 %
```

Baseline comparison remains controller/runtime logic unless modeled.

## U1-3 — NETWORK_MIXED_DEPLOYMENT

Sentence:

```text
The network now combines partially migrated and fully GREEN-enabled devices.
```

```text
router-A = partially GREEN enabled
router-B = fully GREEN enabled
```

Classify information as:

```text
measured
estimated
baseline-only
unknown
```

# 12. SERIES 4 — UC 2.14 Power Shortage / Resilience

Events:

```text
U14-0 GRID_NORMAL
U14-1 GRID_FAILURE
U14-2 BATTERY_OPERATION
U14-3 ENERGY_CRITICAL
U14-4 GRID_RESTORED
```

## U14-0 — GRID_NORMAL

Sentence:

```text
Normal grid power lets every component and service operate without energy restrictions.
```

```text
power-source = grid
router-A = active
router-B = active
critical-service = active
non-critical-service = active
```

## U14-1 — GRID_FAILURE

Sentence:

```text
Grid power fails, so the simulated network switches to its backup energy source.
```

```text
power-source = battery
battery-level = 100 %
router-A = active
router-B = active
```

Keep unsupported battery concepts as simulator metadata.

## U14-2 — BATTERY_OPERATION

Sentence:

```text
Falling battery capacity triggers energy-saving actions while normal connectivity remains available.
```

```text
battery-level = 55 %
router-A = active
router-B = low-power
non-critical-port = disabled
critical-service = active
```

Operational GREEN measurements should reflect reduced consumption.

## U14-3 — ENERGY_CRITICAL

Sentence:

```text
Critical battery levels disable non-essential functions while preserving essential network service.
```

```text
battery-level = 15 %
network-mode = constrained
critical-service = active
non-critical-service = disabled
non-critical components = off or low-power
```

Do not silently power down critical components.

## U14-4 — GRID_RESTORED

Sentence:

```text
Grid power returns, restoring normal operation while the backup battery begins recharging.
```

```text
power-source = grid
battery = charging
router-A = active
router-B = active
non-critical-service = active
```

# 13. Simulator metadata versus YANG

Maintain:

```text
standard/draft YANG data
            versus
simulator/controller metadata
```

Never invent standard YANG nodes for unsupported concepts.

Likely metadata:

```text
battery percentage
grid failure event
traffic event name
critical/non-critical service
baseline source
migration stage
network mode
accounting result
```

# 14. Event progression and NETCONF

Runtime controls scenario progression.

NETCONF observes resulting state:

```text
user/runtime event
       ↓
Python state
       ↓
YANG adapter
       ↓
Sysrepo operational state
       ↓
Netopeer2
       ↓
NETCONF <get>
```

Do not require NETCONF to trigger events yet.

# 15. Minimal Sysrepo state bridge

Prefer:

```text
existing Python models
        ↓
existing YANG adapter
        ↓
Sysrepo-facing adapter
```

Do not duplicate accounting logic, event logic, or scenario state machine inside Sysrepo callbacks.

# 16. NETCONF client tests

Use Python `ncclient`.

Create integration tests inspired by `sysrepo-netopeer2-smoketests`.

At minimum test:

1. NETCONF connection.
2. RFC 8348 hardware retrieval.
3. GREEN Energy Object retrieval.
4. UC 2.13 relationship retrieval.
5. UC 2.13 topology changes.
6. UC 2.10 live energy changes.
7. UC 2.10 sleep/wake behavior.
8. UC 2.1 partial deployment.
9. UC 2.1 device migration.
10. UC 2.14 grid failure.
11. UC 2.14 constrained operation.
12. UC 2.14 recovery.

Do not rely on manual inspection.

# 17. Schema consistency

NETCONF-returned data MUST reuse the existing YANG adapter.

Do not create competing mappings for:

```text
sample JSON
runtime
Sysrepo
NETCONF tests
```

# 18. Test structure

Prefer:

```text
tests/
  netconf/
    test_connection.py
    test_hardware.py
    test_energy_objects.py
    test_uc213_accounting.py
    test_uc210_live_state.py
    test_uc21_incremental.py
    test_uc214_power_shortage.py
```

Keep unit tests, YANG tests, and NETCONF integration tests clearly separated.

# 19. NETCONF configuration

Use:

```text
NETCONF_HOST
NETCONF_PORT
NETCONF_USERNAME
NETCONF_PASSWORD
```

through environment variables or ignored local configuration.

Do not commit credentials.

# 20. Local service management

Document:

```text
start Netopeer2
stop Netopeer2
check Netopeer2 process
check NETCONF listening port
list installed Sysrepo modules
verify Sysrepo connectivity
```

Small helper scripts are acceptable:

```text
scripts/
  netconf-start.sh
  netconf-stop.sh
  netconf-status.sh
```

No Docker/container scripts.

# 21. Health checks

Before NETCONF tests verify:

```text
Sysrepo available
Netopeer2 running
NETCONF port listening
required YANG modules installed
```

Infrastructure failures must be distinguishable from GREEN functional failures.

# 22. Existing tests remain mandatory

Run the complete existing test suite.

NETCONF integration must not break:

```text
UC 2.13 Double Accounting
UC 2.10 Fixed Network Energy Saving
UC 2.1 Incremental GREEN Deployment
UC 2.14 Power Shortage / Resilience
YANG adapter
interactive runtime
```

# 23. No control plane yet

Do NOT implement:

```text
<edit-config> energy-control
NETCONF-triggered state changes
YANG Push
NETCONF notifications
RESTCONF
```

This increment proves:

```text
runtime state
     ↓
YANG representation
     ↓
Sysrepo
     ↓
Netopeer2
     ↓
NETCONF observation
```

# 24. Runtime presentation

Display visible separators:

```text
==================================================
SERIES 1 — UC 2.13 Double Accounting
==================================================
```

Then:

```text
==================================================
UC 2.13 Double Accounting completed
Starting UC 2.10 Fixed Network Energy Saving
==================================================
```

Continue similarly for:

```text
UC 2.1 Incremental GREEN Deployment
UC 2.14 Power Shortage / Resilience
```

Every event must follow:

```text
[UC x.xx / EVENT-ID] EVENT_NAME
<brief explanatory sentence under 20 words>

State / measurements / accounting...
```

# 25. README

Document:

- architecture;
- Sysrepo role;
- Netopeer2 role;
- `ncclient` role;
- relationship to `notconf`;
- relationship to `sysrepo-netopeer2-smoketests`;
- local installation;
- module installation;
- startup commands;
- tests;
- UC 2.13 Double Accounting;
- UC 2.10 Fixed Network Energy Saving;
- UC 2.1 Incremental GREEN Deployment;
- UC 2.14 Power Shortage / Resilience;
- event descriptions;
- YANG data versus simulator metadata;
- read-only NETCONF limitation;
- planned next step.

# 26. Before implementation

Report briefly:

```text
existing YANG modules
existing YANG adapter
existing runtime scenarios
local libyang availability
local Sysrepo availability
local Netopeer2 availability
files to modify
new runtime events
new NETCONF tests
```

Then continue with implementation.

Do not stop after the plan.

# 27. After implementation

Run, as applicable:

```powershell
python -m green --auto --interval 0
pytest -v
pytest tests/netconf -v
```

Report:

```text
Python version
libyang version
Sysrepo version
Netopeer2 version
installed YANG modules/revisions
NETCONF host
NETCONF port
```

Report results separately for:

```text
UC 2.13 — Double Accounting
UC 2.10 — Fixed Network Energy Saving
UC 2.1 — Incremental GREEN Deployment
UC 2.14 — Power Shortage / Resilience
```

Do not fabricate successful commands or test results.

# Acceptance criteria

This increment is complete only when:

- the existing Python runtime works;
- the existing YANG adapter works;
- four ordered use-case series are available;
- every event has a deterministic explanatory sentence shorter than 20 words;
- UC 2.13 Double Accounting demonstrates topology-dependent de-duplication;
- UC 2.10 Fixed Network Energy Saving demonstrates traffic-driven energy variation;
- UC 2.1 Incremental GREEN Deployment demonstrates legacy → component → device → mixed GREEN deployment;
- missing UC 2.1 telemetry is never treated as zero;
- UC 2.14 Power Shortage / Resilience demonstrates grid → battery → constrained operation → recovery;
- essential service remains active during the critical-energy event;
- Sysrepo loads required YANG modules;
- Netopeer2 starts locally;
- `ncclient` connects successfully;
- `<get>` retrieves RFC 8348 and GREEN operational data;
- scenario changes become observable through NETCONF where modeled;
- NETCONF smoke tests cover all four scenarios;
- unsupported scenario metadata is never presented as standardized YANG;
- existing tests still pass;
- no container technology is required;
- no NETCONF control behavior is implemented yet.

Stop after read-only NETCONF integration and smoke tests for all four GREEN use-case series work.

The next increment will add controlled NETCONF configuration behavior, especially:

```text
energy-control/.../power-state/admin
```
