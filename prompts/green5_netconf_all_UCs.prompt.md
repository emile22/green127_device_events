# GREEN NETCONF All Event-Ready Use Cases — `allrun5`

Act as a senior IETF GREEN, YANG, NETCONF, Sysrepo, Netopeer2, WSL, and Python implementation engineer.

Work in the currently opened local `green` repository.

This increment extends the existing `minrun4` implementation into a new, isolated implementation under:

```text
allrun5/
```

The baseline sources are:

```text
green4_minimal_netconf_4_UCs.prompt.md
minrun4/
```

Treat `minrun4/` as a **read-only implementation reference**.

Do not modify, delete, rename, or reformat files in `minrun4/`.

All files created or modified by this task MUST be under:

```text
allrun5/
```

This includes source code, copied YANG modules, tests, scripts, logs, generated snapshots, test artifacts, documentation, temporary runtime state, and any local configuration templates.

Do not create implementation output elsewhere in the repository.

The primary use-case source is:

```text
https://github.com/emile22/draft-ietf-green-use-cases/blob/main/draft-ietf-green-use-cases.md
```

Use the terminology and intent of that draft. Do not silently replace its content with more generic GREEN examples.

The existing `minrun4` behavior is the implementation baseline. Preserve working behaviors whenever they are applicable.

---

# 1. Objective

Build a new GREEN NETCONF simulator under `allrun5/` that focuses on **all use cases with enough granularity to extract deterministic operational events**.

The simulator MUST:

- reuse the working design patterns of `minrun4`;
- preserve the existing Python/YANG/Sysrepo/Netopeer2 architecture unless a change is necessary;
- keep NETCONF read-only for this increment;
- expose real `ietf-hardware` and `ietf-power-and-energy` operational data;
- prepare stable RFC 8348 component identity and Energy Object mappings for future Power State capability discovery work, without implementing capability discovery in `allrun5`;
- use deterministic event sequences;
- double the event granularity of the current minimum event plan while preserving the use-case meaning;
- provide a compact line-oriented console layout by default, avoiding bordered tables and box-heavy UI;
- exercise all four GREEN Energy Object relationship families;
- provide compact human-readable relationship displays as well as raw YANG/NETCONF data;
- run Sysrepo and Netopeer2 natively under Ubuntu/WSL;
- keep the Windows Python environment separate;
- use no containers.

Do not implement NETCONF-driven control, `<edit-config>`, RESTCONF, or YANG Push in this increment.

---

# 2. First inspect the actual `minrun4` implementation

Before modifying anything:

1. inspect the complete `minrun4/` tree;
2. identify its Python package layout;
3. identify its event model;
4. identify its YANG adapter;
5. identify its Sysrepo bridge;
6. identify its Netopeer2 startup/status scripts;
7. identify its NETCONF client tests;
8. identify its interactive CLI and `ENTER/a/d/r/q` behavior;
9. identify its current rendering of:
   - `ietf-hardware`;
   - `ietf-power-and-energy`;
   - `source-component-id`;
   - Energy Object `relationship`;
10. identify all existing UC 2.1, UC 2.10, UC 2.13, and UC 2.14 event values and tests.

Report this inventory briefly.

Then copy/adapt the minimum necessary implementation into `allrun5/`.

Do not stop after reporting the inventory.

Do not assume that `minrun4` has exactly the layout described in this prompt; the actual code wins.

---

# 3. Use-case grouping by event granularity

Use exactly two groups.

## Group A — event-ready use cases implemented in `allrun5`

These use cases contain enough concrete states, actions, modes, data-processing steps, or transitions to support deterministic simulator events without changing their core meaning.

Implement all of them:

```text
UC 2.1  Incremental Application of the GREEN Framework

UC 2.2  Selective reduction of energy consumption in network parts
        proportional to traffic levels

UC 2.5  Indirect Energy Monitoring and control

UC 2.6  Consideration of other domains for obtention of end-to-end metrics

UC 2.7  Dynamic adjustment of network element throughput according to
        traffic levels in wireless transport networks

UC 2.8  Video streaming use case

UC 2.9  WLAN Network Energy Saving

UC 2.10 Fixed Network Energy Saving

UC 2.11 Energy Efficiency Network Management

UC 2.12 ISAC-enabled Energy-Aware Smart City Traffic Management

UC 2.13 Double Accounting Open issue

UC 2.14 Energy Efficiency Under Power Shortage

UC 2.15 Energy-Efficient Management of Distributed AI Training Workloads

UC 2.16 Network-level Cross Layer Energy Saving
```

For UC 2.6 and UC 2.11, the event sequence is a deterministic simulator representation of the processing stages explicitly described by the use case.

Do not claim that the exact event names are standardized by IETF.

## Group B — deferred because the current text is not granular enough

Do NOT implement runtime event series for these use cases in this increment:

```text
UC 2.3 Reporting on Lifecycle Management

UC 2.4 Real-time Energy Metering of Virtualised or Cloud-native Network Functions
```

Reason for deferral:

### UC 2.3

The current text is primarily lifecycle/carbon/energy-mix reporting and external metadata ingestion.

It does not define a sufficiently concrete operational event flow for the current NETCONF device simulator without inventing lifecycle transitions or external-data behavior.

### UC 2.4

The current text states the need for real-time metering of virtualized/cloud-native functions, but its GREEN requirements are still TODO.

It does not yet define enough concrete entities, correlation behavior, transitions, or control steps for a grounded event series.

Create:

```text
allrun5/docs/deferred_group_b.md
```

containing the two deferred UCs and the above reasons.

Do not invent events for Group B.

---

# 4. Output isolation

All implementation output MUST remain inside:

```text
allrun5/
```

Prefer a self-contained structure similar to the working `minrun4` structure.

For example, adapt as appropriate after inspection:

```text
allrun5/
  README.md
  pyproject.toml
  src/
  tests/
  yang/
  scripts/
  docs/
  logs/
  runtime/
```

Rules:

- `minrun4/` is read-only.
- Copy exact required YANG revisions into `allrun5/yang/`.
- Do not modify shared root YANG modules.
- Put generated NETCONF traces under `allrun5/logs/`.
- Put runtime snapshots/state under `allrun5/runtime/`.
- Add local generated files to `allrun5/.gitignore`.
- Do not write logs or snapshots into `minrun4/`.
- Do not create Docker files.

---

# 5. Runtime architecture

Preserve the baseline architecture:

```text
GREEN event simulator
        |
        v
internal Python models
        |
        v
existing/adapted YANG mapping
        |
        v
Sysrepo operational data
        |
        v
Netopeer2
        |
        | NETCONF over SSH
        v
Python ncclient
```

Keep accounting and scenario logic outside Sysrepo callbacks.

Do not create a second independent accounting implementation for NETCONF.

Prefer:

```text
scenario state
    -> one internal model
    -> one YANG adapter
    -> Sysrepo-facing adapter
    -> NETCONF
```

---

# 6. Windows / WSL execution model

Use this local architecture:

```text
Windows
-------
VS Code
Python 3.11 virtual environment
GREEN runtime/client-side tests where applicable
ncclient
        |
        | NETCONF/SSH
        v
localhost:<NETCONF_PORT>


Ubuntu under WSL
----------------
libyang
Sysrepo
Netopeer2
installed YANG modules
```

Requirements:

- do not install Sysrepo or Netopeer2 as Windows binaries;
- do not use Docker or containers;
- run Sysrepo and Netopeer2 natively inside Ubuntu/WSL;
- keep the Windows Python `.venv` separate from the WSL infrastructure;
- use `localhost` from Windows when WSL localhost forwarding works;
- if localhost is unavailable, detect the WSL address and use `NETCONF_HOST`;
- do not hard-code environment-specific IP addresses;
- preserve the currently working WSL distribution rather than creating a new distribution.

---

# 7. Preserve interactive runtime behavior

Preserve the working `minrun4` controls:

```text
[ENTER] next event
a       automatically run all remaining events
d       toggle live NETCONF operational-data trace
r       restart the complete demo
q       quit
```

Requirements:

- `ENTER` advances exactly one event;
- `a` runs all remaining Group A events across UC boundaries;
- `r` resets all use cases, counters, topology, relationships, and runtime state;
- `q` exits cleanly;
- `d` toggles the live operational-data trace without changing scenario state.

When `d` is enabled:

- show each Sysrepo operational-data request path;
- show the returned YANG data used for NETCONF `<get>`;
- label the output with current UC and event;
- append the same data to a log below `allrun5/logs/`;
- log each runtime snapshot even if there is no NETCONF client;
- do not log credentials;
- do not describe this as a complete SSH wire capture.

---

# 8. Event presentation

The default console UI MUST use a compact line-oriented layout.

Do NOT use bordered tables, box-drawing frames, large panels, or full-screen TUI layouts for the normal event display.

Prefer a compact form such as:

```text
UC2.10 U10-4 COMPONENT_SLEEP_PREPARED
HW     linecard-1=active  linecard-2=ready
ENERGY eo-lc1=60W/ON  eo-lc2=25W/ON
REL    switch-fabric ENABLING -> linecard-1,linecard-2
DIFF   linecard-2: 90->25W
Enter next | a auto | d netconf | r restart | q quit
```

The default display SHOULD fit comfortably in a normal terminal without horizontal scrolling.

Use one short line per logical section where possible:

```text
HW
ENERGY
REL
DIFF
```

Longer detailed views such as `relationships`, `json`, `xml`, and `diff` MAY expand vertically on demand.

If Rich or another console library is used, use it only for lightweight emphasis, alignment, syntax highlighting, and optional color.

Do NOT use Rich bordered tables or large panels by default.

Every event MUST have:

```text
[UC x.xx / EVENT-ID] EVENT_NAME
<one deterministic explanatory sentence shorter than 20 words>
```

The sentence MUST:

- contain fewer than 20 words;
- explain the purpose or effect of the event;
- use plain language;
- be deterministic;
- not be dynamically generated;
- not claim that the simulator-specific event name is standardized by IETF.

Add unit tests that check:
- every Group A event has exactly one non-empty description;
- every description has fewer than 20 words;
- every UC meets its required doubled event count;
- total Group A event count is at least 122;
- added events are uniquely identified and deterministically ordered.

---

# 9. Minimum event plan for every Group A use case

The event density MUST be doubled relative to the minimum semantic sequences listed below.

The listed event sequences remain the mandatory semantic backbone, but the implementation MUST add grounded intermediate events so that every Group A use case contains at least twice the number of events listed for that use case.

Required minimum event counts:

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

Minimum total for Group A:

```text
122 deterministic events
```

The added events MUST:

- be grounded in the corresponding GREEN use-case text and existing simulator semantics;
- represent meaningful intermediate observations, state transitions, topology changes, measurement steps, or recovery stages;
- not merely duplicate a previous event with a different name;
- preserve deterministic ordering;
- preserve cumulative-energy monotonicity;
- preserve existing relationship semantics;
- avoid inventing a standardized IETF event vocabulary.

Preserve existing `minrun4` event names and values for UC 2.1, UC 2.10, UC 2.13, and UC 2.14 where already implemented and correct.

Those existing events MUST remain present as anchor events inside the expanded sequences.

Do not change those values merely for cosmetic consistency.

For each use case, use the following sequence as the mandatory semantic backbone and add enough grounded intermediate events to reach the required doubled count.

## UC 2.1 — Incremental Application of the GREEN Framework

Mandatory backbone:

```text
U1-0 LEGACY_BASELINE
U1-1 COMPONENT_GREEN_ENABLED
U1-2 DEVICE_CONTROLLER_GREEN
U1-3 NETWORK_LEVEL_GREEN
```

Preserve the existing baseline/component/device/network progression from `minrun4`.

Missing telemetry MUST remain unknown, never zero.

## UC 2.2 — Selective reduction proportional to traffic

Mandatory backbone:

```text
U2-0 TRAFFIC_PEAK
U2-1 TRAFFIC_VALLEY
U2-2 TRAFFIC_RELOCATED
U2-3 COMPONENTS_SLEEPING
U2-4 TRAFFIC_RECOVERY
```

Ground the sequence in:

- traffic peaks and valleys;
- traffic relocation/concentration;
- component sleep/standby/hibernation/off;
- service continuity;
- recovery when demand returns.

## UC 2.5 — Indirect Energy Monitoring and control

Mandatory backbone:

```text
U5-0 TARGET_UNINSTRUMENTED
U5-1 EXTERNAL_METER_DISCOVERED
U5-2 INDIRECT_MEASUREMENT_ACTIVE
U5-3 UPSTREAM_POWER_CONTROL_AVAILABLE
```

Use a PDU or PoE switch as the external energy-management entity.

Do not fabricate direct measurements on an uninstrumented target.

## UC 2.6 — Other domains for end-to-end metrics

Mandatory backbone:

```text
U6-0 DOMAIN_METRICS_AVAILABLE
U6-1 METRICS_MAPPED
U6-2 DOUBLE_COUNTING_GUARD_APPLIED
U6-3 END_TO_END_METRIC_COMPOSED
```

Represent:

- domain-specific metrics;
- mapping/transformation;
- domain-boundary accounting protection;
- composed end-to-end view.

Keep external-domain semantics as simulator/controller metadata unless represented by an actual YANG module already present.

## UC 2.7 — Wireless transport throughput adjustment

Mandatory backbone:

```text
U7-0 PEAK_TRAFFIC_LINK_POWER
U7-1 NORMAL_TRAFFIC_DETECTED
U7-2 RADIO_LINK_POWER_REDUCED
U7-3 PEAK_TRAFFIC_RESTORED
```

Represent dynamic power adjustment according to observed traffic.

## UC 2.8 — Video streaming

Mandatory backbone:

```text
U8-0 HIGH_UNICAST_DEMAND
U8-1 MULTICAST_DELIVERY_ENABLED
U8-2 CACHE_PLACED_NEAR_USERS
U8-3 REDUNDANT_BACKBONE_TRAFFIC_REDUCED
```

Do not invent a standardized GREEN multicast-control protocol.

The event series is a deterministic demonstration of the optimization choices described by the UC.

## UC 2.9 — WLAN Network Energy Saving

Mandatory backbone:

```text
U9-0 AP_ACTIVE
U9-1 AP_LOW_POWER
U9-2 AP_HIBERNATING
U9-3 POE_POWER_OFF
U9-4 AP_REACTIVATED
```

Preserve the UC distinction among:

- active;
- low-power;
- hibernation;
- PoE power-off;
- wake-up/recovery.

## UC 2.10 — Fixed Network Energy Saving

Preserve the existing `minrun4` series, including:

```text
U10-0 TRAFFIC_HIGH
U10-1 TRAFFIC_LOW
U10-2 COMPONENT_SLEEP
U10-3 TRAFFIC_BURST
```

Preserve interval versus cumulative energy semantics.

## UC 2.11 — Energy Efficiency Network Management

Mandatory backbone:

```text
U11-0 INVENTORY_DISCOVERED
U11-1 REALTIME_TELEMETRY_COLLECTED
U11-2 CAPABILITIES_AND_LEGACY_CLASSIFIED
U11-3 NETWORK_ENERGY_TREND_AGGREGATED
```

Represent the management functions explicitly described by the UC:

- visibility;
- telemetry;
- energy-saving capability/status;
- legacy versus optimized classification;
- aggregated network trends.

For this increment, any `capability` or `legacy/optimized capability classification` used by UC 2.11 MUST remain explicitly labeled simulator/controller metadata unless it is represented by an already installed YANG module.

Do NOT model UC 2.11 capability classification as `ietf-system-capabilities` or `ietf-power-state-capabilities` in `allrun5`.

Future `caprun10+` work will add `draft-claise-green-capability-discovery-03` and RFC 9196 capability data.

## UC 2.12 — ISAC-enabled Energy-Aware Smart City Traffic Management

Mandatory backbone:

```text
U12-0 PEAK_HIGH_RESOLUTION_SENSING
U12-1 LOW_TRAFFIC_DETECTED
U12-2 SENSING_LOW_POWER
U12-3 ENERGY_AWARE_TRAFFIC_REROUTE
U12-4 CRITICAL_SENSING_PRESERVED
```

Critical functions remain operational.

Non-critical sensing may adapt according to context.

## UC 2.13 — Double Accounting Open issue

Preserve the existing `minrun4` sequence and values:

```text
U13-0 RAW_MEASUREMENTS
U13-1 TOPOLOGY_DISCOVERED
U13-2 NEXT_MEASUREMENT_INTERVAL
U13-3 TOPOLOGY_INCOMPLETE
```

Accounting MUST remain topology-driven.

Do not infer de-duplication from numerical equality.

## UC 2.14 — Energy Efficiency Under Power Shortage

Preserve the existing `minrun4` sequence and behavior:

```text
U14-0 GRID_NORMAL
U14-1 GRID_FAILURE
U14-2 BATTERY_OPERATION
U14-3 ENERGY_CRITICAL
U14-4 GRID_RESTORED
```

Essential network service remains operational during the constrained stage.

## UC 2.15 — Distributed AI Training Workloads

Mandatory backbone:

```text
U15-0 TRAINING_FULL_CLUSTER
U15-1 ENERGY_AWARE_SCHEDULE_WINDOW
U15-2 DATA_TRANSFER_OPTIMIZED
U15-3 ACTIVE_NODES_ADJUSTED
```

Ground these in:

- East-West traffic monitoring;
- energy-aware scheduling;
- compression/data-transfer reduction;
- resource co-location where represented;
- dynamic active-node allocation.

Do not invent an AI-training protocol.

## UC 2.16 — Network-level Cross Layer Energy Saving

Mandatory backbone:

```text
U16-0 MULTILAYER_NORMAL
U16-1 IP_LINECARD_SLEEP_REQUEST
U16-2 UNDERLAY_DEPENDENCIES_COORDINATED
U16-3 MULTILAYER_LOW_POWER_STABLE
U16-4 MULTILAYER_RESTORED
```

Represent coordinated energy saving across IP overlay and transport underlay.

Do not model an L3 shutdown as independent when it affects L0/L1/L2 resources.

---

# 10. Deterministic values

For all newly added events:

- choose deterministic values;
- use stable Energy Object IDs;
- use stable hardware component names;
- use stable UUIDs;
- keep units consistent with the actual YANG schema;
- keep interval and cumulative energy distinct;
- ensure cumulative energy never decreases after an event;
- reset cumulative values only on explicit runtime restart;
- do not silently reinterpret YANG units;
- document simulator-only assumptions.

Create a single data source for event fixtures rather than scattering numeric constants across tests and rendering code.

---

# 11. Energy Object relationship model

Use the operational `relationship` list of `ietf-power-and-energy`.

Support all four relationship families and their inverse identities:

```text
metering      / metered-by
aggregating   / aggregated-by
powering      / powered-by
enabling      / enabled-by
```

Semantics:

```text
A METERING B
=> A measures B

A METERED-BY B
=> B measures A

A AGGREGATING B
=> A aggregates Energy Management information about B

A AGGREGATED-BY B
=> B aggregates Energy Management information about A

A POWERING B
=> A provides electrical power to B

A POWERED-BY B
=> B provides electrical power to A

A ENABLING B
=> B functionally depends on A being operational

A ENABLED-BY B
=> A functionally depends on B being operational
```

Do not confuse:

- hardware containment with Energy Object relationships;
- traffic aggregation with the `aggregating` Energy Management relationship;
- physical powering with functional enablement;
- `source-component-id` with relationship peer identity.

`source-component-id` remains the leaf that maps an Energy Object to its RFC 8348 hardware component.

Hardware hierarchy must come only from RFC 8348 hierarchy data.

Do not infer hardware hierarchy from Energy Object names.

The relationship list is read-only operational data.

Do not add a writable relationship list under `energy-control`.

---

# 12. Mandatory relationship coverage

For **each relationship family**, demonstrate the relationship in **at least three distinct Group A use cases**.

For every selected use case, the relationship MUST be observable in **at least four events**.

This is intentionally stronger than merely showing four relationship instances total.

The same event may demonstrate more than one relationship family when semantically correct.

Use at least the following coverage matrix.

## A. Metering / metered-by

Use at minimum:

```text
UC 2.5  Indirect Energy Monitoring and control
UC 2.9  WLAN Network Energy Saving
UC 2.13 Double Accounting
```

Examples:

```text
physical-meter  METERING    legacy-device
legacy-device   METERED-BY  physical-meter

poe-port        METERING    ap-1
ap-1            METERED-BY  poe-port

upstream-meter  METERING    server-A
server-A        METERED-BY  upstream-meter
```

Ensure at least four events in each of those three UCs expose or intentionally change the metering relationship.

## B. Aggregating / aggregated-by

Use at minimum:

```text
UC 2.6  Other domains for end-to-end metrics
UC 2.11 Energy Efficiency Network Management
UC 2.12 ISAC-enabled Energy-Aware Smart City Traffic Management
```

Use actual Energy Management information aggregation.

Do NOT use traffic concentration alone as an `aggregating` relationship.

Examples:

```text
domain-energy-aggregator  AGGREGATING    domain-energy-object
domain-energy-object      AGGREGATED-BY  domain-energy-aggregator

network-energy-aggregator AGGREGATING    router-energy-object
router-energy-object      AGGREGATED-BY  network-energy-aggregator

isac-energy-aggregator    AGGREGATING    roadside-unit-energy-object
roadside-unit-energy-object AGGREGATED-BY isac-energy-aggregator
```

Ensure at least four events in each of those three UCs expose or intentionally change the aggregation relationship.

## C. Powering / powered-by

Use at minimum:

```text
UC 2.5  Indirect Energy Monitoring and control
UC 2.9  WLAN Network Energy Saving
UC 2.14 Energy Efficiency Under Power Shortage
```

Examples:

```text
pdu-outlet      POWERING    legacy-device
legacy-device   POWERED-BY  pdu-outlet

poe-port        POWERING    ap-1
ap-1            POWERED-BY  poe-port

grid-source     POWERING    router-A
router-A        POWERED-BY  grid-source
```

For UC 2.14, make the transition from grid to backup source explicit in operational relationship data when supported by the simulator.

Ensure at least four events in each of those three UCs expose or intentionally change the power-source relationship.

## D. Enabling / enabled-by

Use at minimum:

```text
UC 2.9  WLAN Network Energy Saving
UC 2.10 Fixed Network Energy Saving
UC 2.16 Network-level Cross Layer Energy Saving
```

Use functional dependencies, not electrical power flow.

Examples:

```text
ap-baseband       ENABLING    ap-radio-5ghz
ap-radio-5ghz     ENABLED-BY  ap-baseband

switch-fabric     ENABLING    linecard-1
linecard-1        ENABLED-BY  switch-fabric

transport-module  ENABLING    dependent-ip-function
dependent-ip-function ENABLED-BY transport-module
```

Only use these examples when they match the actual simulated topology.

Ensure at least four events in each of those three UCs expose or intentionally change the functional dependency relationship.

---

# 13. Relationship symmetry and representation

When both participants are represented in the same simulator domain, expose both perspectives for selected demonstration relationships:

```text
A METERING B
B METERED-BY A

A AGGREGATING B
B AGGREGATED-BY A

A POWERING B
B POWERED-BY A

A ENABLING B
B ENABLED-BY A
```

Do not fabricate the inverse in the raw NETCONF display if it is absent from the actual operational datastore.

If the UI derives an inverse for readability, mark it explicitly:

```text
[derived view]
```

Prefer that the simulator datastore itself contains the paired relationships for the mandatory relationship-coverage scenarios so tests can verify symmetry directly.

Use stable peer identifiers.

Preserve the exact raw `identityref` value in raw JSON/XML views.

---

# 14. Compact line-oriented relationship display

The default human-readable console MUST be compact and line-oriented.

Do NOT render the normal event view as bordered tables.

Do NOT use box-drawing frames around HARDWARE, ENERGY OBJECTS, RELATIONSHIPS, or UC interpretation.

The default event view MUST show the same logical information in compact lines, for example:

```text
UC2.10 U10-4 COMPONENT_SLEEP_PREPARED
HW     switch-fabric=active  linecard-1=active  linecard-2=ready
ENERGY eo-fabric=45W/ON  eo-lc1=60W/ON  eo-lc2=25W/ON
REL    eo-fabric ENABLING -> eo-lc1,eo-lc2
DIFF   eo-lc2: power 90->25W
Enter next | a auto | d netconf | r restart | q quit
```

Each Energy Object compact entry SHOULD preserve, when applicable:

```text
Energy Object ID
source component
Power or Energy value
operational Power State
compact relationship summary
```

A compact Energy Object line may use:

```text
eo-lc2[linecard-2]=25W/SLEEP REL=ENABLED-BY(1)
```

The detailed `relationships` view MAY expand vertically, but SHOULD still avoid decorative box borders.

Example:

```text
RELATIONSHIPS
eo-switch-fabric ENABLING -> eo-linecard-1, eo-linecard-2
eo-linecard-1 ENABLED-BY -> eo-switch-fabric
eo-linecard-2 ENABLED-BY -> eo-switch-fabric
```

For all relationship types, display the exact directional identity returned by the datastore.

Do not collapse `metering` and `metered-by` into an ambiguous label.

When a UI-only inverse is derived for readability, mark it explicitly:

```text
[derived view]
```

The default console must prioritize information density and readability over decorative formatting.

---

# 15. Raw and human-friendly NETCONF views

Preserve raw protocol data while making the default view readable.

Support, adapting existing `minrun4` CLI conventions:

```text
summary
relationships
json
xml
diff
```

The default MUST be a concise, compact, line-oriented summary with no bordered tables.

Keep the normal event display to a small number of terminal lines where practical.

`json` MUST preserve complete normalized YANG JSON values.

`xml` MUST show the real NETCONF XML reply.

`relationships` MUST show the directional Energy Object graph.

`diff` MUST show meaningful changes between consecutive events, including relationship additions/removals.

Formatting MUST NOT alter underlying values.

---

# 16. `source-component-id` handling

Remember:

```text
/ietf-power-and-energy:energy-objects/energy-object/source-component-id
```

is the Energy Object leaf referring to the RFC 8348 hardware component name.

Use it to present:

```text
Energy Object -> Source component
```

Do not treat it as an Energy Object relationship.

Example:

```text
eo-router-a
  source-component-id = router-A
```

maps to the RFC 8348 component named `router-A`.

The hardware UUID remains a separate property of that hardware component.

Keep distinct:

```text
energy_object_id
hardware_component_name
hardware_component_uuid
relationship_peer_id
```

---

# 17. Capability-discovery readiness contract for future `caprun10+`

`allrun5` MUST be prepared for later integration with:

```text
draft-claise-green-capability-discovery-03
RFC 9196 ietf-system-capabilities
```

but MUST NOT implement those capability models in this increment.

The purpose of this section is only to ensure that the existing RFC 8348 hardware inventory, GREEN Energy Objects, and GREEN relationships provide stable correlation points for later capability-discovery work.

## 17.1 Do not implement discovery in `allrun5`

Do NOT add to `allrun5`:

```text
ietf-system-capabilities
ietf-power-state-capabilities
RFC 9196 capability operational data
Power State capability provider callbacks
capability-specific NETCONF filters
capability-gated control
```

Those belong to future `caprun10+` work.

`allrun5` remains a read-only GREEN device simulator exposing:

```text
RFC 8348 hardware
+
ietf-power-and-energy operational state
+
GREEN Energy Object relationships
```

## 17.2 Stable RFC 8348 component identity

Every hardware Component selected for future capability discovery MUST have a stable:

```text
hardware/component/name
hardware/component/uuid
```

The `name` and `uuid` MUST remain distinct values.

The Component name MUST remain stable across event transitions, UC transitions, auto mode, NETCONF reads, and restart.

A restart may reset runtime state, but it MUST NOT rename a Component.

Do not derive Component names from transient event state.

## 17.3 Stable Energy Object to hardware mapping

For every Energy Object selected for future capability discovery:

```text
/ietf-power-and-energy:energy-objects/energy-object/source-component-id
```

MUST resolve to exactly one existing RFC 8348:

```text
/ietf-hardware:hardware/component/name
```

For the current schema, the future capability correlation key is the RFC 8348 Component `name`.

Keep separate:

```text
energy_object_id
hardware_component_name
hardware_component_uuid
relationship_peer_id
```

Do not replace the current `source-component-id` leafref with UUID.

## 17.4 Select future capability-demo Components now

Identify and document a small stable set of existing `allrun5` Components that future `caprun10+` work can use to attach Power State capabilities.

Prefer Components already used by:

```text
UC 2.9  WLAN Network Energy Saving
UC 2.10 Fixed Network Energy Saving
UC 2.16 Network-level Cross Layer Energy Saving
```

Prefer semantically useful Components such as, when they actually exist in the simulator:

```text
AP baseband
AP radio
switch fabric
linecard
transport module
dependent IP function
```

Do NOT create artificial hardware Components solely for future discovery when an equivalent existing Component can be reused.

Create:

```text
allrun5/docs/capability_discovery_readiness.md
```

with a table containing at least:

```text
UC
hardware_component_name
hardware_component_uuid
energy_object_id
source_component_id
relevant_relationships
reason_selected_for_future_capability_demo
```

## 17.5 Hardware-backed dependency examples

For selected future capability-demo Components using `enabling / enabled-by`, both relationship participants MUST map to real RFC 8348 hardware Components through their own `source-component-id`, where the simulated entity is physically represented in RFC 8348.

Example:

```text
eo-switch-fabric
  source-component-id = switch-fabric
  ENABLING -> eo-linecard-1

eo-linecard-1
  source-component-id = linecard-1
  ENABLED-BY -> eo-switch-fabric
```

Do not fabricate hardware containment from these relationships.

Do not reinterpret `enabling` as electrical powering.

## 17.6 Capability information remains metadata in `allrun5`

If a use case internally needs concepts such as:

```text
sleep-capable
energy-saving-capable
legacy
optimized
supported low-power mode
```

and those concepts are not represented by the currently installed YANG modules, they MUST remain simulator/controller metadata.

They MUST NOT appear in raw NETCONF output as invented YANG leaves.

In particular, UC 2.11 — Energy Efficiency Network Management event `U11-2 CAPABILITIES_AND_LEGACY_CLASSIFIED` MUST NOT be presented as RFC 9196 / `ietf-power-state-capabilities` data in `allrun5`.

Future `caprun10+` work will provide real capability data.

## 17.7 Readiness tests

Add tests that fail unless every Component listed in `allrun5/docs/capability_discovery_readiness.md` satisfies all of the following:

```text
RFC 8348 Component exists
Component name is stable
Component UUID exists
Component UUID is distinct from Component name
Energy Object exists
Energy Object source-component-id resolves to the Component name
selected relationship peers resolve to known Energy Objects
hardware-backed enabling/enabled-by peers resolve to RFC 8348 Components where expected
no RFC 9196 capability data is fabricated by allrun5
no ietf-power-state-capabilities data is fabricated by allrun5
```

Also test that the selected Component mappings remain stable across all events in the relevant UCs and after `r` restart.

## 17.8 Future integration boundary

Document this intended future layering:

```text
allrun5
  RFC 8348 hardware
  GREEN Energy Objects
  live operational state
  GREEN relationships
  stable Component correlation
        |
        v
caprun10
  RFC 9196
  + draft-claise-green-capability-discovery-03
  Power State capability advertisement
        |
        v
caprun11+
  external NETCONF controller
  joins capability + live state
```

The readiness work in `allrun5` MUST NOT create a dependency on future `caprun10+` code.

---

# 18. Group A runtime ordering

Run the Group A use cases in numeric order:

```text
UC 2.1
UC 2.2
UC 2.5
UC 2.6
UC 2.7
UC 2.8
UC 2.9
UC 2.10
UC 2.11
UC 2.12
UC 2.13
UC 2.14
UC 2.15
UC 2.16
```

Display a compact separator before each UC.

Prefer:

```text
--- UC 2.9 WLAN Network Energy Saving ---
```

After a series, prefer one compact transition line:

```text
UC 2.9 complete -> UC 2.10 Fixed Network Energy Saving
```

Do not use multi-line decorative separator blocks in the default console.

Do not execute Group B UCs.

At the end print:

```text
Group A completed: 14 use cases
Group B deferred: 2 use cases
```

---

# 19. Simulator metadata versus YANG

Maintain a strict distinction:

```text
standard/draft YANG operational data
                 versus
simulator/controller metadata
```

Never invent YANG leaves for concepts absent from the current modules.

Possible simulator-only metadata includes:

```text
event name
event description
UC number
traffic condition
video-delivery strategy
battery percentage if unsupported
critical-service classification if unsupported
baseline source
cross-domain mapping status
accounting result
optimization rationale
```

Raw NETCONF output must contain only data represented by installed YANG modules.

Human-readable UC interpretation may combine YANG data and clearly labeled simulator metadata.

---

# 20. YANG modules

Reuse the exact YANG revisions already validated by the working baseline.

At minimum:

```text
ietf-power-and-energy
ietf-hardware
```

plus their exact dependencies.

Copy required YANG files into:

```text
allrun5/yang/
```

Do not silently download or replace revisions.

Before implementation report:

```text
module name
revision
source path in minrun4
copied destination in allrun5
```

Validate schemas using the same proven tools as `minrun4`.

Use `pyang` for schema validation/tree generation.

Use `yanglint` for instance validation when available.

Do not claim `pyang` validates arbitrary JSON instance data.

---

# 21. NETCONF scope

This increment remains read-only.

Implement/test:

```xml
<get>
```

and preserve `<get-config>` only if it already works and is useful.

Do NOT add:

```text
<edit-config> energy-control
NETCONF-driven scenario changes
NETCONF-driven power-state changes
custom GREEN RPCs
custom GREEN notifications
YANG Push
RESTCONF
```

Runtime events drive state.

NETCONF observes state.

---

# 22. NETCONF tests

Reuse the working `minrun4` NETCONF test approach.

Create Group A integration tests below:

```text
allrun5/tests/netconf/
```

At minimum test:

- connection to Netopeer2;
- RFC 8348 hardware retrieval;
- `ietf-power-and-energy` retrieval;
- stable `source-component-id` mapping;
- all 14 Group A series are reachable;
- every Group A UC meets its doubled event minimum from Section 9;
- every event has a description shorter than 20 words;
- event ordering is deterministic;
- restart returns to UC 2.1 first event;
- auto mode crosses all UC boundaries;
- raw JSON and XML remain parseable;
- relationship summary does not modify raw identities;
- relationship diffs correctly show additions/removals.

Add dedicated tests for each relationship family.

---

# 23. Mandatory relationship tests

Create tests that fail unless all of these are true.

## Metering family

At least three distinct UCs:

```text
UC 2.5
UC 2.9
UC 2.13
```

Each contributes at least four events containing or changing:

```text
metering / metered-by
```

## Aggregation family

At least three distinct UCs:

```text
UC 2.6
UC 2.11
UC 2.12
```

Each contributes at least four events containing or changing:

```text
aggregating / aggregated-by
```

## Power-source family

At least three distinct UCs:

```text
UC 2.5
UC 2.9
UC 2.14
```

Each contributes at least four events containing or changing:

```text
powering / powered-by
```

## Functional-enablement family

At least three distinct UCs:

```text
UC 2.9
UC 2.10
UC 2.16
```

Each contributes at least four events containing or changing:

```text
enabling / enabled-by
```

Also test:

- forward and inverse semantics;
- peer IDs resolve to known simulator Energy Objects where expected;
- no self-relationships;
- no duplicate peer within the same relationship type;
- no accidental conversion between relationship families;
- relationship state resets correctly on `r`.

---

# 24. UC-specific tests

Create at least one focused test module per implemented UC.

Prefer names such as:

```text
allrun5/tests/uc/test_uc01_incremental.py
allrun5/tests/uc/test_uc02_selective_reduction.py
allrun5/tests/uc/test_uc05_indirect_monitoring.py
allrun5/tests/uc/test_uc06_cross_domain_metrics.py
allrun5/tests/uc/test_uc07_wireless_transport.py
allrun5/tests/uc/test_uc08_video_streaming.py
allrun5/tests/uc/test_uc09_wlan.py
allrun5/tests/uc/test_uc10_fixed_network.py
allrun5/tests/uc/test_uc11_network_management.py
allrun5/tests/uc/test_uc12_isac.py
allrun5/tests/uc/test_uc13_double_accounting.py
allrun5/tests/uc/test_uc14_power_shortage.py
allrun5/tests/uc/test_uc15_ai_training.py
allrun5/tests/uc/test_uc16_cross_layer.py
```

Adapt names to the actual copied baseline conventions if needed.

Do not create empty placeholder tests.

---

# 25. Preserve critical existing semantics

Preserve all applicable correctness rules from `minrun4`, especially:

- missing measurement is unknown, never zero;
- interval energy and cumulative energy are different;
- cumulative energy is monotonic between restarts;
- accounting follows topology, not numerical coincidence;
- Energy Object ID, hardware component name, and hardware UUID remain distinct;
- `source-component-id` maps an Energy Object to RFC 8348 hardware;
- relationship topology is separate from hardware containment;
- operational `power-state/oper` is observed state;
- do not treat a requested/configuration state as observed operational truth;
- unsupported capability is unknown, not false/zero;
- simulator metadata is never presented as standardized YANG.

---

# 26. Health checks

Before NETCONF tests, verify:

```text
WSL distribution available
Sysrepo available inside WSL
Netopeer2 running inside WSL
NETCONF port listening
required YANG modules installed
Windows ncclient can connect
```

Infrastructure failure messages MUST be clearly distinguishable from GREEN functional test failures.

Do not report a missing WSL service as an accounting failure.

---

# 27. Service scripts

Adapt the working `minrun4` service scripts into:

```text
allrun5/scripts/
```

Provide concise commands to:

```text
start Netopeer2 in WSL
stop Netopeer2
show status
list Sysrepo modules
verify NETCONF port
show WSL address fallback
```

Do not create container scripts.

Do not require an administrator to re-install modules for every run.

---

# 28. Documentation outputs

Create at least:

```text
allrun5/README.md
allrun5/docs/use_case_groups.md
allrun5/docs/deferred_group_b.md
allrun5/docs/relationship_coverage.md
allrun5/docs/event_catalog.md
allrun5/docs/capability_discovery_readiness.md
```

`use_case_groups.md` MUST list Group A and Group B.

`relationship_coverage.md` MUST contain a matrix:

```text
relationship family
UC
event IDs
forward identity
inverse identity
Energy Objects involved
```

`capability_discovery_readiness.md` MUST list the stable RFC 8348 Components selected for future `caprun10+` capability discovery and their Energy Object mappings.

`event_catalog.md` MUST list all expanded events in execution order and MUST contain at least 122 Group A events in total, with:

```text
UC number
UC title
event ID
event name
<20-word description
main state change
relationship families exercised
YANG-visible data
simulator-only metadata
```

---

# 29. README requirements

Document:

- the purpose of `allrun5`;
- that `minrun4` was used as read-only baseline;
- Group A and Group B;
- why Group B is deferred;
- Windows/WSL architecture;
- Sysrepo role;
- Netopeer2 role;
- ncclient role;
- YANG revisions;
- startup commands;
- runtime controls;
- compact line-oriented default console layout;
- doubled event-density requirement and actual event counts;
- relationship semantics;
- relationship coverage matrix;
- capability-discovery readiness boundary and selected future capability-demo Components;
- summary/json/xml/relationships/diff views;
- tests;
- current read-only limitation;
- planned future work for Group B and NETCONF control.

---

# 30. Before implementation

Before writing `allrun5`, report briefly:

```text
minrun4 structure found
working baseline commands
existing four UC series found
YANG revisions found
Sysrepo/Netopeer2 integration found
existing runtime controls found
existing console rendering found
plan to convert default rendering to compact line-oriented output
existing relationship support found
current event counts and exact doubled target counts
candidate stable RFC 8348 Components for future capability discovery
files/directories to create in allrun5
```

Then continue.

Do not ask for confirmation.

Do not stop at the plan.

---

# 31. After implementation

Run all applicable checks from the new directory.

Examples, adapt to actual baseline layout:

```powershell
cd allrun5
python -m green --auto --interval 0
pytest -v
pytest tests/netconf -v
```

Run WSL-native infrastructure checks as required.

Report exact results for:

```text
Python version
WSL distribution
libyang version
Sysrepo version
Netopeer2 version
installed YANG modules/revisions
NETCONF host
NETCONF port
Group A UC count
Group B UC count
total event count
confirmation that total Group A events >= 122
events per UC
confirmation that each UC meets its doubled minimum
relationship events per family
relationship UCs per family
capability-readiness Components selected
capability-readiness mapping test results
test counts and failures
```

Do not fabricate successful results.

If a dependency is unavailable, report exactly what worked and what remains blocked.

---

# 32. Acceptance criteria

The increment is complete only when all of the following are true:

- `minrun4/` remains unchanged;
- all task-created implementation output is under `allrun5/`;
- Group A contains and runs all 14 specified event-ready use cases;
- Group B contains only UC 2.3 and UC 2.4 and is documented but not simulated;
- every Group A UC meets the doubled event minimum defined in Section 9;
- Group A contains at least 122 deterministic events in total;
- the added events are meaningful intermediate steps, not renamed duplicates;
- every event has exactly one explanatory sentence shorter than 20 words;
- the default console uses a compact line-oriented layout;
- the default console does not use bordered tables, box-heavy panels, or full-screen TUI rendering;
- detailed relationship/XML/JSON views may expand on demand without changing underlying values;
- existing UC 2.1, UC 2.10, UC 2.13, and UC 2.14 semantics are preserved from `minrun4`;
- NETCONF remains read-only;
- Sysrepo and Netopeer2 run under WSL, not containers;
- Windows Python/ncclient remains separate from WSL infrastructure;
- RFC 8348 hardware data is retrievable;
- GREEN Energy Objects are retrievable;
- `source-component-id` mapping is preserved;
- a documented set of stable RFC 8348 Components is selected for future capability discovery;
- each selected Component has a stable name and distinct UUID;
- each selected Energy Object maps to its RFC 8348 Component through `source-component-id`;
- selected hardware-backed `enabling/enabled-by` examples resolve to RFC 8348 Components where expected;
- `allrun5` does not fabricate RFC 9196 or `ietf-power-state-capabilities` data;
- UC 2.11 capability classification remains clearly simulator/controller metadata in this increment;
- `allrun5/docs/capability_discovery_readiness.md` is generated and tested;
- all four relationship families are represented;
- each relationship family appears in at least three distinct Group A UCs;
- each selected UC contributes at least four relationship-bearing events for that family;
- forward/inverse relationship semantics are tested;
- aggregation relationships represent Energy Management aggregation, not traffic aggregation;
- powering relationships represent electrical power topology;
- enabling relationships represent functional dependency;
- metering relationships represent measurement topology;
- raw NETCONF XML/JSON is preserved;
- human-friendly relationship rendering is available;
- relationship diffs are available between events;
- restart resets all state correctly;
- auto mode runs the entire Group A catalog;
- all tests are deterministic;
- unsupported concepts remain simulator metadata;
- no containers are used;
- no `<edit-config>`, YANG Push, RESTCONF, custom RPC, or custom notification is added.

Stop after the read-only NETCONF simulator for all Group A use cases and the mandatory relationship coverage is working.

Future work will separately refine and implement Group B:

```text
UC 2.3 Reporting on Lifecycle Management
UC 2.4 Real-time Energy Metering of Virtualised or Cloud-native Network Functions
```

Future work will also add Power State capability discovery through:

```text
draft-claise-green-capability-discovery-03
RFC 9196 ietf-system-capabilities
```

in separate `caprun10+` increments, using the stable RFC 8348 correlation prepared here.

It may later add controlled NETCONF configuration behavior.
