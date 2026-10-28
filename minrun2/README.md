# GREEN Minimal Runtime: UC 2.13 and UC 2.10

`minrun2` extends the interactive runtime with explicit topology-aware double
accounting (UC 2.13) and deterministic live-like traffic events (UC 2.10).
It stops before YANG, NETCONF, RESTCONF, or device-control integration.

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
install the project environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

The workspace selects `minrun2/.venv/Scripts/python.exe` on Windows. The
project uses the standard library and pytest; it has no YANG or network
management dependencies.

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

## Tests

Run tests without starting the interactive runtime:

```powershell
python -m pytest -v
```

Tests MUST NOT call `input()`, depend on `sleep()` or real-time delays, or hide
the simulator/accounting engine behind the CLI. They call the simulator and
accounting engine directly, using scripted input and a no-op sleeper only for
runtime-control tests.

## Project Files

- `src/green/models.py`: explicit identities, relationships, measurements, and results.
- `src/green/topology.py`: graph validation, traversal, and demo boundary.
- `src/green/simulator.py`: deterministic event and cumulative-counter state.
- `src/green/accounting.py`: compatibility checks and topology-aware accounting.
- `src/green/__main__.py`: interactive runtime and CLI.
- `tests/`: accounting, topology, simulator, and runtime behavior.
- `prompts/green_minimal_uc_2_13_uc_2_10_live.prompt.md`: implementation prompt.