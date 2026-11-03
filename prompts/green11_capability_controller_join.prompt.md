# green11 — Build an external capability-aware GREEN controller

## Objective

Build a runnable external controller under:

```text
caprun11/
```

that reads, through NETCONF only:

```text
RFC 8348 hardware inventory
RFC 9196 system capabilities
draft-claise-green-capability-discovery-03 Power State capabilities
draft-ietf-green-power-and-energy-yang-04 live GREEN state
```

and correlates them into one per-Component view.

This is an implementation task, not an analysis-only task.

## Read-only baselines

Use as read-only:

```text
allrun5/
ctrlrun6/
ctrlrun7/
gaprun8/
caprun10/
```

Do not modify them.

## Critical architectural rule

`caprun11` is an external controller.

It MUST NOT obtain device truth by:

- importing Python objects from `allrun5/` or `caprun10/`;
- reading simulator internal event state;
- reading internal runtime JSON that is not itself a captured NETCONF response;
- calling simulator helper functions to obtain current values.

Device truth must come through NETCONF.

Fixtures may be used for unit tests, but the live controller path must use NETCONF.

## Mandatory package

Create runnable code, for example:

```text
caprun11/
  README.md
  green_capability_controller/
    __init__.py
    __main__.py
    netconf.py
    inventory.py
    capabilities.py
    energy.py
    join.py
    views.py
    ...
  tests/
  docs/
  snapshots/
```

Adapt to repo conventions where appropriate.

## NETCONF collection sequence

The controller must independently collect:

1. YANG Library/module support;
2. `/ietf-hardware:hardware`;
3. `/ietf-system-capabilities:system-capabilities`;
4. `/ietf-power-and-energy:energy-objects`.

Prefer RFC 8526 `<get-data>` from the operational datastore where supported.

Fall back to `<get>` where necessary.

Do not use `<get-config>` for the read-only capability data.

Preserve raw NETCONF XML responses in local snapshots.

## Correlation model

Build a normalized object with at least:

```text
hardware_component_name
hardware_component_uuid
energy_object_id
energy_source_component_id
capability_source
supported_power_states
current_oper_power_state
requested_admin_power_state_if_visible
instantaneous_power
nameplate_power
relationships
```

Keep every identifier separate.

Do not equate:

```text
Energy Object ID
hardware Component name
hardware UUID
relationship peer ID
```

## Join algorithm

The primary current-schema join is:

```text
RFC9196 node-selector
  -> RFC8348 component[name='X']

GREEN energy-object/source-component-id
  -> RFC8348 component[name='X']
```

Join through the RFC 8348 Component.

Do not join directly by Energy Object ID.

## RFC 9196 precedence

Implement and test the effective capability selection:

```text
specific per-Component capability
    overrides/fills the capability for that Component

otherwise system-wide default
    applies to that Component

otherwise
    UNKNOWN
```

Respect RFC 9196 precedence if multiple per-node selectors match.

Do not silently merge a system-wide default into an explicit per-Component capability contrary to RFC 9196/revision `-03`.

## Coverage states

For every RFC 8348 hardware Component classify:

```text
PER_COMPONENT
SYSTEM_DEFAULT
UNKNOWN
```

A Component with no applicable capability is UNKNOWN.

Never treat it as zero Power or "does not support sleep".

## Sleep-capable derivation

Derive `sleep-capable`.

A Component is sleep-capable if it advertises a supported Power State whose identity derives from:

```text
ietf-power-and-energy:power-state-sleep
```

Do not rely only on literal string equality with `power-state-sleep`.

Use schema-aware identity ancestry when practical.

Add tests with at least one derived low-power identity if the YANG corpus supports one.

## Static PSP

For every supported low-power state, derive static planning PSP only when both values exist:

```text
PSP =
  nominal-power(power-state-on)
  -
  nominal-power(low-power-state)
```

If either nominal value is missing:

```text
PSP = unknown
```

Do not substitute max Power.

Do not use measured instantaneous Power and still label the result as static PSP.

## Nameplate consistency

Where GREEN `nameplate-power` is available:

check:

```text
nominal-power(ON) <= nameplate-power
max-power(ON)     <= nameplate-power
```

Report violations as consistency warnings.

Do not mutate the data.

## Per-Component display

Provide a compact view like:

```text
COMPONENT CAPABILITY + LIVE STATE

Component: linecard-3
  Hardware UUID: ...
  Capability coverage: PER_COMPONENT
  Supported:
    ON     nominal=200W max=240W
    SLEEP  nominal=15W  max=25W exit-max=2000ms
  Static PSP(SLEEP): 185W
  Current oper state: ON
  Instantaneous Power: ...
  Energy Object: ...
```

## Diff and snapshots

Support:

```text
--once
--watch
--interval N
--json
--xml
--diff
```

where practical and consistent with existing controller tooling.

Capabilities should normally remain stable while live GREEN state can change between events.

Highlight that difference.

## Tests

Tests must verify:

- NETCONF-only live data path;
- raw XML preserved;
- hardware/capability/live-state join;
- per-Component precedence;
- system-wide fallback;
- unknown coverage;
- missing optional Power figures;
- identity-derived sleep capability;
- static PSP;
- nameplate consistency;
- identifiers not conflated;
- no previous run directory modified.

## Required execution

Provide documented commands such as:

```powershell
cd caprun11
python -m green_capability_controller --once
python -m green_capability_controller --watch --interval 1
python -m green_capability_controller --once --json
pytest -v
```

Use the actual working project command structure if different.

## Out of scope

Do not:

- write `power-state/admin`;
- execute `<edit-config>`;
- infer runtime eligibility from capability;
- infer dependent-idle state from absence of data;
- modify upstream YANG;
- add new GAP IDs;
- redesign the capability YANG.

## Final report

Report:

- exact files created;
- exact NETCONF calls/filters;
- capability coverage by Component;
- joined Component count;
- unmatched selectors;
- Energy Objects with no matched hardware Component;
- static PSP results;
- consistency warnings;
- tests and results.
