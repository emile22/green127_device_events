# GREEN Runtime with Minimal YANG Adapter

`minrun3` reuses the UC 2.13/UC 2.10 runtime from `minrun2` and adds a local
adapter between its Python models and the actual GREEN/RFC 8348 YANG schemas.
It stops before NETCONF, RESTCONF, YANG Push, or device-control integration.

## Relationship to minrun4

`minrun4` builds on this runtime and adapter. It retains UC 2.13 and UC 2.10,
adds UC 2.1 and UC 2.14 for 17 events total, and adds a native, read-only
Sysrepo/Netopeer2 NETCONF layer with ncclient smoke tests. Those additions are
in the separate `minrun4/` project; `minrun3` itself remains NETCONF-free.

## Runtime Flow

```text
__main__.py
    |
    +-- interactive runtime / CLI only
    |
    +--> simulator.py
           |
           +--> measurements
                    |
                    +--> accounting.py
```

The simulator creates event state and immutable measurements. The accounting
engine independently evaluates those measurements against an explicit
metering graph and `rack-1` boundary. The CLI only coordinates and displays
results.

## Requirements and Setup

Python 3.11 is pinned in `pyproject.toml`. From this directory, create and
install the project and validation environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

The workspace selects `minrun3/.venv/Scripts/python.exe` on Windows. The
runtime adapter uses the standard library. `pyang` is a development/test
dependency and is not required to start the runtime.

## Interactive Runtime

Run the existing test-first launcher:

```powershell
python run.py
```

It prints verbose test names first and starts the runtime only if all tests
pass. The runtime pauses before each event and runs UC 2.13 first, followed by
UC 2.10. It preserves the existing controls:

| Input | Behavior |
| --- | --- |
| ENTER | Run only the next event, then pause again. |
| `a` | Run all remaining events automatically. |
| `r` | Restart the complete demo at `U13-0`, resetting topology, component state, and cumulative counters. |
| `q` | Stop cleanly. |

Run without prompts using `python -m green --auto --interval 1`. Automatic mode
continues across the UC 2.13/UC 2.10 series boundary. The CLI interval controls
real-time pauses between displayed events only; it is not the measurement
interval. Each simulated measurement represents a distinct one-hour interval.
Use `--interval 0` to disable runtime delays.

## Accounting Model

Device IDs, Energy Object IDs, hardware component names, and component UUIDs
are separate fields. Relationships have explicit types and provenance; only
`metering` and `metered-by` relationships participate in de-duplication.
`aggregating`, `aggregated-by`, `powering`, and `powered-by` remain distinct
model values and do not imply metering.

`rack-1` explicitly scopes `eo-upstream-meter`, `eo-server-a`, and
`eo-server-b`. When the graph is complete, the upstream meter is authoritative
for the boundary total. Server readings remain visible as raw observations and
are excluded with an explanation citing their explicit metering paths. With
missing paths, the naive total remains available, but `accounted_total_wh` is
`None` and topology is incomplete. Cycles or unknown graph peers produce an
invalid-topology result, not a guessed total.

Raw values are immutable and use Wh. `interval_energy_wh` is the consumed
energy for one event interval; `cumulative_energy_wh` is a separate running
counter. Accounting uses interval values only.

| Series / ID | Event | Meter interval | A interval | B interval | Naive | Accounted | Topology | Meter cumulative |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| UC 2.13 / U13-0 | RAW_MEASUREMENTS | 300 | 120 | 180 | 600 | unavailable | incomplete | — |
| UC 2.13 / U13-1 | TOPOLOGY_DISCOVERED | 300 | 120 | 180 | 600 | 300 | complete | — |
| UC 2.13 / U13-2 | NEXT_MEASUREMENT_INTERVAL | 340 | 140 | 190 | 670 | 340 | complete | — |
| UC 2.13 / U13-3 | TOPOLOGY_INCOMPLETE | 310 | 125 | 175 | 610 | unavailable | incomplete | — |
| UC 2.10 / U10-0 | TRAFFIC_HIGH | 300 | 120 | 180 | 600 | 300 | complete | 300 |
| UC 2.10 / U10-1 | TRAFFIC_LOW | 150 | 60 | 90 | 300 | 150 | complete | 450 |
| UC 2.10 / U10-2 | COMPONENT_SLEEP | 80 | 60 | 20 | 160 | 80 | complete | 530 |
| UC 2.10 / U10-3 | TRAFFIC_BURST | 360 | 150 | 210 | 720 | 360 | complete | 890 |

For U13-2, the downstream total is 330 Wh, not 340 Wh; the explicit metering
topology still selects the upstream boundary value of 340 Wh. UC 2.10 cumulative
counters are separate from interval readings. `server-B` transitions from
`active` to `low-power` at U10-2 and back to `active` at U10-3. No real network
packets or GREEN power-state controls are used.

## YANG Modules and Validation

The unchanged source modules are vendored under `yang/`:

- `ietf-power-and-energy@2026-07-02.yang`: `ietf-power-and-energy` code block from [draft -04](https://www.ietf.org/archive/id/draft-ietf-green-power-and-energy-yang-04.xml).
- `iana-power-and-energy@2026-07-02.yang`: `iana-power-and-energy` code block from [draft -04](https://www.ietf.org/archive/id/draft-ietf-green-power-and-energy-yang-04.xml).
- `ietf-hardware@2018-03-13.yang`: [RFC 8348 source](https://raw.githubusercontent.com/YangModels/yang/master/standard/ietf/RFC/ietf-hardware@2018-03-13.yang).
- `iana-hardware@2018-03-13.yang`: [RFC 8348 source](https://raw.githubusercontent.com/YangModels/yang/master/standard/ietf/RFC/iana-hardware@2018-03-13.yang).
- `ietf-inet-types@2013-07-15.yang`: [RFC 6991 source](https://raw.githubusercontent.com/YangModels/yang/master/standard/ietf/RFC/ietf-inet-types@2013-07-15.yang).
- `ietf-yang-types@2013-07-15.yang`: [RFC 6991 source](https://raw.githubusercontent.com/YangModels/yang/master/standard/ietf/RFC/ietf-yang-types@2013-07-15.yang).

Validate the GREEN schema and render its tree:

```powershell
pyang -p yang yang\ietf-power-and-energy@2026-07-02.yang
pyang -p yang -f tree yang\ietf-power-and-energy@2026-07-02.yang
```

`pyang` validates YANG modules, not arbitrary JSON instance data. The example
JSON is checked against adapter mapping tests; full instance validation is not
claimed unless a schema-aware data validator is available.

## Python/YANG Mapping

`src/green/yang_adapter.py` keeps internal Python models as the accounting
source of truth and maps them to/from RFC 7951-shaped dictionaries:

- `energy_object_id` maps to the GREEN `energy-object/id`.
- `hardware_component_name` maps to `source-component-id`; the actual leafref targets `/hw:hardware/hw:component/hw:name`.
- `hardware_component_uuid` remains correlated to RFC 8348 `uuid`; it is not
    substituted into the `source-component-id` leafref.
- UC 2.13 metering relationships map to the module's actual `metering`
    identity and peer list. Peer IDs use the internal Energy Object IDs as
    locally unique values, with details preserving context.
- Energy values map to `energy/total-energy-consumed` only when a cumulative
    counter exists. Internal Wh values are emitted without scaling, following
    the YANG `units "Watt-hours"` statement. The draft's prose says mWh; this
    schema/prose discrepancy is documented and no silent factor-of-1000
    conversion is applied.

`examples/hardware-instance.json` contains the RFC 8348 inventory. The
`examples/pdu-instance.json` file contains the corresponding GREEN Energy
Objects and metering relationships. Event labels, accounting boundaries,
naive/accounted totals, and exclusion explanations remain Python controller
metadata, not custom YANG leaves.

## Tests

Run tests without starting the interactive runtime:

```powershell
python -m pytest -v
```

Tests MUST NOT call `input()`, depend on `sleep()` or real-time delays, or hide
the simulator/accounting engine behind the CLI. They call the simulator and
accounting engine directly, using scripted input and a no-op sleeper only for
runtime-control tests. Adapter tests cover Python-to-YANG mapping, RFC 8348
hardware correlation, relationship mapping, round-trip conversion, and the
existing UC 2.13 accounting result.

## Project Files

- `src/green/models.py`: explicit identities, relationships, measurements, and results.
- `src/green/topology.py`: graph validation, traversal, and demo boundary.
- `src/green/simulator.py`: deterministic event and cumulative-counter state.
- `src/green/accounting.py`: compatibility checks and topology-aware accounting.
- `src/green/yang_adapter.py`: isolated Python/YANG and hardware mapping.
- `src/green/__main__.py`: interactive runtime and CLI.
- `yang/`: original GREEN, RFC 8348, and RFC 6991 modules.
- `examples/`: representative RFC 7951-shaped hardware and PDU data.
- `tests/`: accounting, topology, simulator, and runtime behavior.
- `prompts/green3_minimal_yang_adapter.prompt.md`: implementation prompt.