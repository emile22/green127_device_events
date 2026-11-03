# GREEN 5.1 — Canonical Device/Topology Architecture for All Event-Ready Use Cases — `allrun51`

Act as a senior IETF GREEN, YANG, NETCONF, Sysrepo, Netopeer2, WSL, Python, network-topology, and controller-architecture implementation engineer.

Work in the currently opened local `green` repository.

This increment extends the existing `allrun5/` implementation into a new, isolated implementation under:

```text
allrun51/
```

The primary implementation baseline is:

```text
allrun5/
```

Treat `allrun5/` as a **strictly read-only implementation reference**.

Do not modify, delete, rename, reformat, or generate runtime artifacts inside `allrun5/`.

All files created or modified by this task MUST be under:

```text
allrun51/
```

This includes source code, copied YANG modules, tests, fixtures, scripts, logs, runtime state, generated snapshots, documentation, and temporary files.

Do not create implementation output elsewhere in the repository.

`allrun5/` may be inspected as a strictly read-only implementation reference, but files produced under `allrun51/` MUST NOT contain the name `allrun5` or paths into any other run directory. Describe allrun51 as self-contained; do not add baseline-source path tables to its README or generated documentation.

The primary use-case source remains:

```text
https://github.com/emile22/draft-ietf-green-use-cases/blob/main/draft-ietf-green-use-cases.md
```

Use the terminology and intent of that draft.

The existing `allrun5` behavior is the implementation baseline. Preserve working behaviors unless this prompt explicitly requires an architectural improvement.

---

# 1. Objective

Refactor and extend the GREEN simulator into a topology-driven implementation under:

```text
allrun51/
```

The main architectural goal is:

> Use one stable canonical demo network composed of reusable device archetypes and topology subgraphs, while representing GREEN use cases as deterministic event overlays over that stable network.

The simulator MUST:

- preserve the working Python/YANG/Sysrepo/Netopeer2/NETCONF architecture from `allrun5`;
- keep NETCONF read-only;
- expose RFC 8348 hardware and `ietf-power-and-energy` operational data;
- preserve all 14 Group A GREEN use cases;
- preserve at least 122 deterministic Group A events;
- preserve all four GREEN relationship families;
- keep the compact line-oriented console layout;
- keep `ENTER/a/d/r/q`;
- run Sysrepo and Netopeer2 natively under Ubuntu/WSL;
- keep Windows Python/ncclient separate;
- use no containers;
- prepare a much stronger base for:
  - controller reconstruction;
  - GREEN Controller processing;
  - RFC 9196 capability discovery;
  - `draft-claise-green-capability-discovery-03`;
  - later capability-aware controller work.

Do NOT implement RFC 9196 capability discovery itself in `allrun51`.

Do NOT add `<edit-config>`, YANG Push, RESTCONF, custom GREEN RPCs, or custom notifications.

---

# 2. First inspect `allrun5`

Before writing code:

1. inspect the complete `allrun5/` tree;
2. identify:
   - Python package layout;
   - event fixture structure;
   - hardware inventory model;
   - Energy Object model;
   - relationship model;
   - YANG adapter;
   - Sysrepo operational callbacks;
   - Netopeer2 scripts;
   - NETCONF tests;
   - console renderer;
   - capability-discovery-readiness files;
3. count:
   - Group A UCs;
   - events per UC;
   - total events;
   - device instances;
   - RFC 8348 components;
   - Energy Objects;
4. identify where topology is currently duplicated across UCs;
5. identify where device/component identities vary unnecessarily across scenarios;
6. identify which relationships are:
   - stable structural;
   - physical-dynamic;
   - observability/discovery-related;
7. identify the best existing components to reuse in the canonical network.

Report this inventory briefly.

Then continue implementation.

Do not stop after analysis.

---

# 3. Core architectural model

Separate these five concepts explicitly:

```text
1. DEVICE ARCHETYPE
2. DEVICE INSTANCE
3. DEPLOYMENT TOPOLOGY
4. CAPABILITY PROFILE PLACEHOLDER / READINESS
5. UC SCENARIO OVERLAY
```

Their semantics are:

```text
DEVICE ARCHETYPE
  defines what a class of device contains

DEVICE INSTANCE
  instantiates an archetype with stable identity

DEPLOYMENT TOPOLOGY
  connects stable device/component instances

CAPABILITY PROFILE PLACEHOLDER / READINESS
  identifies where future RFC 9196 capability data will attach
  but does NOT implement discovery yet

UC SCENARIO OVERLAY
  changes dynamic state without redefining the whole network
```

Do not encode all five concepts inside each UC event fixture.

---

# 4. One canonical demo network

Build one canonical logical demo network:

```text
DEMO-NETWORK-1
```

composed of six reusable sub-topologies:

```text
T1 CORE — FIXED NETWORK
T2 AIR — WLAN / PoE
T3 POWER — POWER INFRASTRUCTURE
T4 BACKHAUL — WIRELESS TRANSPORT
T5 EDGE — EDGE / COMPUTE
T6 CITY — ISAC / SMART CITY
```

The controller-facing view should eventually look like one coherent managed environment, not fourteen unrelated UC-specific laboratories.

---

# 4A. Topology identifiers and nicknames

Use the following naming convention consistently in code, documentation, console output, tests, and controller-facing reports:

```text
T1 CORE       Fixed Network
T2 AIR        WLAN / PoE
T3 POWER      Power Infrastructure
T4 BACKHAUL   Wireless Transport
T5 EDGE       Edge / Compute
T6 CITY       ISAC / Smart City
```

Rules:

- `T1` through `T6` are the stable topology identifiers;
- `CORE`, `AIR`, `POWER`, `BACKHAUL`, `EDGE`, and `CITY` are human-friendly nicknames;
- the long descriptive label remains the authoritative descriptive name;
- machine-readable identifiers may use `T1`...`T6`;
- human-facing logs and documentation SHOULD prefer forms such as `T1 CORE`, `T2 AIR`, etc.;
- do not create competing aliases for the same topology.

Examples:

```text
UC 2.10 uses T1 CORE
UC 2.9 uses T2 AIR + T3 POWER
UC 2.16 uses T1 CORE + T4 BACKHAUL
UC 2.15 uses T5 EDGE
UC 2.12 uses T6 CITY
```

---

# 5. T1 — Fixed network topology

Create a stable fixed-network subgraph similar to:

```text
router-1
 |
 +-- chassis
 +-- switch-fabric
 +-- linecard-1
 |    +-- port-1
 |    +-- port-2
 +-- linecard-2
      +-- port-3
      +-- port-4

router-2
 |
 +-- chassis
 +-- switch-fabric
 +-- linecard-1
 +-- linecard-2
```

Adapt exact names to existing `allrun5` objects where possible.

Prefer reuse over inventing new names.

Use stable RFC 8348 hierarchy.

Useful GREEN functional relationships include:

```text
switch-fabric ENABLING -> linecard-1
switch-fabric ENABLING -> linecard-2
```

and corresponding inverse relationships where represented in the datastore.

Primary use cases:

```text
UC 2.1  Incremental Application of the GREEN Framework
UC 2.2  Selective reduction of energy consumption in network parts proportional to traffic levels
UC 2.10 Fixed Network Energy Saving
UC 2.11 Energy Efficiency Network Management
UC 2.16 Network-level Cross Layer Energy Saving
```

---

# 6. T2 — WLAN / PoE topology

Create a stable WLAN/PoE subgraph similar to:

```text
poe-switch-1
 |
 +-- poe-port-1 ---- ap-1
 |                    +-- baseband
 |                    +-- radio-2g
 |                    +-- radio-5g
 |
 +-- poe-port-2 ---- ap-2
 |
 +-- poe-port-3 ---- ap-3
```

Use real RFC 8348 hardware components.

Use semantically correct relationships:

```text
poe-port-1 POWERING -> ap-1
poe-port-1 METERING -> ap-1
ap-1-baseband ENABLING -> ap-1-radio-5g
```

Primary use cases:

```text
UC 2.5  Indirect Energy Monitoring and control
UC 2.9  WLAN Network Energy Saving
UC 2.14 Energy Efficiency Under Power Shortage
```

---

# 7. T3 — Power infrastructure topology

Create a stable power topology similar to:

```text
grid-source
      |
      v
     ups-1
      |
      v
     pdu-1
   /       \
router-1   poe-switch-1

battery-1
   |
   +---- alternate power path ----> ups-1 / pdu-1
```

Represent actual power topology through:

```text
POWERING
POWERED-BY
```

and measurement topology through:

```text
METERING
METERED-BY
```

Primary use cases:

```text
UC 2.5  Indirect Energy Monitoring and control
UC 2.13 Double Accounting Open issue
UC 2.14 Energy Efficiency Under Power Shortage
```

For UC 2.14, support an actual dynamic power-source relationship change when the simulated source changes from grid to backup.

---

# 8. T4 — Wireless transport topology

Create a stable wireless transport subgraph similar to:

```text
transport-node-1
  +-- modem
  +-- radio
  +-- interface

      wireless link

transport-node-2
  +-- modem
  +-- radio
  +-- interface
```

Primary use cases:

```text
UC 2.7  Dynamic adjustment of network element throughput according to traffic levels in wireless transport networks
UC 2.16 Network-level Cross Layer Energy Saving
```

Ensure UC 2.16 can demonstrate dependency between higher-layer network functions and lower-layer transport components.

---

# 9. T5 — Edge / compute topology

Create a stable edge/compute subgraph similar to:

```text
edge-switch-1
 |
 +-- server-1
 |    +-- nic-1
 |    +-- cpu-1
 |    +-- accelerator-1
 |
 +-- server-2
 |
 +-- server-3
 |
 +-- cache-1
```

Primary use cases:

```text
UC 2.6  Consideration of other domains for obtention of end-to-end metrics
UC 2.8  Video streaming use case
UC 2.13 Double Accounting Open issue
UC 2.15 Energy-Efficient Management of Distributed AI Training Workloads
```

This topology must support accounting tests where parent/child measurements could otherwise be double counted.

Do not infer aggregation from hardware containment.

---

# 10. T6 — ISAC / smart-city topology

Create a stable ISAC subgraph similar to:

```text
roadside-unit-1
  +-- sensing
  +-- processing
  +-- radio

roadside-unit-2
  +-- sensing
  +-- processing
  +-- radio

isac-energy-aggregator
```

Use actual Energy Management aggregation relationships where appropriate:

```text
isac-energy-aggregator AGGREGATING -> roadside-unit-1
isac-energy-aggregator AGGREGATING -> roadside-unit-2
```

Primary use cases:

```text
UC 2.6  Consideration of other domains for obtention of end-to-end metrics
UC 2.12 ISAC-enabled Energy-Aware Smart City Traffic Management
```

---

# 11. UC-to-topology mapping

Use at least this mapping:

```text
UC 2.1   primary T1
UC 2.2   primary T1, secondary T2
UC 2.5   primary T2, secondary T3
UC 2.6   primary T1 + T5, secondary T6
UC 2.7   primary T4
UC 2.8   primary T5, secondary T1
UC 2.9   primary T2, secondary T3
UC 2.10  primary T1
UC 2.11  whole canonical network
UC 2.12  primary T6, secondary T4
UC 2.13  primary T5, secondary T3
UC 2.14  primary T3, secondary T1/T2
UC 2.15  primary T5, secondary T1
UC 2.16  primary T1, secondary T4
```

Document this in:

```text
allrun51/docs/uc_topology_matrix.md
```

---

# 12. Stable identity rules

Across all Group A events, these MUST remain stable unless there is an explicit modeled lifecycle event:

```text
device IDs
RFC 8348 hardware component names
RFC 8348 hardware component UUIDs
hardware parent hierarchy
Energy Object IDs
source-component-id mappings
device archetype identity
```

A normal UC event MUST NOT recreate or rename hardware.

A restart MUST reset runtime state but MUST NOT rename components.

Keep distinct:

```text
device_id
hardware_component_name
hardware_component_uuid
energy_object_id
relationship_peer_id
```

Do not use one field as a substitute for another.

---

# 13. Controller-scoped identity

Prepare the data model for multiple NETCONF devices.

Treat a hardware Component identity at controller scope as:

```text
(device-id, hardware-component-name)
```

not merely:

```text
hardware-component-name
```

because multiple devices may legitimately have:

```text
linecard-1
```

Keep UUID as a separate stable property.

Likewise, normalize Energy Object identity at controller scope as:

```text
(device-id, energy-object-id)
```

Document this rule in:

```text
allrun51/docs/controller_identity_model.md
```

Do not require the device-side YANG to change to implement this controller-side normalization rule.

---

# 14. Event overlays, not full topology replacement

Refactor UC event fixtures so that the model is conceptually:

```text
base canonical network
       +
UC initial overlay
       +
event patch
       =
current runtime state
```

An event SHOULD change only what is dynamic, such as:

```text
instantaneous Power
interval Energy
cumulative Energy
power-state/oper
selected relationship state
measurement visibility
source availability
UC metadata
```

Do not duplicate the entire hardware inventory in every event.

Prefer a reusable base inventory and event patch structure.

---

# 15. Preserve at least 122 Group A events

Preserve the doubled event-density requirement from `allrun5`.

Minimum counts:

```text
UC 2.1   8 events
UC 2.2  10 events
UC 2.5   8 events
UC 2.6   8 events
UC 2.7   8 events
UC 2.8   8 events
UC 2.9  10 events
UC 2.10  8 events
UC 2.11  8 events
UC 2.12 10 events
UC 2.13  8 events
UC 2.14 10 events
UC 2.15  8 events
UC 2.16 10 events
```

Minimum total:

```text
122 deterministic events
```

Do not reduce existing event counts.

Do not replace existing anchor events with new names.

Added/refactored events must remain meaningful, deterministic, and grounded in the UC semantics.

---

# 16. Three relationship behavior classes

Classify relationship behavior explicitly into:

```text
A. STABLE STRUCTURAL
B. PHYSICAL DYNAMIC
C. KNOWLEDGE / OBSERVABILITY
```

Examples:

```text
STABLE STRUCTURAL
  switch-fabric ENABLING linecard

PHYSICAL DYNAMIC
  router POWERED-BY grid
  changes to
  router POWERED-BY battery/UPS path

KNOWLEDGE / OBSERVABILITY
  metering relationship exists physically
  but is not yet exposed/known to the controller
```

Do not model a knowledge/discovery event as a physical topology change unless the UC actually describes a physical topology change.

Document the classification in:

```text
allrun51/docs/relationship_behavior_classes.md
```

---

# 17. UC 2.13 topology-discovery semantics

For:

```text
UC 2.13 — Double Accounting Open issue
```

distinguish:

```text
actual topology
```

from:

```text
controller knowledge / observability of topology
```

For example:

```text
U13-x RAW_MEASUREMENTS
  actual metering relation may already exist
  controller knowledge incomplete

U13-y TOPOLOGY_DISCOVERED
  controller can now observe/use the relation
```

Do not automatically create the physical relationship only when discovery occurs.

The accounting engine should use only the topology available to the controller for the current event.

This preserves the intended demonstration of incomplete versus complete topology knowledge.

---

# 18. Hardware hierarchy versus Energy Object topology

Keep strictly separate:

```text
RFC 8348 containment
```

from:

```text
GREEN Energy Object relationships
```

Do not infer:

```text
METERING
AGGREGATING
POWERING
ENABLING
```

from RFC 8348 parent/child hierarchy.

Do not infer RFC 8348 containment from Energy Object names.

---

# 19. All four GREEN relationship families

Preserve full support for:

```text
metering      / metered-by
aggregating   / aggregated-by
powering      / powered-by
enabling      / enabled-by
```

Preserve all semantics and coverage requirements from `allrun5`.

The canonical topologies should make the relationship usage more natural and less UC-specific.

---


# 19A. Energy Object population and observability contract

The current `allrun5` baseline may contain Energy Objects whose compact display is mostly:

```text
Power = -
State = -
Relationships = -
```

`allrun51` MUST make this sparsity intentional and explicit.

For every Energy Object in the canonical network, define an observability class:

```text
FULL
  Power + State available; relationships exposed where semantically applicable

POWER_ONLY
  Power available; State unavailable or not modeled

STATE_ONLY
  State available; Power unavailable or not modeled

TOPOLOGY_ONLY
  object exists primarily to express a GREEN relationship/topology role

UNOBSERVED
  object is known in inventory, but current telemetry is unavailable
```

Create and maintain:

```text
allrun51/docs/energy_object_observability.md
```

For every Energy Object document at least:

```text
device-id
energy-object-id
source-component-id
observability-class
Power availability
State availability
relationship role(s)
UCs that modify its telemetry/state
reason for any intentionally unavailable field
```

## Display semantics

The console/UI MUST NOT use a bare `-` to represent several different meanings.

Use explicit display labels:

```text
UNKNOWN
  the value is applicable but currently unavailable/not observed

N/A
  the value is intentionally not applicable to this Energy Object

0
  only when the actual measured/modeled value is zero
```

Important:

- do NOT write the strings `UNKNOWN` or `N/A` into numeric or identityref YANG leaves;
- preserve valid YANG types;
- when a YANG leaf is unavailable, omit the leaf according to the schema and render the reason explicitly in the simulator/controller display;
- never substitute zero for missing telemetry.

The compact Energy Object view should therefore prefer output such as:

```text
Energy Object         Source component   Power    State    Relationships
eo-router-1           router-1           420000   ON       POWERED-BY->eo-pdu-1
eo-switch-fabric      switch-fabric      120000   ON       ENABLING->eo-linecard-1,eo-linecard-2
eo-linecard-1         linecard-1           90000  ON       ENABLED-BY->eo-switch-fabric
eo-server-1           server-1            UNKNOWN ON       METERED-BY->eo-upstream-meter
eo-grid-source        grid-source          N/A     ON       POWERING->eo-ups-1
```

The exact values must remain deterministic and grounded in the scenario.

Do not populate fields merely to avoid sparsity.

## Population target

For the major Energy Objects in each canonical topology, provide meaningful dynamic values whenever the UC semantics support them.

In particular, the principal objects for:

```text
T1 CORE — Fixed Network
T2 AIR — WLAN / PoE
T3 POWER — Power Infrastructure
T4 BACKHAUL — Wireless Transport
T5 EDGE — Edge / Compute
T6 CITY — ISAC / Smart City
```

should normally expose useful Power and/or State data.

Relationships should also be populated where the canonical topology semantically defines them.

Examples include:

```text
poe-port POWERING -> access-point
poe-port METERING -> access-point
ap-baseband ENABLING -> ap-radio
pdu POWERING -> router
switch-fabric ENABLING -> linecard
energy-aggregator AGGREGATING -> measured Energy Objects
```

Not every Energy Object needs every field.

However, an important Energy Object MUST NOT remain:

```text
Power = unavailable
State = unavailable
Relationships = none
```

unless its `observability-class` and documentation explicitly justify that condition.

## Controller/discovery importance

The simulator must preserve the distinction between:

```text
object exists
telemetry available
telemetry unavailable
field not applicable
relationship known
relationship unknown/not exposed
capability known
capability unknown
```

This distinction is required so later `ctrlrun6/7/8` and `caprun10+` can reason about absence correctly.

Do not let the controller infer capability from missing or present runtime telemetry.

---

# 20. Compact line-oriented console

Preserve the compact default console from `allrun5`.

Normal event output should look conceptually like:

```text
UC2.10 U10-4 COMPONENT_SLEEP_PREPARED
HW     router-1: lc1=active lc2=ready fabric=active
ENERGY eo-lc1=60W/ON eo-lc2=25W/ON
REL    fabric ENABLING -> lc1,lc2
DIFF   lc2: 90->25W
Enter next | a auto | d netconf | r restart | q quit
```

Do NOT use bordered tables, decorative boxes, or full-screen TUI rendering by default.

Detailed `relationships`, `json`, `xml`, and `diff` views may expand on demand.

Formatting must never alter underlying YANG identities or values.

---

# 21. Capability-discovery readiness

`allrun51` MUST be a stronger preparation point for:

```text
draft-claise-green-capability-discovery-03
RFC 9196 ietf-system-capabilities
```

but MUST NOT implement those models.

Capability discovery later must be able to attach to stable RFC 8348 Components from the canonical network.

Prepare at least these future capability-demo classes:

```text
router linecard
WLAN AP radio
WLAN AP baseband
transport radio/module
server NIC
ISAC radio or sensing component
```

Only select components that actually exist in the canonical inventory.

Create:

```text
allrun51/docs/capability_discovery_readiness.md
```

with:

```text
device-id
hardware-component-name
hardware-component-uuid
device archetype
topology
Energy Object ID
source-component-id
relevant GREEN relationships
UCs using the component
future capability-profile class
```

Do NOT put actual RFC 9196 capability values into `allrun51`.

---

# 22. Capability profiles belong to archetypes, not UCs

Document the future modeling rule:

```text
BAD:
  UC2.10 capability profile
  UC2.16 capability profile

GOOD:
  router-linecard capability profile
  AP-radio capability profile
  transport-radio capability profile
  server-NIC capability profile
```

Capabilities should later attach to stable hardware/component classes or instances, not to scenario event names.

Create:

```text
allrun51/docs/future_capability_profile_model.md
```

Do not implement the capability YANG yet.

---

# 23. Controller reconstruction readiness

A future controller MUST NOT read internal topology fixtures.

Therefore `allrun51` must expose enough data through NETCONF for an external controller to reconstruct:

```text
hardware inventory
Energy Object inventory
source-component-id mappings
Energy Object relationships
dynamic state
```

Create a test concept with two views:

```text
EXPECTED
  canonical topology from simulator fixtures

OBSERVED
  topology reconstructed only from NETCONF-visible YANG
```

Implement a deterministic comparison test where practical.

Do not let the controller-side test import simulator internals as the observed source.

Fixtures may be used only as the expected reference.

---

# 24. Discovery/controller separation

Prepare for this future architecture:

```text
allrun51
  stable hardware/topology
  + dynamic UC state
        |
        v
NETCONF
        |
        +--> controller reconstructs live network
        |
        +--> future caprun adds RFC 9196 capability data
```

The future capability provider MUST NOT derive supported Power States from the current UC event.

The intended future separation is:

```text
hardware identity
     |
     +--> capability profile

UC event
     |
     +--> operational state
```

The two join only through the stable hardware Component identity.

---

# 25. Recommended data organization

Prefer a structure similar to:

```text
allrun51/
  data/
    devices/
      router.json
      poe-switch.json
      wlan-ap.json
      power-system.json
      wireless-transport.json
      compute-node.json
      isac-rsu.json

    topologies/
      demo-network.json
      fixed-network.json
      wlan-poe.json
      power-chain.json
      wireless-transport.json
      edge-compute.json
      isac.json

    scenarios/
      uc01.json
      uc02.json
      ...
      uc16.json

  src/
  tests/
  yang/
  scripts/
  docs/
  logs/
  runtime/
```

Use JSON unless the existing `allrun5` implementation strongly favors another format.

Avoid adding unnecessary dependencies.

The exact file layout may adapt to the existing repository structure, but preserve the conceptual separation.

---

# 26. Device and component scale

Do not over-model.

Target approximately:

```text
1 canonical demo network
6 reusable topology subgraphs
7-8 device archetypes
15-20 device instances
30-50 RFC 8348 hardware Components
14 Group A UCs
122+ deterministic events
```

These are design targets, not hard schema constraints.

The purpose is semantic coverage, not scale benchmarking.

---

# 27. YANG modules

Reuse the same validated YANG revisions as `allrun5`.

At minimum:

```text
ietf-hardware
ietf-power-and-energy
```

plus exact dependencies.

Copy required modules into:

```text
allrun51/yang/
```

Do not patch upstream YANG.

Do not silently upgrade revisions.

Use:

```text
pyang
```

for schema validation/tree generation.

Use:

```text
yanglint
```

for instance validation where available.

---

# 28. NETCONF scope

Remain read-only.

Implement/test:

```xml
<get>
```

and preserve other working read-only retrieval behavior from `allrun5`.

Do NOT add:

```text
<edit-config>
YANG Push
RESTCONF
custom GREEN RPC
custom GREEN notification
capability-gated control
```

Events drive runtime state.

NETCONF observes runtime state.

---

# 29. Runtime architecture

Preserve:

```text
UC event overlay
      |
      v
canonical internal model
      |
      v
YANG adapter
      |
      v
Sysrepo operational data
      |
      v
Netopeer2
      |
      v
NETCONF
```

Do not create multiple competing topology/accounting implementations.

Prefer one canonical model and one YANG adapter.

---

# 30. Windows / WSL model

Preserve:

```text
Windows
  VS Code
  Python 3.11
  ncclient
      |
      v
localhost / detected WSL address

Ubuntu/WSL
  libyang
  Sysrepo
  Netopeer2
```

No containers.

No hard-coded WSL IP.

Use the existing working WSL distribution.

---

# 31. Tests

Create/extend tests for:

## Identity stability

- device IDs stable;
- component names stable;
- UUIDs stable;
- UUID != component name;
- Energy Object IDs stable;
- `source-component-id` resolves correctly;
- restart does not rename stable inventory.

## Topology

- all six sub-topologies load;
- canonical network contains expected device instances;
- hardware parent hierarchy is valid;
- relationship peers resolve;
- no duplicate device/component key collisions at controller scope.

## Events

- all 14 Group A UCs execute;
- each UC meets its minimum event count;
- total events >= 122;
- deterministic ordering;
- event patches do not recreate the whole inventory;
- cumulative Energy monotonicity preserved.

## Energy Object observability

- every Energy Object has a declared observability class;
- important Energy Objects do not remain unintentionally empty;
- missing Power/State is never converted to zero;
- bare `-` is not used as the default ambiguous console representation;
- `UNKNOWN` and `N/A` are display semantics only and never violate YANG leaf types;
- principal objects across T1-T6 expose meaningful Power and/or State when grounded by the UC;
- intentionally sparse objects have documented reasons;
- relationship availability is consistent with the canonical topology and current observability.

## Relationships

- all four relationship families preserved;
- stable structural relations remain stable unless explicitly changed;
- physical dynamic relations change only in appropriate events;
- observability/discovery events do not falsely imply physical topology change;
- inverse semantics remain correct.

## Controller readiness

- expected canonical topology can be reconstructed from NETCONF-visible data;
- controller-visible identifiers are sufficient to distinguish same local component names on different devices;
- internal fixtures are not used as live observed truth.

## Discovery readiness

- future capability-demo components exist;
- selected components have stable RFC 8348 identities;
- their Energy Objects map correctly;
- no RFC 9196 capability data is fabricated in `allrun51`.

---

# 32. Documentation outputs

Create at least:

```text
allrun51/README.md
allrun51/docs/canonical_network.md
allrun51/docs/device_archetypes.md
allrun51/docs/uc_topology_matrix.md
allrun51/docs/controller_identity_model.md
allrun51/docs/relationship_behavior_classes.md
allrun51/docs/energy_object_observability.md
allrun51/docs/capability_discovery_readiness.md
allrun51/docs/future_capability_profile_model.md
allrun51/docs/event_catalog.md
allrun51/docs/relationship_coverage.md
```

`canonical_network.md` should describe the six sub-topologies and their device instances.

`device_archetypes.md` should describe reusable device classes separately from individual UC scenarios.

`uc_topology_matrix.md` should map every UC to primary/secondary topologies.

`controller_identity_model.md` should explain `(device-id, component-name)` scoping.

`relationship_behavior_classes.md` should distinguish structural, physical-dynamic, and observability relationships.

`energy_object_observability.md` should classify every Energy Object and explain Power, State, relationship, `UNKNOWN`, and `N/A` semantics.

`capability_discovery_readiness.md` should identify future RFC 9196 attachment points.

`future_capability_profile_model.md` should explain archetype-based capability profiles.

## 32A. Documentation Table Layout

Every Markdown table under `allrun51/docs/` MUST have aligned column boundaries in the source file. Pad data and separator cells to the same per-column widths so the pipe delimiters occur at the same positions on every row.

Keep summary tables compact. Do not put long prose, full device-instance lists, relationship lists, event state/data dumps, or rationale paragraphs into summary-table cells; put those details in per-topology, per-event, per-component, or per-relationship sections below the summary. Keep every Markdown table row at or below 160 characters.

Add an idempotence and maximum-row-width regression test across all generated docs. Every documentation-generation entry point MUST apply the same table formatter after writing its files. This includes `canonical_network.md` and `event_catalog.md`.

---

# 33. README requirements

`allrun51/README.md` MUST contain a visible architecture section near the top.

Include this detailed simulator-internals view:

```text
device archetypes
      ↓
device instances
      ↓
canonical topology
      ↓
UC overlays
      ↓
YANG adapter
      ↓
Sysrepo / Netopeer2
      ↓
NETCONF
```

Also include this detailed six-topology view:

```text
T1 CORE       Fixed Network
T2 AIR        WLAN / PoE
T3 POWER      Power Infrastructure
T4 BACKHAUL   Wireless Transport
T5 EDGE       Edge / Compute
T6 CITY       ISAC / Smart City
```

Use the `Ti + nickname` form consistently in human-facing README text, UC-to-topology mappings, console summaries, and reports.

These two views are normative README documentation for `allrun51`; do not leave them only in the implementation prompt or secondary documentation.

Document:

- purpose of `allrun51`;
- allrun51 is described as a self-contained implementation with no references to other run directories;
- one canonical network concept;
- six reusable sub-topologies;
- device archetype versus device instance;
- event overlay architecture;
- 122+ event requirement;
- compact console;
- Windows/WSL architecture;
- Sysrepo/Netopeer2 roles;
- NETCONF read-only scope;
- relationship semantics;
- Energy Object observability classes and explicit `UNKNOWN` / `N/A` display semantics;
- controller-scoped identity;
- controller reconstruction principle;
- discovery-readiness boundary;
- future `draft-claise-green-capability-discovery-03` integration;
- tests;
- current limitations.

---

# 34. Before implementation

Report briefly:

```text
allrun5 structure found
existing event counts
existing topology duplication
existing stable device/component identities
existing relationship model
existing Energy Object population/sparsity and use of `-`
existing NETCONF path
existing capability-readiness components
proposed canonical device archetypes
proposed six topology subgraphs
proposed files/directories under allrun51
```

Then continue implementation.

Do not ask for confirmation.

Do not stop at the plan.

---

# 35. After implementation

Run the implementation and tests.

Adapt commands to the actual copied package structure, but provide a working equivalent to:

```powershell
cd allrun51
python -m green --auto --interval 0
pytest -v
pytest tests/netconf -v
```

Run WSL-native Sysrepo/Netopeer2 checks.

Report:

```text
Python version
WSL distribution
libyang version
Sysrepo version
Netopeer2 version
YANG modules/revisions
NETCONF host/port

device archetype count
device instance count
RFC 8348 component count
Energy Object count
Energy Object observability-class counts
Energy Objects with Power available
Energy Objects with State available
Energy Objects intentionally UNKNOWN / N/A
topology subgraph count

Group A UC count
Group B deferred count
total event count
events per UC

relationship counts by family
stable structural relationship count
physical dynamic relationship count
observability/discovery relationship count

controller identity collision checks
NETCONF topology reconstruction result
capability-discovery readiness component count

test counts
failures
blockers
```

Do not fabricate successful results.

---

# 36. Acceptance criteria

The increment is complete only when all of the following are true:

- `allrun5/` remains unchanged;
- all output is under `allrun51/`;
- one canonical demo network exists;
- six reusable topology subgraphs exist;
- device archetypes are separated from device instances;
- UC scenarios are implemented as overlays/patches over stable topology;
- all 14 Group A UCs are preserved;
- Group B remains deferred;
- total Group A events >= 122;
- per-UC minimum event counts are preserved;
- stable hardware identity is maintained across events;
- Energy Object identity is stable;
- every Energy Object has an explicit observability class;
- major Energy Objects have meaningful Power and/or State whenever grounded by the UC;
- unexplained `Power=- / State=- / Relationships=-` objects are eliminated;
- missing telemetry is not replaced by zero;
- `UNKNOWN` and `N/A` are explicit display semantics and do not violate YANG types;
- intentionally sparse Energy Objects are documented;
- `source-component-id` mapping remains correct;
- controller scope uses `(device-id, component-name)` normalization;
- all four GREEN relationship families remain represented;
- relationships are classified as structural, physical-dynamic, or observability-related;
- UC 2.13 distinguishes actual topology from controller knowledge;
- compact line-oriented console remains default;
- `allrun51/README.md` contains the required simulator-internals architecture view;
- `allrun51/README.md` contains the required T1-T6 six-topology view;
- no file under `allrun51/`, including README and generated docs, contains an exact reference to `allrun5`;
- all Markdown tables under `allrun51/docs/` have aligned pipe boundaries and rows no longer than 160 characters;
- NETCONF remains read-only;
- controller reconstruction can be tested from NETCONF-visible data;
- discovery-readiness components are explicitly documented;
- no RFC 9196 or `ietf-power-state-capabilities` operational data is fabricated;
- no capability values are derived from UC event state;
- no containers are used;
- no `<edit-config>`, YANG Push, RESTCONF, custom RPC, or custom notification is added.

Stop when the canonical topology-driven, controller-ready, discovery-ready, read-only GREEN simulator is working under:

```text
allrun51/
```

Future increments may add:

```text
RFC 9196 capability discovery
draft-claise-green-capability-discovery-03
external capability-aware controller
capability + live-state correlation
capability-aware decision support
controlled NETCONF configuration
```
