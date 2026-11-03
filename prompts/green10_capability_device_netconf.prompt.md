# green10 — Implement draft-claise-green-capability-discovery-03 on the device side

## Objective

Implement an executable, NETCONF-visible device-side realization of:

- `draft-claise-green-capability-discovery-03`
- RFC 9196 `ietf-system-capabilities`
- RFC 8348 hardware Component binding

under a new directory:

```text
caprun10/
```

This is an implementation task, not an analysis-only task.

## Read-only baselines

Inspect these existing directories first:

```text
allrun5/
ctrlrun6/
ctrlrun7/
gaprun8/
```

Treat all of them as read-only.

Do not modify previous run directories.

The actual working code and installed YANG schemas win over assumptions in this prompt.

## Normative/reference material

Use the exact semantics of:

- `draft-claise-green-capability-discovery-03`
- `draft-ietf-green-power-and-energy-yang-04`
- RFC 9196
- RFC 9195
- RFC 8348
- RFC 8342
- RFC 8525
- RFC 8526
- RFC 6241

Do not implement revision `-02` if `-03` is available.

## Mandatory implementation

Create runnable code under `caprun10/`.

At minimum provide:

```text
caprun10/
  README.md
  pyproject.toml or requirements files consistent with the repo
  green_capability_device/
    __init__.py
    __main__.py
    ...
  yang/
    upstream/
  data/
  tests/
  docs/
  wsl/
```

Adapt names only if the existing repo structure clearly requires it.

## YANG requirements

Install/use the exact upstream modules required by the capability draft.

Keep exact upstream copies under:

```text
caprun10/yang/upstream/
```

Do not patch upstream IETF YANG files.

The implementation must expose:

```text
ietf-system-capabilities:system-capabilities
```

augmented by:

```text
ietf-power-state-capabilities:power-state-capabilities
```

at both:

```text
/system-capabilities/power-state-capabilities
```

and, when used:

```text
/system-capabilities/datastore-capabilities/per-node-capabilities/
  power-state-capabilities
```

All capability data is read-only operational state.

Do not create writable capability nodes.

## RFC 8348 binding

Discover the actual hardware Component names used by `allrun5/`.

Do not invent a separate component identifier.

Per-Component capability entries must use RFC 9196 `node-selector` values targeting actual RFC 8348 Components, for example:

```text
/ietf-hardware:hardware/component[name='...']
```

The join key for the current schema is the RFC 8348 hardware Component `name`.

Important:

`draft-ietf-green-power-and-energy-yang-04` contains prose that discusses UUID use, but the actual YANG `source-component-id` leafref targets:

```text
/hw:hardware/hw:component/hw:name
```

Follow the actual schema.

Record the prose/schema mismatch in:

```text
caprun10/docs/schema_observations.md
```

Do not modify the schema to "fix" it.

## Capability scenarios

Provide deterministic capability data that demonstrates at least:

1. a Component with ON and SLEEP plus all Power and transition fields;
2. a Component with supported Power States but missing optional Power figures;
3. a Component with a per-Component override;
4. a Component covered only by a system-wide default;
5. a hardware Component with no applicable capability entry, therefore UNKNOWN;
6. at least one Component participating in an existing GREEN `enabling/enabled-by` relationship if the baseline inventory provides one.

Prefer existing Components from `allrun5/`.

Do not invent hardware Components when equivalent existing Components can be reused.

## Semantics

Preserve these distinctions:

```text
unsupported != unknown
unknown != zero
nominal-power != max-power
nominal-power != measured instantaneous-power
capability != operational state
capability != eligibility
```

A system-wide capability applies to a Component only when there is no applicable per-Component entry.

Do not merge system-wide and per-Component capabilities in a way that contradicts RFC 9196 precedence or revision `-03`.

## NETCONF runtime

Use the existing native WSL architecture:

```text
Windows Python/ncclient
        |
        v
Netopeer2
        |
        v
Sysrepo
```

No containers.

Provide scripts under `caprun10/wsl/` for any required module installation, verification, provider startup, and cleanup.

Do not hard-code a transient WSL IP.

Use localhost forwarding when available and the repo's existing fallback method otherwise.

## Operational data provider

Register the capability subtree as operational data in Sysrepo using the same implementation style that already works in the repo.

The provider must be executable and must stay alive when serving operational callbacks.

Do not merely generate JSON files and call the task complete.

## NETCONF verification

Implement a Windows-side or repo-consistent ncclient smoke test that:

1. connects to Netopeer2;
2. verifies relevant modules through YANG Library when available;
3. reads RFC 8348 hardware state;
4. reads the RFC 9196 capability subtree;
5. confirms the per-Component `node-selector` points to real hardware Components;
6. verifies the expected capability data is returned through NETCONF.

Prefer RFC 8526 `<get-data>` against `ietf-datastores:operational` when the server advertises support.

If `<get-data>` is not available, use NETCONF `<get>`.

Do not use `<get-config>` as the primary capability read, because capability nodes are `config false`.

## Human-readable output

Provide a view like:

```text
POWER STATE CAPABILITIES

Component     Coverage        State     Nominal   Max   Entry(max)   Exit(max)
linecard-3    per-component   ON        200 W     240 W
linecard-3    per-component   SLEEP      15 W      25 W   600 ms      2000 ms
...
```

Clearly label missing values as:

```text
unknown
```

not zero.

## Tests

Tests must cover at least:

- schema validation with `pyang`;
- instance validation with `yanglint` where applicable;
- per-Component selector resolution;
- system-wide fallback;
- per-Component override;
- unknown capability;
- optional missing Power values;
- transition-time values;
- no previous run directory modified;
- live NETCONF read when infrastructure is available.

If live Sysrepo/Netopeer2 is temporarily unavailable, still implement and run deterministic fixture-based tests.

Do not fall back to documentation-only output.

## Required commands

Provide a clean documented execution path, for example:

```powershell
cd caprun10
python -m green_capability_device --once
python -m green_capability_device --serve
pytest -v
```

If the existing repo architecture requires different exact commands, use the working architecture and document the exact commands.

## Out of scope

Do not:

- perform `<edit-config>`;
- change `power-state/admin`;
- add controller policy;
- implement TE/IGP advertisements;
- add YANG Push as a requirement;
- patch upstream YANG;
- call missing information zero.

## Final report

Report:

- exact files created;
- exact YANG modules/revisions used;
- exact commands run;
- tests and results;
- NETCONF RPC method used;
- Components covered per-Component;
- Components covered by system default;
- Components with unknown capability;
- schema/prose observations;
- remaining blockers.
