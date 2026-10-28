# Minimal GREEN Implementation Prompt — UC 2.13 + Live UC 2.10

Act as a senior Python and network-management implementation engineer with YANG awareness.

Work in the currently opened local `green` repository.

A minimal runnable runtime should already exist from `green_minimal_runtime_implementation.prompt.md`.

This increment MUST **reuse and extend the existing runtime**. Preserve working code, tests, project structure, and CLI behavior unless a small refactor is required to introduce the real accounting and event models.

The runtime MUST now present **two ordered event series**:

```text
SERIES 1 — UC 2.13: Double Accounting
    ↓
SERIES 2 — UC 2.10: Fixed Network Energy Saving
```

The goal is to replace any placeholder accounting/runtime data with the smallest correct implementation covering:

- **UC 2.13 — Double Accounting**
- **UC 2.10 — Fixed Network Energy Saving**, using deterministic live-like traffic events and energy-consumption variation.

Do not implement real YANG modules in this increment. The next step will be `green_minimal_yang_adapter.prompt.md`.

Do not implement NETCONF, RESTCONF, YANG Push, sysrepo, Netopeer2, capability discovery, UC 2.1, persistence, Docker, or a web UI.

Use the existing Python 3.11 project `.venv` selected by VS Code.

Use Python standard library plus `pytest` unless the repository already establishes another lightweight convention.

# 1. Preserve the existing runtime

Keep these commands working:

```powershell
python -m green
python -m green --auto --interval 1
pytest -v
```

Keep the interactive controls:

```text
[ENTER] next event
a       automatically run all remaining events
r       restart the complete demo from UC 2.13 event U13-0
q       quit
```

The complete demo now contains the two event series in this order:

```text
UC 2.13 series
    U13-0
    U13-1
    U13-2
    U13-3

then

UC 2.10 series
    U10-0
    U10-1
    U10-2
    U10-3
```

`a` MUST automatically run all remaining events across both series.

`r` MUST reset all runtime state and restart from `U13-0`.

Do not replace the existing console runtime with a second CLI.

Tests MUST remain non-interactive and MUST NOT rely on real-time delays.

# 2. Core internal models

Implement or complete:

1. an `EnergyObject` model;
2. an immutable raw energy measurement model;
3. explicit energy relationships;
4. a relationship graph;
5. an explicit accounting boundary;
6. an accounting result model;
7. a deterministic event simulator supporting multiple event series.

Keep these identifiers separate:

```text
device_id
energy_object_id
hardware_component_name
hardware_component_uuid
```

Do not use one as an alias for another.

This distinction is required for the later YANG/RFC 8348 adapter.

# 3. Measurement semantics

Use `Wh` as the internal canonical energy unit.

Represent at least:

```text
interval_energy_wh
```

The simulator SHOULD also maintain cumulative counters for the UC 2.10 energy-consumption sequence so that the next YANG-adapter increment can map cleanly to cumulative energy data.

The accounting examples operate on **energy for a defined simulated measurement interval**.

Never silently treat a lower interval value as a decreasing cumulative counter.

# 4. UC 2.13 topology

Use this topology:

```text
upstream-meter
      |
    meters
      |
  +---+---+
  |       |
server-A server-B
```

Represent the relationship explicitly.

At minimum support relationship types needed by the project model:

```text
metering
metered-by
aggregating
aggregated-by
powering
powered-by
```

Only metering logic needs to be operational in this increment.

Keep the model extensible for the later YANG adapter.

Do not treat relationship types as interchangeable.

# 5. Relationship graph

Build an explicit graph from Energy Objects and relationships.

The graph MUST:

- traverse metering relationships;
- detect cycles;
- detect references to unknown peers;
- distinguish topology errors from measurement errors;
- never infer relationships from equal values;
- never infer topology from object names.

Only explicit topology may drive de-duplication.

# 6. Accounting boundary

Represent the accounting boundary explicitly.

For the demo use:

```text
rack-1
```

The boundary identifies the Energy Objects included in the calculation.

Do not implement accounting as:

```text
sum(all measurements)
```

The accounting engine must calculate a result for an explicit boundary and explicit measurement interval.

Accounting-boundary metadata is controller/runtime metadata, not a standard YANG field.

# 7. Accounting result

Return an explicit result containing at least:

```text
series
event sequence
event name
boundary
raw measurements
naive total
accounted total
included measurements
excluded measurements
exclusion reasons
relationship used
topology status
warnings/errors
```

Raw measurements must remain visible and unchanged.

The result must explain every de-duplication decision.

# 8. SERIES 1 — UC 2.13 Double Accounting

The first runtime series MUST demonstrate the double-accounting problem progressively.

Use event IDs:

```text
U13-0 RAW_MEASUREMENTS
U13-1 TOPOLOGY_DISCOVERED
U13-2 NEXT_MEASUREMENT_INTERVAL
U13-3 TOPOLOGY_INCOMPLETE
```

## U13-0 — RAW_MEASUREMENTS

Receive measurements before sufficient metering topology is available.

Measurements:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

The naive total is:

```text
300 + 120 + 180 = 600 Wh
```

At this point the topology is insufficient.

Expected:

```text
naive_total     = 600 Wh
accounted_total = None
topology_status = incomplete-topology
```

The runtime MUST NOT guess that the correct total is 300 Wh.

Display all three raw measurements.

## U13-1 — TOPOLOGY_DISCOVERED

Keep the SAME raw measurements:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

Now make the explicit Metering Relationships available:

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

The result MUST explain that `server-A` and `server-B` remain valid raw observations but are excluded from additional summation because they are already represented inside the upstream metering boundary.

Do NOT deduplicate merely because:

```text
120 + 180 = 300
```

The explicit topology is authoritative.

## U13-2 — NEXT_MEASUREMENT_INTERVAL

Demonstrate that de-duplication still works when values change and the downstream sum is not numerically identical to the upstream measurement.

Use:

```text
upstream-meter = 340 Wh
server-A       = 140 Wh
server-B       = 190 Wh
```

The downstream sum is:

```text
140 + 190 = 330 Wh
```

The naive total is:

```text
340 + 140 + 190 = 670 Wh
```

Because the explicit metering topology remains complete and `upstream-meter` is the measurement selected for the upstream accounting boundary, expected:

```text
naive_total     = 670 Wh
accounted_total = 340 Wh
topology_status = complete
```

This event is important: it proves that de-duplication is based on topology and accounting boundary, not numeric equality.

The 10 Wh difference may represent upstream overhead/losses in this deterministic demo. Do not silently redistribute it to downstream objects.

## U13-3 — TOPOLOGY_INCOMPLETE

Use a new measurement interval:

```text
upstream-meter = 310 Wh
server-A       = 125 Wh
server-B       = 175 Wh
```

Naive total:

```text
310 + 125 + 175 = 610 Wh
```

Now intentionally remove or invalidate one required Metering Relationship.

For example:

```text
upstream-meter meters server-A
```

is known, but the relationship covering `server-B` is missing.

Expected:

```text
naive_total     = 610 Wh
accounted_total = None
topology_status = incomplete-topology
```

Do not partially guess an authoritative de-duplicated total.

Preserve the raw observations and explain which topology information is missing.

# 9. Transition between event series

After `U13-3`, print a visible separator such as:

```text
==================================================
UC 2.13 series completed
Starting UC 2.10 — Fixed Network Energy Saving
==================================================
```

Then begin the UC 2.10 series.

Interactive mode should pause normally before `U10-0` unless automatic mode is active.

# 10. SERIES 2 — UC 2.10 Fixed Network Energy Saving

The second event series demonstrates energy variation caused by traffic and operational state changes.

Use:

```text
U10-0 TRAFFIC_HIGH
U10-1 TRAFFIC_LOW
U10-2 COMPONENT_SLEEP
U10-3 TRAFFIC_BURST
```

For UC 2.10, the metering topology is known and complete throughout the series.

The simulator represents operational changes that affect energy consumption.

It does not need to generate real network packets.

## U10-0 — TRAFFIC_HIGH

Interval energy:

```text
server-A       = 120 Wh
server-B       = 180 Wh
upstream-meter = 300 Wh
```

Expected:

```text
naive     = 600 Wh
accounted = 300 Wh
```

Component states:

```text
server-A = active
server-B = active
```

Cumulative counters after this event:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

## U10-1 — TRAFFIC_LOW

Traffic decreases.

Interval energy:

```text
server-A       = 60 Wh
server-B       = 90 Wh
upstream-meter = 150 Wh
```

Expected:

```text
naive     = 300 Wh
accounted = 150 Wh
```

Component states:

```text
server-A = active
server-B = active
```

Cumulative counters:

```text
upstream-meter = 450 Wh
server-A       = 180 Wh
server-B       = 270 Wh
```

## U10-2 — COMPONENT_SLEEP

Simulate `server-B` entering a low-power state because traffic remains low.

Interval energy:

```text
server-A       = 60 Wh
server-B       = 20 Wh
upstream-meter = 80 Wh
```

Expected:

```text
naive     = 160 Wh
accounted = 80 Wh
```

State:

```text
server-A = active
server-B = low-power
```

Cumulative counters:

```text
upstream-meter = 530 Wh
server-A       = 240 Wh
server-B       = 290 Wh
```

Do not implement real GREEN power-state control.

This is an operational simulation event only.

## U10-3 — TRAFFIC_BURST

Simulate an unexpected traffic increase that causes `server-B` to return to active state.

Interval energy:

```text
server-A       = 150 Wh
server-B       = 210 Wh
upstream-meter = 360 Wh
```

Expected:

```text
naive     = 720 Wh
accounted = 360 Wh
```

State:

```text
server-A = active
server-B = active
```

Cumulative counters:

```text
upstream-meter = 890 Wh
server-A       = 390 Wh
server-B       = 500 Wh
```

# 11. Event-to-accounting separation

Keep this pipeline strict for BOTH event series:

```text
EVENT
    ↓
SIMULATOR
    ↓
RAW INTERVAL MEASUREMENTS
    ↓
TOPOLOGY STATE / RELATIONSHIP GRAPH
    ↓
ACCOUNTING ENGINE
    ↓
ACCOUNTING RESULT
    ↓
CONSOLE DISPLAY
```

Events may change:

```text
measurements
component state
topology availability
```

Events MUST NOT directly set:

```text
naive_total
accounted_total
```

The accounting engine independently computes totals from:

```text
measurements
+
topology
+
accounting boundary
```

# 12. Runtime output

Reuse the existing interactive runtime.

Every event MUST display the series and event identifier.

Example UC 2.13 output:

```text
[UC 2.13 / U13-1] TOPOLOGY_DISCOVERED

Raw interval energy:
  upstream-meter  300 Wh
  server-A        120 Wh
  server-B        180 Wh

Naive total:       600 Wh
Accounted total:   300 Wh
Topology:          complete

Excluded from additional summation:
  server-A 120 Wh
    reason: explicit upstream metering relationship
  server-B 180 Wh
    reason: explicit upstream metering relationship
```

Example UC 2.10 output:

```text
[UC 2.10 / U10-2] COMPONENT_SLEEP

State:
  server-A       active
  server-B       low-power

Interval energy:
  upstream-meter  80 Wh
  server-A         60 Wh
  server-B         20 Wh

Cumulative energy:
  upstream-meter 530 Wh
  server-A       240 Wh
  server-B       290 Wh

Naive total:       160 Wh
Accounted total:    80 Wh
Topology:          complete
```

# 13. Interactive runtime regression

The existing runtime behavior MUST remain functional.

Conceptual session:

```text
GREEN demo starting...

--- SERIES 1: UC 2.13 Double Accounting ---

[ENTER]=next  a=auto  r=restart  q=quit >

[UC 2.13 / U13-0] RAW_MEASUREMENTS
...
Accounted total: unavailable
Topology: incomplete-topology

[ENTER]=next  a=auto  r=restart  q=quit >

[UC 2.13 / U13-1] TOPOLOGY_DISCOVERED
...
Naive total:       600 Wh
Accounted total:   300 Wh

...

UC 2.13 series completed.
Starting UC 2.10.

[ENTER]=next  a=auto  r=restart  q=quit >

[UC 2.10 / U10-0] TRAFFIC_HIGH
...
```

If the user enters:

```text
a
```

at any point, run all remaining events in the current series and then all events of the following series automatically.

If the user enters:

```text
r
```

reset:

```text
current series
event index
topology state
cumulative counters
component state
```

and restart the complete demo at:

```text
UC 2.13 / U13-0
```

# 14. Cycle detection

Separately test an invalid topology:

```text
A meters B
B meters A
```

The graph must report/reject the cycle.

It must not recurse indefinitely and must not silently produce an accounting result.

This does not need to be a normal runtime event unless it is simple to expose as a test-only scenario.

# 15. Measurement compatibility

Before accounting measurements together, verify that they are compatible for the selected interval.

At minimum check:

```text
metric type
unit
time step / interval
```

Do not silently combine incompatible units or different measurement intervals.

# 16. Minimal project structure

Reuse the structure created by the runtime prompt.

Prefer:

```text
src/
  green/
    __main__.py
    models.py
    topology.py
    accounting.py
    simulator.py

tests/
  test_accounting.py
  test_simulator.py
```

Do not create parallel modules such as:

```text
accounting2.py
new_simulator.py
runtime_new.py
```

unless there is an unavoidable reason.

Refactor existing files instead.

# 17. YANG readiness, but no YANG implementation yet

This increment MUST remain compatible with the next YANG adapter step.

Therefore preserve:

```text
energy_object_id
hardware_component_name
hardware_component_uuid
relationship type
peer identity
interval energy
cumulative energy
component state
topology state
```

as explicit concepts.

However:

- do not vendor YANG modules yet;
- do not add `pyang` as a requirement solely for this increment;
- do not invent YANG serialization;
- do not add NETCONF or RESTCONF;
- do not make accounting depend on XPath.

The next prompt will implement the actual YANG adapter.

# 18. Tests

Add or update tests for both event series.

## UC 2.13 event series

Assert:

```text
U13-0:
  naive_total     = 600 Wh
  accounted_total = None
  topology_status = incomplete-topology

U13-1:
  naive_total     = 600 Wh
  accounted_total = 300 Wh
  topology_status = complete

U13-2:
  naive_total     = 670 Wh
  accounted_total = 340 Wh
  topology_status = complete

U13-3:
  naive_total     = 610 Wh
  accounted_total = None
  topology_status = incomplete-topology
```

Verify that U13-1 and U13-2 exclusions are explained through explicit metering topology.

For U13-2, explicitly verify that:

```text
140 + 190 != 340
```

and that accounting still selects 340 Wh based on topology.

## UC 2.10 event series

Assert interval accounted totals:

```text
U10-0 = 300 Wh
U10-1 = 150 Wh
U10-2 = 80 Wh
U10-3 = 360 Wh
```

Verify:

```text
300 > 150 > 80
360 > 80
```

## UC 2.10 cumulative counters

Assert:

```text
upstream-meter:
300, 450, 530, 890

server-A:
120, 180, 240, 390

server-B:
180, 270, 290, 500
```

Verify that restart resets cumulative counters before the next `U10-0`.

## UC 2.10 component state

Assert:

```text
U10-0 server-B = active
U10-1 server-B = active
U10-2 server-B = low-power
U10-3 server-B = active
```

## Series ordering

Assert that the default event order is exactly:

```text
U13-0
U13-1
U13-2
U13-3
U10-0
U10-1
U10-2
U10-3
```

## Auto mode

Verify that `a` / automatic execution processes every remaining event across the series boundary.

## Restart

Verify that restart returns to:

```text
U13-0
```

and resets topology, counters, and component states.

## Cycle detection

Assert the invalid metering cycle is rejected/reported.

## Runtime regression

Keep existing tests for:

```text
ENTER/next logic through callable runtime functions
auto mode
restart
quit
invalid interval
```

Tests MUST NOT call a real interactive `input()` loop or wait with real `sleep()`.

# 19. Before implementation

Before changing files, briefly report:

```text
repository root
current branch
Python interpreter/version
existing runtime files found
files to modify
tests to add/update
```

Then continue with implementation.

Do not stop after the plan.

# 20. After implementation

Run:

```powershell
python -m green --auto --interval 0
pytest -v
```

Report:

- files modified;
- exact commands;
- exact test results;
- UC 2.13 event results U13-0 through U13-3;
- UC 2.10 event results U10-0 through U10-3;
- cumulative values;
- component-state transitions;
- topology-state transitions;
- cycle-detection test result;
- runtime regression result;
- remaining limitations.

# Acceptance criteria

This increment is complete only when:

- the existing runtime is preserved;
- `ENTER / a / r / q` behavior remains functional;
- the runtime executes **UC 2.13 first, then UC 2.10**;
- UC 2.13 has its own explicit four-event series;
- UC 2.10 has its own explicit four-event series;
- events generate facts/state, not accounting results;
- explicit Metering Relationships drive de-duplication;
- U13-0 reports incomplete topology and no authoritative accounted total;
- U13-1 produces `600 Wh` naive and `300 Wh` accounted;
- U13-2 produces `670 Wh` naive and `340 Wh` accounted despite downstream sum being `330 Wh`;
- U13-3 reports incomplete topology and no authoritative accounted total;
- U10-0 produces `600 Wh` naive and `300 Wh` accounted;
- U10-1 produces `300 Wh` naive and `150 Wh` accounted;
- U10-2 produces `160 Wh` naive and `80 Wh` accounted;
- U10-3 produces `720 Wh` naive and `360 Wh` accounted;
- UC 2.10 cumulative counters increase monotonically;
- `server-B` transitions `active -> low-power -> active`;
- topology cycles are detected;
- tests remain non-interactive and delay-free;
- `pytest -v` passes.

Stop after UC 2.13 + UC 2.10 are working as two ordered runtime event series.

Do not continue automatically to YANG integration.

The next implementation increment is `green_minimal_yang_adapter.prompt.md`.
