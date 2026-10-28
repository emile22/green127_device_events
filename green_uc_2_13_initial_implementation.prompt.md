# GREEN Initial Implementation Prompt — UC 2.13 Core Accounting

Act as a senior network-management, energy-accounting, and YANG implementation engineer.

Work in the currently opened local clone of the `green` repository.

The repository analysis has already been completed. Do not repeat the full architecture study unless required to resolve an implementation issue.

The immediate objective is to implement the smallest correct vertical slice for **Use Case 2.13 — Double Accounting** from `draft-ietf-green-use-cases-02`.

This first implementation increment MUST focus on:

1. internal Energy Object representation;
2. hardware identity correlation;
3. energy relationship graph;
4. raw measurement representation;
5. explicit accounting boundary;
6. de-duplication accounting logic;
7. deterministic PDU scenario;
8. tests proving `600 Wh` naive versus `300 Wh` accounted.

Do NOT implement yet:

- NETCONF;
- RESTCONF;
- YANG Push;
- power-state control;
- capability discovery;
- UC 2.1 migration stages;
- full device simulator;
- full controller API;
- persistence/database;
- unrelated GREEN use cases.

Keep the implementation minimal, testable, and easy to extend later.

## References

Use these references as design inputs:

- `draft-ietf-green-power-and-energy-yang-04`
  https://datatracker.ietf.org/doc/html/draft-ietf-green-power-and-energy-yang-04
- `draft-ietf-green-framework-02`
  https://datatracker.ietf.org/doc/html/draft-ietf-green-framework-02
- `draft-ietf-green-use-cases-02`
  https://datatracker.ietf.org/doc/html/draft-ietf-green-use-cases-02
- RFC 8348 hardware inventory

Treat Internet-Drafts as evolving work.

Do not invent standardized YANG nodes, RPCs, notifications, or identities.

## First: inspect the local repository

Before changing files:

1. confirm the repository root;
2. confirm the current Git branch;
3. inspect existing files and conventions;
4. inspect the existing prompt files;
5. identify the smallest set of files to create or modify.

Then show a short implementation plan.

Do not stop after the plan: continue with implementation.

# Implementation scope

## 1. Internal Energy Object representation

Create a minimal internal model representing an Energy Object.

At minimum include:

- `device_id`
- `energy_object_id`
- `hardware_component_name`
- `hardware_component_uuid`
- measurement metadata
- relationships

Keep these identities distinct:

```text
energy-object/id
    !=
hw:component/name
    !=
hw:component/uuid
```

Do not collapse them into a single identifier.

The model should be compatible with later mapping to:

```text
/energy-objects/energy-object
```

and RFC 8348 hardware components.

Do not claim the internal model itself is standardized YANG.

## 2. Raw measurement representation

Create an explicit raw measurement structure.

At minimum support:

- measurement identifier;
- device identifier;
- Energy Object identifier;
- metric type;
- numeric value;
- unit;
- timestamp;
- interval or accounting period when applicable;
- source/provenance;
- freshness status;
- accuracy metadata if available.

For this first increment, support cumulative consumed energy in `Wh`.

Raw observations MUST remain immutable from the accounting engine's point of view.

The accounting engine must never rewrite raw measurements to make totals easier to compute.

## 3. Relationship representation

Represent the relevant GREEN relationships explicitly.

At minimum support:

- `metered-by`
- `metering`
- `aggregated-by`
- `aggregating`
- `powered-by`
- `powering`

For this first scenario, implement the logic required for Metering Relationships.

Keep the model extensible for Aggregation and Power Source Relationships.

Do not treat these relationship types as interchangeable.

Each relationship should identify:

- relationship type;
- source Energy Object;
- peer Energy Object;
- source/provenance of the topology information.

## 4. Relationship graph

Build an explicit graph from Energy Objects and relationships.

The graph MUST:

- support traversal of metering relationships;
- detect obvious cycles;
- detect missing peers;
- keep topology errors separate from measurement errors.

Do not infer relationships from equal numeric values.

Do not infer topology from naming conventions.

Only explicit relationship information may drive de-duplication.

## 5. Accounting boundary

Represent the accounting boundary explicitly.

For this increment implement a simple boundary such as:

```text
rack-1
```

The boundary MUST identify which Energy Objects are included in the accounting scope.

The accounting engine must not simply calculate:

```text
sum(all known measurements)
```

It must calculate a result for a declared boundary.

Keep accounting-boundary metadata controller-side and implementation-specific.

Do not invent a standardized YANG node for it.

## 6. Accounting result

Create an explicit result object containing at least:

```text
boundary
raw observations
naive total
accounted total
included measurements
excluded measurements
exclusion reason
relationship used
topology status
warnings/errors
```

The result must preserve enough information to explain the calculation.

The accounting engine must be deterministic.

# Mandatory PDU scenario

Implement this deterministic scenario.

Topology:

```text
upstream-meter
      |
   meters
      |
  +---+---+
  |       |
server-A server-B
```

Use these cumulative energy measurements for the same accounting interval:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

The naive total is:

```text
300 + 120 + 180 = 600 Wh
```

This result is intentionally wrong for the selected upstream accounting boundary.

When the Metering Relationships establish that `upstream-meter` covers `server-A` and `server-B`, the accounting engine MUST return:

```text
naive_total = 600 Wh
accounted_total = 300 Wh
```

The result MUST explain why:

```text
server-A 120 Wh
```

and:

```text
server-B 180 Wh
```

were not added again.

The reason must refer to explicit metering topology, not to numeric coincidence.

The raw measurements for the servers MUST remain visible.

# Required accounting behavior

For the PDU case:

1. load raw observations;
2. load explicit metering relationships;
3. build the relationship graph;
4. validate that all measurements are compatible:
   - same metric;
   - same unit;
   - same accounting period;
5. compute the naive sum;
6. determine which measurements represent energy already covered by the upstream meter;
7. compute the de-duplicated total;
8. emit a full explanation.

If units or accounting periods are incompatible, do not aggregate them silently.

Return a clear validation error.

# Unknown or incomplete topology

Add a second test case with the SAME measurements:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

but WITHOUT sufficient Metering Relationships.

In that case:

- do not guess that 300 Wh covers the two servers;
- do not silently return 300 Wh;
- preserve the raw values;
- return a topology status such as:

```text
incomplete-topology
```

The API/result may expose the naive `600 Wh`, but it MUST clearly state that no authoritative de-duplicated total can be derived from the available topology.

# Cycle detection

Add at least one unit test showing that an invalid relationship cycle is detected.

For example:

```text
A meters B
B meters A
```

This must not cause recursion or silent accounting.

Return an explicit topology error.

# Unit model

Use `Wh` consistently inside this first implementation.

Do not attempt to resolve the draft's `Watt-hours` versus `milliwatt-hours` inconsistency by modifying the YANG module.

Document the project convention for this first increment.

Later YANG adapters may normalize draft-specific representations into this internal canonical unit.

# Source/component identity

The draft analysis identified a discrepancy between prose and schema for hardware component identity.

For this implementation:

- keep `hardware_component_name`;
- keep `hardware_component_uuid`;
- keep `energy_object_id`;
- do not use one as an alias for another.

Do not change any IETF YANG module.

# Code structure

Prefer a small structure similar to:

```text
src/
  green/
    models.py
    topology.py
    accounting.py

tests/
  test_accounting_pdu.py
  test_topology.py
```

Adapt names to existing repository conventions if necessary.

Do not create unnecessary abstraction layers.

Do not introduce a framework unless the repository already uses one.

If the repository is currently empty, prefer standard-library Python plus `pytest`, unless a strong technical reason requires something else.

Document any dependency added.

# Required tests

At minimum add tests for:

## Test 1 — PDU de-duplication

Input:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

with complete metering topology.

Assert:

```text
naive total = 600 Wh
accounted total = 300 Wh
topology status = complete
```

Assert that the result explains the exclusion of `server-A` and `server-B`.

## Test 2 — incomplete topology

Use the same measurements without sufficient relationship information.

Assert that:

- raw measurements remain visible;
- the system reports incomplete topology;
- no authoritative de-duplicated total is silently invented.

## Test 3 — cycle detection

Create an invalid metering cycle.

Assert that the graph rejects or reports it explicitly.

## Test 4 — incompatible periods

Use measurements from incompatible accounting intervals.

Assert that they are not silently combined.

## Test 5 — incompatible units

Use incompatible units.

Assert that they are rejected or explicitly normalized only if a defined conversion exists.

# CLI/demo output

A minimal CLI or executable demo is optional for this first increment, but if simple to add, provide an output equivalent to:

```text
Accounting boundary: rack-1

Raw observations:
  upstream-meter  300 Wh
  server-A        120 Wh
  server-B        180 Wh

Naive total:
  600 Wh

Accounted total:
  300 Wh

Excluded from additional summation:
  server-A 120 Wh
    reason: already represented by explicit metering topology

  server-B 180 Wh
    reason: already represented by explicit metering topology

Topology status:
  complete
```

Do not present this output format as standardized YANG.

# Documentation

Update or add minimal documentation explaining:

- scope of this increment;
- relationship between UC 2.13 and the implementation;
- raw versus accounted energy;
- explicit accounting boundary;
- why 600 Wh is naive and 300 Wh is correct in the deterministic scenario;
- why de-duplication requires explicit topology;
- current limitations;
- unit convention;
- how to run the tests.

Do not yet write extensive documentation for features not implemented.

# Validation workflow

Before implementation, report:

```text
files to create/modify
models involved
tests to add
```

After implementation:

1. run the focused unit tests;
2. run the whole test suite if one exists;
3. report exact commands;
4. report exact pass/fail results;
5. list files created or modified.

If `pyang` and YANG modules are not yet present in the repository, do not block this first internal accounting increment on YANG validation.

Instead explicitly report:

```text
YANG validation: not run in this increment because YANG modules are not yet vendored in the repository.
```

Do not fabricate a successful YANG validation.

# Completion criteria

This increment is complete only when all of the following are true:

- internal Energy Object identities are distinct;
- raw measurements are preserved;
- explicit Metering Relationships are represented;
- accounting boundaries are explicit;
- the relationship graph works;
- the deterministic PDU scenario produces:
  - `600 Wh` naive;
  - `300 Wh` accounted;
- the result explains the de-duplication;
- incomplete topology is reported rather than guessed;
- cycles are detected;
- focused tests pass;
- exact commands and results are reported.

Do NOT continue automatically to UC 2.1, NETCONF, RESTCONF, YANG Push, power-state control, or capability discovery.

Stop after completing and reporting this increment.
