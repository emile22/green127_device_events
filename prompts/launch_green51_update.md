# Launch GREEN 5.1 update — `allrun51`

Use this file as the launch instruction for GitHub Copilot in the opened `green` repository.

## Task

Apply the requirements from:

```text
green51_netconf_all_UCs.prompt.md
```

to the **existing** implementation:

```text
allrun51/
```

Do **not** recreate `allrun51` from scratch if it already exists.

Do **not** create another run directory.

Treat:

```text
allrun5/
```

as a strict read-only historical baseline.

## Update mode

First inspect the current `allrun51/` implementation and compare it requirement-by-requirement with:

```text
green51_netconf_all_UCs.prompt.md
```

Then:

1. keep everything already correct;
2. modify only what is missing, incomplete, inconsistent, or failing;
3. do not duplicate existing files, fixtures, topology definitions, tests, or documentation;
4. preserve working behavior unless the prompt explicitly requires a change;
5. keep all implementation output under `allrun51/`.

The current implementation may already contain:

```text
canonical network
six topology subgraphs
UC overlays
122 events
controller reconstruction
capability-discovery readiness
NETCONF tests
README architecture documentation
Energy Object observability handling
```

Verify these from the actual repository state. Do not assume they are complete merely because they were previously reported as complete.

## Mandatory checks

Confirm that `allrun51` satisfies the current prompt, including:

```text
T1 CORE       Fixed Network
T2 AIR        WLAN / PoE
T3 POWER      Power Infrastructure
T4 BACKHAUL   Wireless Transport
T5 EDGE       Edge / Compute
T6 CITY       ISAC / Smart City
```

and that `allrun51/README.md` contains the simulator-internals view:

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

Also verify:

- one canonical stable demo network;
- reusable device archetypes and stable device instances;
- UC scenarios implemented as overlays/patches;
- 14 Group A UCs;
- at least 122 deterministic events;
- stable RFC 8348 component names and UUIDs;
- stable Energy Object IDs;
- valid `source-component-id` mappings;
- controller identity normalization using `(device-id, component-name)`;
- all four GREEN relationship families;
- relationship classification:
  - stable structural;
  - physical dynamic;
  - knowledge/observability;
- UC 2.13 distinguishes actual topology from controller knowledge;
- NETCONF remains read-only;
- controller reconstruction uses NETCONF-visible data as observed truth;
- no RFC 9196 or `ietf-power-state-capabilities` data is fabricated in `allrun51`.

## Energy Object checks

Inspect the current Energy Object population carefully.

Do not leave unexplained rows equivalent to:

```text
Power = -
State = -
Relationships = -
```

Every Energy Object must have an explicit observability class:

```text
FULL
POWER_ONLY
STATE_ONLY
TOPOLOGY_ONLY
UNOBSERVED
```

Use display semantics:

```text
UNKNOWN
  applicable but unavailable/not observed

N/A
  intentionally not applicable

0
  actual modeled/measured zero only
```

Do not write `UNKNOWN` or `N/A` into typed numeric or identityref YANG leaves.

Major Energy Objects in T1-T6 should expose meaningful Power and/or State values whenever supported by the use-case semantics.

Relationships should be populated where the canonical topology defines them.

Verify:

```text
allrun51/docs/energy_object_observability.md
```

and update it if needed.

## Discovery readiness

Verify:

```text
allrun51/docs/capability_discovery_readiness.md
```

against the actual canonical inventory.

Future capability-demo components should include real stable components from classes such as:

```text
router linecard
WLAN AP radio
WLAN AP baseband
transport radio/module
server NIC
ISAC radio or sensing component
```

Do not implement RFC 9196 capability values in this update.

## Controller readiness

Future controller and discovery work will use `allrun51` as the authoritative device-side baseline.

Therefore verify that an external controller can reconstruct, through NETCONF-visible YANG only:

```text
hardware inventory
Energy Object inventory
source-component-id mappings
Energy Object relationships
dynamic state
```

Do not use internal simulator fixtures as observed controller truth.

Expected fixtures may be used only for comparison.

## Validation

After applying only the required updates, run the complete validation.

From `allrun51`, run the appropriate equivalent of:

```powershell
pytest -v
pytest tests/netconf -v
python -m green --auto --interval 0
```

Also validate the WSL-native Sysrepo/Netopeer2 path and the live NETCONF retrieval used by the implementation.

From repository root verify:

```powershell
git diff -- allrun5
```

The expected result is no changes under `allrun5/`.

## Final report

Report the actual verified state, including:

```text
files changed in allrun51
files added in allrun51

device archetype count
device instance count
RFC 8348 component count
Energy Object count
Energy Object observability-class counts

T1-T6 topology status

Group A UC count
events per UC
total event count

relationship counts by family
relationship behavior-class counts

NETCONF reconstruction result
capability-discovery readiness result

pytest result
NETCONF test result
auto-run event result

git diff -- allrun5 result

remaining gaps or blockers
```

Do not claim success for commands or tests that were not actually run.

If the current `allrun51` already satisfies a requirement, keep it unchanged and report it as verified rather than recreating it.
