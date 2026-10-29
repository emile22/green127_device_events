# GREEN Runtime with Read-Only NETCONF

`minrun4` reuses the UC 2.13/UC 2.10 runtime, Python models, accounting engine,
and YANG adapter from earlier increments. It adds UC 2.1 and UC 2.14 scenarios
and exposes read-only operational data through local Sysrepo and Netopeer2.
There is no RESTCONF, YANG Push, `<edit-config>`, or NETCONF-driven state change.

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

Python 3.11 is pinned in `pyproject.toml`. On Windows, create the Python venv
from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

The workspace selects `minrun4/.venv/Scripts/python.exe`. `ncclient` is used
only by NETCONF smoke tests; `pyang` validates schemas. Neither is required to
start the Python runtime.

Sysrepo, libyang, and Netopeer2 run natively in Ubuntu 22.04 WSL, not in a
container. Install the native packages inside WSL:

```bash
sudo apt update
sudo apt install -y sysrepo sysrepo-plugind netopeer2 libyang2-dev libyang2-tools build-essential pkg-config libssh-dev
```

From the `minrun4` directory in WSL, install the exact YANG revisions, build
the provider, and start the systemd services:

```bash
bash scripts/wsl-netconf-start.sh
bash scripts/wsl-netconf-status.sh
```

The installer stores a random local password in the ignored
`state/netconf/connection.env`, configures its hash in Sysrepo and a dedicated
non-interactive WSL account, and writes the current WSL IP into `NETCONF_HOST`.
The Python smoke-test fixture reads `NETCONF_HOST`, `NETCONF_PORT`,
`NETCONF_USERNAME`, and `NETCONF_PASSWORD` from that file when the process
environment does not already define them. Do not commit credentials.

## Interactive Runtime

Run the existing test-first launcher:

```powershell
python run.py
```

It prints verbose test names first and starts the runtime only if all tests
pass. The runtime runs UC 2.13, UC 2.10, UC 2.1, then UC 2.14 and preserves
the existing controls:

| Input | Behavior |
| --- | --- |
| ENTER | Run only the next event, then pause again. |
| `a` | Run all remaining events automatically. |
| `r` | Restart the complete demo at `U13-0`, resetting topology, component state, and cumulative counters. |
| `q` | Stop cleanly. |

Run without prompts using `python -m green --auto --interval 0`. Automatic mode
continues across all use-case series. The CLI interval controls local display
delays only; it is not the measurement interval.

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

For schema-aware instance validation, run `yanglint` inside WSL after the
runtime or smoke tests have written a combined snapshot:

```bash
yanglint -p yang \
    yang/iana-hardware@2018-03-13.yang \
    yang/ietf-hardware@2018-03-13.yang \
    yang/iana-power-and-energy@2026-07-02.yang \
    yang/ietf-power-and-energy@2026-07-02.yang \
    state/netconf/operational.json
```

The combined runtime snapshot has been validated with `yanglint`. The two
example JSON files are module fragments and are compared together with adapter
output by unit tests.

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
- YANG `int64`/`uint64` power and energy values are serialized as JSON strings,
    as required by RFC 7951.

`examples/hardware-instance.json` contains the RFC 8348 inventory. The
`examples/pdu-instance.json` file contains the corresponding GREEN Energy
Objects and metering relationships. Event labels, accounting boundaries,
naive/accounted totals, and exclusion explanations remain Python controller
metadata, not custom YANG leaves.

## NETCONF Data Flow

```text
Python runtime + existing YANG adapter
          ↓ local JSON snapshot
Sysrepo operational-data provider (native WSL process)
          ↓
Netopeer2 server on the WSL interface, TCP/830
          ↓ NETCONF <get> only
ncclient smoke tests
```

The runtime writes RFC 7951-shaped hardware and GREEN snapshots atomically.
The Sysrepo provider publishes those snapshots as operational data when
Netopeer2 requests `<get>`. Scenario progression remains in the Python runtime.
The NETCONF layer does not accept writes or drive scenario state.

The start script installs the exact YANG revisions and required crypt-hash
feature before starting Sysrepo and Netopeer2. Run the live read-only smoke
tests from Windows with:

```powershell
.\scripts\run-netconf-smoke.ps1
```

Stop the native services from WSL with `bash scripts/wsl-netconf-stop.sh`.
The operational provider and service scripts are local/native; they do not
use Docker. NETCONF tests issue `<get>` only and do not send configuration
changes.

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
existing UC 2.13 accounting result. `tests/netconf/` contains live ncclient
smoke tests for the connection, RFC 8348 inventory, UC 2.13 topology, UC 2.10
energy/state, UC 2.1 partial deployment, and UC 2.14 resilience data.

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
- `prompts/green4_minimal_netconf_4_UCs.prompt.md`: minrun4 implementation prompt.
- `prompts/green3_minimal_yang_adapter.prompt.md`: preceding YANG adapter prompt.