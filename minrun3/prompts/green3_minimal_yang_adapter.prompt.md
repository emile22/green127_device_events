# Minimal GREEN YANG Adapter Implementation Prompt

Act as a senior Python, YANG, and network-management implementation engineer.

Work in the currently opened local `green` repository.

The runtime and UC 2.13 / UC 2.10 prototype already exist or are being implemented. This increment adds the **smallest real YANG integration layer** on top of the existing Python models and accounting logic.

Do NOT redesign the working runtime. Do NOT replace the existing `EnergyObject`, topology, accounting, simulator, or interactive console unless a small adapter hook is required.

Do NOT implement NETCONF, RESTCONF, YANG Push, sysrepo, Netopeer2, ConfD, or a database yet.

The goal is:

```text
existing Python runtime
        ↓
YANG adapter
        ↓
real IETF/draft YANG modules
        ↓
pyang validation
        ↓
validated sample instance data
```

## References

Use the exact modules/specifications relevant to the prototype:

- `draft-ietf-green-power-and-energy-yang-04`
- `draft-ietf-green-framework-02`
- `draft-ietf-green-use-cases-02`
- RFC 8348 / `ietf-hardware`

Do not invent YANG nodes, identities, RPCs, notifications, or paths. Treat Internet-Drafts as evolving work and record the exact revision/version used.

## Scope

Implement only:

1. local storage of required YANG modules;
2. `pyang` validation;
3. a minimal Python-to-YANG adapter;
4. mapping of the existing Python `EnergyObject` model to the actual GREEN YANG structure;
5. mapping of RFC 8348 hardware component identity;
6. mapping of GREEN relationships used by UC 2.13;
7. deterministic sample instance data;
8. instance validation where practical;
9. tests for the mapping.

Do not implement transport protocols in this increment.

## Repository layout

Prefer:

```text
yang/
  ietf-power-and-energy.yang
  ietf-hardware.yang
  dependencies/

src/
  green/
    yang_adapter.py

examples/
  pdu-instance.json
  hardware-instance.json

tests/
  test_yang_adapter.py
```

Adapt names to actual module filenames and repository conventions.

Do not modify upstream YANG content merely to make Python code easier.

## Real YANG modules

Use the YANG source from the referenced IETF draft/RFC. Store the module files under `yang/` and preserve the original text.

If imports are required, include the minimum dependency set under `yang/` or `yang/dependencies/`.

Record where each module came from.

## pyang validation

Use `pyang` with the project Python 3.11 environment.

If not installed, add it as a development/test dependency.

Run commands equivalent to:

```powershell
pyang -p yang yang\ietf-power-and-energy.yang
pyang -p yang -f tree yang\ietf-power-and-energy.yang
```

If dependencies use a separate directory, include it in the search path.

Do not report validation success unless the command actually succeeds.

If the published draft module itself has a validation problem, report the exact error and do not silently patch it.

## Python-to-YANG adapter

Keep the internal Python model separate from the YANG representation:

```text
Python EnergyObject
        ↓
yang_adapter.py
        ↓
ietf-power-and-energy instance structure
```

The accounting engine must continue to operate on internal Python models, not raw YANG dictionaries.

## Identity mapping

Keep these distinct:

```text
energy_object_id
hardware_component_name
hardware_component_uuid
```

Map them carefully using the actual schema as authoritative.

Expected mapping:

```text
EnergyObject.energy_object_id
    -> /energy-objects/energy-object/id

EnergyObject.hardware_component_name
    -> source-component-id
       when the actual leafref targets hw:component/hw:name

EnergyObject.hardware_component_uuid
    -> controller-side correlation with RFC 8348 uuid
```

Do not substitute UUID for `hw:name` if that violates the actual leafref.

Document any prose/schema discrepancy.

## RFC 8348 hardware instance

Create minimal deterministic hardware inventory data for:

```text
upstream-meter
server-A
server-B
```

Each component should have a stable `name` and `uuid` where supported by RFC 8348.

The GREEN Energy Objects must correlate to these hardware components through the actual YANG-defined reference.

## GREEN Energy Objects

Generate YANG-compatible instance data for:

```text
upstream-meter
server-A
server-B
```

Map current runtime data only to nodes that actually exist in the YANG module.

Do not create custom leaves inside the standard/draft tree for:

- event names;
- accounting boundaries;
- naive totals;
- accounted totals;
- exclusion explanations.

Those remain controller/runtime metadata.

## Energy values and units

Map the runtime energy values to the relevant consumed-energy leaves in the GREEN module.

Use `Wh` as the internal canonical unit.

The draft analysis found a discrepancy between the declared unit and descriptive text. Do not modify the YANG module.

Instead:

1. document the discrepancy;
2. define the adapter convention explicitly;
3. make any conversion explicit;
4. never silently multiply or divide by 1000.

## Relationship mapping

Map the existing UC 2.13 metering topology into the actual GREEN relationship structure.

Represent:

```text
upstream-meter
      |
    meters
      |
  +---+---+
  |       |
server-A server-B
```

Use only relationship identities/types actually defined by the module.

Keep both directions separate:

```text
YANG instance
    ↓ adapter/parser
internal topology
    ↓
accounting engine
```

and:

```text
internal topology
    ↓ adapter
YANG instance
```

Do not make the accounting engine read raw YANG structures directly.

## Event data stays outside standard YANG

The simulator events:

```text
TRAFFIC_HIGH
TRAFFIC_LOW
COMPONENT_SLEEP
TRAFFIC_BURST
```

are implementation-specific.

Do not invent GREEN YANG nodes for them.

Events may update YANG-compatible operational values, but the labels remain outside the standard/draft YANG tree.

## Sample instance files

Generate deterministic samples:

```text
examples/hardware-instance.json
examples/pdu-instance.json
```

Optionally add:

```text
examples/pdu-T0.json
examples/pdu-T1.json
examples/pdu-T2.json
examples/pdu-T3.json
```

only if simple.

## Instance validation

Validate representative instance data where practical.

Use `yanglint` if already available and easy to use, or another schema-aware validator already present.

Do not add a heavy stack just for this increment.

If only `pyang` is available, validate the modules with `pyang` and clearly state that full JSON/XML instance validation was not performed.

Do not claim `pyang` alone validates arbitrary JSON instance data if it does not.

## Tests

Add tests for:

1. **Mapping** — internal `EnergyObject` to YANG-compatible representation.
2. **Hardware correlation** — `source-component-id` references the RFC 8348 key required by the actual schema.
3. **Relationship mapping** — `upstream-meter meters server-A/server-B`.
4. **Round trip** — internal model -> YANG representation -> internal model preserves identifiers/topology where practical.
5. **Runtime compatibility** — existing UC 2.13 result remains:
   ```text
   naive = 600 Wh
   accounted = 300 Wh
   ```
6. **Event compatibility** — at least `TRAFFIC_LOW` can update YANG-compatible operational data without changing topology mapping.

## Mandatory separation

Keep:

```text
YANG / RFC 8348 data
        ↓
adapter
        ↓
internal EnergyObject + relationships
        ↓
accounting engine
```

The accounting engine MUST NOT depend on:

```text
JSON paths
XML paths
NETCONF
RESTCONF
pyang
```

## Runtime compatibility

Keep:

```powershell
python -m green
```

working.

Keep interactive controls `ENTER / a / r / q` working if already implemented.

Do not make runtime startup depend on invoking `pyang`.

YANG validation is a development/test operation, not a runtime dependency.

## Dependencies

Keep runtime dependencies minimal.

Prefer `pyang` as a development/test dependency rather than a mandatory runtime dependency.

## README

Add a concise YANG section covering:

- modules included;
- exact draft/RFC versions;
- `pyang` command;
- YANG search path;
- Python-to-YANG mapping;
- `energy_object_id` vs `hw:name` vs `hw:uuid`;
- relationship mapping;
- unit interpretation;
- known draft inconsistencies;
- what remains controller-specific;
- why NETCONF/RESTCONF are not included yet.

## Before implementation

Briefly report:

```text
YANG modules required
imports/dependencies required
files to create/modify
mapping to existing Python classes
validation commands planned
```

Then continue with implementation. Do not stop after the plan.

## After implementation

Run at minimum:

```powershell
pyang -p <yang-search-path> <GREEN-module>
pytest -v
python -m green --auto --interval 0
```

Report:

- YANG modules added;
- exact revisions;
- `pyang` command/result;
- instance validation command/result, if performed;
- tests run/results;
- runtime regression result;
- files created/modified;
- known draft inconsistencies.

## Acceptance criteria

This increment is complete only when:

- the real GREEN YANG module is present locally;
- required RFC 8348 YANG dependencies are present;
- `pyang` validation has been run and the real result is reported;
- the existing Python `EnergyObject` maps to real YANG nodes;
- `energy_object_id`, `hardware_component_name`, and `hardware_component_uuid` remain distinct;
- RFC 8348 hardware correlation is explicit;
- UC 2.13 metering relationships map to the actual GREEN relationship structure;
- deterministic sample instance data exists;
- the runtime still produces the existing accounting results;
- tests pass;
- no NETCONF/RESTCONF transport has been added;
- no standard/draft YANG node has been invented.

Stop after this minimal YANG adapter increment is complete.

Do not continue automatically to NETCONF, RESTCONF, YANG Push, sysrepo, Netopeer2, power-state control, or capability discovery.
