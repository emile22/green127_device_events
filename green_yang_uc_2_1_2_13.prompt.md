# GREEN YANG Implementation Prompt — Focus on Use Cases 2.1 and 2.13

Act as a senior network-management, energy-accounting, and YANG implementation engineer.

Build a runnable reference implementation of a GREEN energy-management controller and managed-device simulator in this repository.

The implementation MUST focus primarily on these two use cases from `draft-ietf-green-use-cases-02`:

- **Use Case 2.1 — Incremental Application of the GREEN Framework**
- **Use Case 2.13 — Double Accounting Open issue**

Treat these two use cases as the primary acceptance criteria of the project.

Do not try to implement every GREEN use case.

First inspect the repository and its instructions. Preserve existing work and conventions. If the repository is empty, choose a minimal, maintainable stack and document the choice.

Before implementation:

1. read the referenced drafts and actual YANG modules;
2. summarize the architecture;
3. identify specification gaps or inconsistencies affecting Use Cases 2.1 or 2.13;
4. produce a short YANG-to-code implementation map.

Then implement the system, tests, example scenarios, and setup documentation. Do not stop at a proposal.

## Normative and design references

- Power and Energy YANG Module, `draft-ietf-green-power-and-energy-yang-04`:
  https://datatracker.ietf.org/doc/html/draft-ietf-green-power-and-energy-yang-04

- GREEN Framework, `draft-ietf-green-framework-02`:
  https://datatracker.ietf.org/doc/html/draft-ietf-green-framework-02

- GREEN Use Cases, `draft-ietf-green-use-cases-02`:
  https://datatracker.ietf.org/doc/html/draft-ietf-green-use-cases-02

- GREEN Controller YANG, `draft-swepcarl-green-controller-yang-00`:
  https://datatracker.ietf.org/doc/html/draft-swepcarl-green-controller-yang-00

- Power State Capability Discovery, `draft-claise-green-capability-discovery-02`:
  https://datatracker.ietf.org/doc/html/draft-claise-green-capability-discovery-02

- Hardware inventory: RFC 8348
- YANG Push: RFC 8641
- NACM: RFC 8341

Treat all Internet-Drafts as evolving work, not finalized standards.

Record exactly which draft/version each implemented behavior follows.

The actual YANG schema is authoritative for schema validation. If prose and YANG conflict, identify and document the conflict instead of silently changing the schema.

# PRIORITY 0 — USE CASE 2.1

Implement a demonstrable incremental migration from legacy energy management to GREEN-aware management.

The implementation MUST demonstrate the four stages described by Use Case 2.1:

## Stage 1 — Baseline / legacy device

Represent a legacy network device that does not yet expose full `ietf-power-and-energy` support.

The controller MUST be able to maintain a baseline for this device based on:

- datasheet information;
- manually supplied reference values;
- legacy monitoring measurements, when available.

Baseline information is controller-side information unless a referenced standard YANG model explicitly defines where it belongs.

Do not invent leaves in `ietf-power-and-energy` to store baseline information.

Store implementation-specific baseline information separately and clearly identify it as controller metadata.

For every baseline value, preserve:

- source/provenance;
- units;
- timestamp or validity period where applicable;
- measurement versus estimate status;
- accuracy information when known.

Missing information means UNKNOWN.

Never interpret missing information as zero.

Provide deterministic baseline sample data.

Example:

```text
legacy-router-1
    baseline power: 500 W
    source: vendor-datasheet
    accuracy: estimated
```

The operator interface MUST make clear that this is a reference value and not a live GREEN measurement.

## Stage 2 — Component-level GREEN migration

Simulate partial migration of the same device.

At least one hardware component, for example a line card or interface module, MUST become GREEN-aware while other components remain legacy/uninstrumented.

Use RFC 8348 to represent the hardware hierarchy.

Expose the GREEN-aware component through the actual `ietf-power-and-energy` operational model.

Correlate the Energy Object with its RFC 8348 hardware component.

The controller MUST simultaneously represent:

- measured GREEN-aware components;
- legacy/unmeasured components;
- device baseline information.

It MUST NOT synthesize measurements for components that have no measurement source.

The operator must be able to see which parts of the device are:

- measured;
- estimated;
- baseline-only;
- unknown.

## Stage 3 — Device + controller

Extend the demonstration so that the device exposes GREEN information for multiple components and the controller builds a coherent device-level view.

The controller MUST compare current measurements against the Stage 1 baseline where the scopes and units are comparable.

Implement explicit energy-saving validation.

For comparable measurements expose at least:

```text
baseline
observed
delta
percentage change
comparison interval/scope
confidence/provenance
```

Do not compare values that cover different accounting boundaries, time periods, or incompatible units.

When the comparison is invalid, return an explicit reason rather than a misleading efficiency value.

Example:

```text
baseline power = 500 W
observed power = 420 W
reduction = 80 W
reduction = 16 %
```

Use deterministic values in the demo so tests can verify the result exactly.

## Stage 4 — Network-level view

Demonstrate at least two managed devices with different migration levels.

For example:

```text
legacy-router-1
    partially GREEN enabled

green-router-2
    fully GREEN enabled
```

The controller MUST build a network-level view without pretending that both devices provide the same measurement quality.

Expose:

- device/component identity;
- GREEN support level;
- baseline information;
- measured power;
- consumed energy;
- delivered energy;
- accuracy;
- freshness;
- source/provenance;
- collection status.

Network totals MUST clearly indicate whether coverage is:

- complete;
- partial;
- estimated;
- unknown.

Do not silently substitute zero for missing telemetry.

## Use Case 2.1 — protection from overuse

Use Case 2.1 requires protection from excessive power cycling.

If power-state control is implemented, enforce at least:

- minimum time between disruptive transitions;
- configurable cooldown;
- transition rate limit;
- dependency checks;
- explicit operator authorization or dry-run mode.

A test MUST demonstrate rejection of an excessively frequent power-state transition.

Power-state control is secondary to the baseline/migration demonstration and MUST NOT delay implementation of the core 2.1 stages.

# PRIORITY 0 — USE CASE 2.13: DOUBLE ACCOUNTING

Implement explicit topology-aware energy accounting.

This is a central feature of the reference implementation.

The controller MUST distinguish:

1. raw telemetry;
2. energy/power topology;
3. accounting decisions;
4. final de-duplicated totals.

Never modify or discard the original measurements.

## Energy relationships

Use the relationships actually defined by `ietf-power-and-energy`:

- `powered-by` / `powering`;
- `metered-by` / `metering`;
- `aggregated-by` / `aggregating`;
- `enabled-by` / `enabling`.

Use Metering Relationships to represent measurement topology.

Use Power Source Relationships to represent physical energy-flow dependencies.

Use Aggregation Relationships when one Energy Object reports information already aggregated from other Energy Objects.

Do not treat these relationship types as interchangeable.

The `relationship` data in `ietf-power-and-energy` is operational/read-only.

Do not invent a writable relationship tree below `energy-control`.

For relationships spanning devices that cannot be reported by a device itself, maintain a controller-side relationship overlay and clearly identify it as implementation-specific controller topology.

## Accounting engine

Implement an explicit accounting engine that builds a graph of Energy Objects and their relationships.

For each accounting calculation:

1. define the accounting boundary;
2. identify candidate measurements;
3. normalize compatible units;
4. examine metering, aggregation, and power-source relationships;
5. determine which measurements represent the same energy flow;
6. prevent those measurements from being counted more than once;
7. preserve an audit trail explaining every included and excluded value.

The accounting result MUST expose at least:

```text
raw total
accounted/de-duplicated total
included measurements
excluded measurements
exclusion reason
relevant relationship
accounting boundary
topology completeness
measurement freshness
measurement accuracy/provenance
```

Do not deduplicate solely because two numbers happen to be equal.

A topology relationship or other explicit accounting evidence is required.

If the relationship topology is incomplete, do not guess.

Return an explicit result such as:

```text
accounting-status: incomplete-topology
```

and show the raw measurements separately.

## Mandatory Use Case 2.13 scenario A — PDU / physical meter

Implement a deterministic example corresponding to the PDU/physical-meter problem.

Example topology:

```text
upstream-meter
      |
   meters
      |
  +---+---+
  |       |
server-A server-B
```

Example cumulative energy for the same interval:

```text
upstream-meter = 300 Wh
server-A       = 120 Wh
server-B       = 180 Wh
```

A naive sum gives:

```text
300 + 120 + 180 = 600 Wh
```

This is intentionally wrong.

When the metering topology establishes that the upstream 300 Wh measurement covers the two downstream consumers, the accounting engine MUST demonstrate that the energy crossing the selected upstream accounting boundary is:

```text
300 Wh
```

not:

```text
600 Wh
```

The CLI/API MUST allow the operator to inspect why the 120 Wh and 180 Wh values were not added again to the upstream measurement.

The downstream measurements remain valid telemetry and MUST remain visible.

## Mandatory Use Case 2.13 scenario B — Power over Ethernet

Implement a deterministic PoE example.

Topology:

```text
PoE switch port
      |
   powering
      |
PoE endpoint
```

For the same interval use values such as:

```text
switch-port self consumption = 1 Wh
switch-port delivered energy = 9 Wh
endpoint consumed energy     = 9 Wh
```

The implementation MUST preserve the distinction between:

- energy consumed by the providing component itself;
- energy delivered to a downstream Energy Object;
- energy consumed by the downstream Energy Object.

A naive accounting method that adds all three values would produce:

```text
1 + 9 + 9 = 19 Wh
```

which double counts the transferred 9 Wh.

For an accounting boundary containing both the PoE port and endpoint, the example MUST demonstrate the correct result:

```text
10 Wh
```

corresponding to:

```text
1 Wh port self-consumption
+
9 Wh endpoint consumption
```

The same transferred 9 Wh MUST NOT be counted once as delivered energy and again as endpoint consumed energy.

The output MUST show the relationship and accounting decision that caused the duplicate flow to be excluded.

## Aggregation relationship test

Also provide at least one smaller test for an Aggregation Relationship.

Example:

```text
chassis aggregate = 400 Wh
line-card-1        = 150 Wh
line-card-2        = 250 Wh
```

When the chassis value explicitly aggregates the two line-card values, the controller MUST NOT report:

```text
800 Wh
```

for that accounting boundary.

Test both:

- aggregation relationship known;
- aggregation relationship missing.

When the relationship is missing, flag accounting uncertainty rather than inventing topology.

# Device implementation

Implement a device adapter or simulator exposing the actual `ietf-power-and-energy` model from draft -04.

Include:

- operational `energy-objects`;
- writable `energy-control`;
- RFC 8348 hardware inventory;
- realistic deterministic Energy Objects;
- instantaneous power;
- cumulative consumed energy;
- cumulative delivered energy;
- measurement locality;
- accuracy identity;
- certifications where appropriate;
- power state;
- Energy Object relationships.

Provide a controllable measurement provider so tests can:

- change readings;
- advance cumulative energy;
- simulate missing sensors;
- simulate stale measurements;
- simulate device errors;
- change migration stage.

Track requested power state `admin` separately from actual operational `oper`.

Simulate state transitions rather than immediately claiming that the requested state has been reached.

Do not invent GREEN RPCs or notifications.

The draft defines data nodes, not custom GREEN RPC operations or GREEN notifications.

Use the protocol operations supplied by the selected NETCONF/RESTCONF/YANG implementation stack.

# Hardware identity and draft inconsistencies

Inspect RFC 8348 and the exact `ietf-power-and-energy` YANG source before coding.

Pay particular attention to the Energy Object to hardware-component reference and UUID handling.

If the prose in draft -04 and the actual leafref path disagree about component `name` versus `uuid`, document the discrepancy explicitly.

The implementation MUST validate against the actual YANG module.

Do not modify the standard/draft YANG merely to hide the discrepancy.

Maintain stable controller-side UUID correlation where necessary.

# Controller

Implement onboarding/discovery of devices.

The controller MUST retrieve and correlate:

- RFC 8348 hardware inventory;
- `ietf-power-and-energy` operational data;
- Energy Object relationships;
- collection status.

The controller data model MUST keep separate:

- raw device telemetry;
- controller metadata;
- baseline/reference data;
- topology/relationships learned from devices;
- controller-added cross-device topology;
- computed accounting results.

Do not mix computed values back into raw device telemetry.

A controller-side network view MAY use structures inspired by `draft-swepcarl-green-controller-yang-00`, but clearly mark experimental or incomplete portions.

# Telemetry collection

Prefer YANG Push where supported.

Provide polling fallback.

Collection mechanism is not the main goal of the project and should remain simple.

For each collected measurement preserve:

- source device;
- Energy Object;
- collection method;
- collection timestamp;
- freshness;
- units;
- accuracy/provenance.

Stale telemetry MUST be visible as stale.

# Power-state capabilities

Power-state capability discovery is useful but secondary to Use Cases 2.1 and 2.13.

If `draft-claise-green-capability-discovery-02` is implemented:

- keep static supported-state capability information separate from live operational state;
- reuse its schema and identities;
- include nominal/max power and transition times when available;
- treat missing capabilities as unknown, not zero and not unsupported.

Do not allow capability-discovery work to delay the mandatory 2.1 and 2.13 demonstrations.

# Operator interface

Provide a simple CLI or API.

At minimum it MUST support commands or endpoints equivalent to:

```text
list devices
show device <id>
show energy-objects <device>
show baseline <device>
show migration-status <device>
show relationships
show accounting <boundary>
explain accounting <boundary>
```

The accounting explanation is important.

For example, the operator should be able to see output conceptually similar to:

```text
Accounting boundary: rack-1

Raw observations:
  pdu-meter     300 Wh
  server-A      120 Wh
  server-B      180 Wh

Naive total:
  600 Wh

Accounted total:
  300 Wh

Excluded from additional summation:
  server-A 120 Wh
    reason: already represented by upstream metering relationship

  server-B 180 Wh
    reason: already represented by upstream metering relationship

Topology status:
  complete
```

This output format is implementation-specific and MUST NOT be presented as standardized YANG.

# Safety and correctness

Do not invent RPCs, notifications, identities, leaves, or containers and present them as defined by an IETF draft.

Keep implementation-specific data clearly separated from standardized/draft YANG data.

Restrict control writes and sensitive telemetry reads.

Use authenticated/encrypted management connections where supported by the selected stack.

Do not commit credentials.

Use environment variables or local configuration for secrets.

Preserve measurement accuracy and source provenance.

Do not silently aggregate incompatible units, scopes, intervals, or accuracy semantics.

Keep consumed energy distinct from delivered energy.

Detect relationship cycles and obvious inconsistent topology.

Where inverse relationships are expected, validate consistency when both sides are known.

Do not silently repair inconsistent relationship data.

Report it.

# YANG validation

Use appropriate YANG tooling, preferably `pyang`, to validate all YANG modules used by the project.

Run at least:

```bash
pyang -p <yang-path> <module.yang>
```

and generate tree output where useful:

```bash
pyang -f tree <module.yang>
```

Validate representative instance data against the relevant schema where practical.

Do not change the supplied IETF YANG modules merely to make application code easier.

# YANG-to-code coverage

Before coding, create a compact coverage table for the YANG portions required by these two use cases:

```text
YANG XPath
purpose
UC 2.1 / UC 2.13 relevance
config true/false
implementation component
backend/source
test
status
```

Use:

```text
IMPLEMENTED
PARTIAL
MISSING
NOT REQUIRED
```

Do not attempt to implement unrelated YANG nodes merely to achieve artificial 100% coverage.

# Required tests

Add unit tests for at least:

1. YANG parsing and model loading;
2. RFC 8348 / Energy Object correlation;
3. stable identity mapping;
4. unit handling;
5. accuracy/provenance handling;
6. missing measurement handling;
7. stale measurement handling;
8. baseline versus measured-value comparison;
9. invalid baseline comparisons;
10. incremental migration stages;
11. PDU double-accounting prevention;
12. PoE double-accounting prevention;
13. consumed versus delivered energy;
14. aggregation relationship double-accounting prevention;
15. incomplete relationship topology;
16. relationship cycles/inconsistency;
17. unsupported or unsafe state requests if control is implemented;
18. cooldown/rate-limit behavior if control is implemented.

# Mandatory end-to-end tests

Implement at least two end-to-end scenarios.

## E2E-1 — Use Case 2.1

The test MUST:

1. start with a legacy device baseline;
2. display the baseline;
3. migrate one component to GREEN-aware monitoring;
4. collect the component measurement;
5. migrate the device further;
6. collect multiple component/device measurements;
7. calculate a valid baseline-versus-observed comparison;
8. add a second device;
9. display a network-level view showing different GREEN migration levels.

The test MUST prove that unknown/unmeasured portions are not silently treated as zero.

## E2E-2 — Use Case 2.13

The test MUST:

1. start the simulated PDU/meter and downstream devices;
2. collect all raw measurements;
3. show the naive sum;
4. discover or load the Metering Relationships;
5. build the topology;
6. calculate the de-duplicated total;
7. show why each duplicate measurement was excluded;
8. repeat the core validation with the PoE topology.

The expected numeric results MUST be asserted by the test.

# README

Include a README containing:

- architecture;
- explicit project scope;
- why Use Cases 2.1 and 2.13 are the primary focus;
- draft-to-implementation mapping;
- YANG-to-code mapping;
- Use Case 2.1 walkthrough;
- Use Case 2.13 PDU walkthrough;
- Use Case 2.13 PoE walkthrough;
- explanation of the accounting algorithm;
- raw versus accounted energy;
- topology and relationship handling;
- security assumptions;
- draft inconsistencies encountered;
- limitations;
- setup commands;
- run commands;
- test commands;
- sample CLI/API output.

Include simple ASCII topology diagrams for the PDU and PoE examples.

# Completion criteria

Do not consider the task complete merely because the YANG module can be loaded.

The reference implementation is complete only when:

- the four incremental stages of Use Case 2.1 can be demonstrated;
- baseline and live data remain distinguishable;
- partial GREEN deployment is represented correctly;
- energy savings can be validated for comparable data;
- the PDU double-accounting example produces 300 Wh rather than 600 Wh;
- the PoE example produces 10 Wh rather than 19 Wh;
- the reasoning behind every de-duplication is inspectable;
- unknown topology is reported rather than guessed;
- the YANG validates;
- focused unit tests pass;
- both end-to-end scenarios pass;
- the exact commands and results are documented.

At the end, report:

1. implemented features;
2. files created/modified;
3. YANG validation command and result;
4. test commands and results;
5. Use Case 2.1 demonstration result;
6. Use Case 2.13 PDU result;
7. Use Case 2.13 PoE result;
8. draft ambiguities or interpretations;
9. anything intentionally not implemented.
