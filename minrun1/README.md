# GREEN Minimal Runtime

`minrun1` is a standalone, deterministic Python demo of a small GREEN energy
topology and event runtime. It intentionally does not implement full UC 2.13
accounting or network management protocols.

## Scope

- Simulates four PDU energy events and their raw measurements.
- Models an upstream meter connected to `server-A` and `server-B`.
- Displays raw readings, naive totals, boundary-meter totals, and topology
	completeness.
- Uses demo-only accounting: naive total sums every reading, while accounted
	total uses the upstream meter reading. This is not the full UC 2.13 logic.
- Has no NETCONF, REST API, database, Docker, YANG Push, or async runtime.

## Requirements

Python 3.10 or newer and pip. The project does not pin an interpreter version,
create a virtual environment, or add an editor interpreter-selection setting;
commands use the `python` executable selected in the current shell.

## Install

From the `minrun1` directory:

```powershell
python -m pip install -e ".[test]"
```

This installs the local package in editable mode and the pytest test extra.

## Run

Start the interactive console:

```powershell
python -m green
```

It pauses before each simulated event and displays these controls:

| Input | Behavior |
| --- | --- |
| ENTER | Run only the next event, then pause again. |
| `a` | Run all remaining events without prompting. |
| `q` | Stop cleanly. |
| `r` | Restart at T0 and return to interactive mode. |

Automatic mode waits one second between events by default. Start directly in
automatic mode with:

```powershell
python -m green --auto --interval 1
```

Use `--interval 0` to disable the delay. The only supported scenario is `pdu`.

## Demo Events

Each measurement is in Wh. The naive total sums all three readings; the
accounted total uses only the upstream boundary meter.

| Sequence | Event | Upstream | server-A | server-B | Naive | Accounted |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T0 | TRAFFIC_HIGH | 300 | 120 | 180 | 600 | 300 |
| T1 | TRAFFIC_LOW | 150 | 60 | 90 | 300 | 150 |
| T2 | COMPONENT_SLEEP server-B | 80 | 60 | 20 | 160 | 80 |
| T3 | TRAFFIC_BURST | 360 | 150 | 210 | 720 | 360 |

## Tests

Run the suite with verbose test names:

```powershell
python -m pytest -v
```

To run the tests and then launch the interactive runtime in the same console:

```powershell
python run.py
```

`run.py` uses the same interpreter for both steps and starts the runtime only
if every test passes. Runtime tests provide scripted input and a no-op sleeper,
so they never block for user input or wait for real-time delays.

The console shows the test names and results first, followed by the runtime
prompt:

```text
tests/test_accounting.py::test_demo_accounting_uses_upstream_boundary PASSED
tests/test_runtime.py::test_enter_runs_exactly_one_event_then_prompts_again PASSED
tests/test_runtime.py::test_a_runs_remaining_events_without_prompting_again PASSED
tests/test_runtime.py::test_q_stops_without_running_the_next_event PASSED
tests/test_runtime.py::test_r_restarts_at_t0_and_returns_to_interactive_mode PASSED
tests/test_runtime.py::test_auto_starts_without_reading_input PASSED
tests/test_simulator.py::test_pdu_scenario_emits_deterministic_measurements PASSED
tests/test_simulator.py::test_unknown_scenario_is_rejected PASSED
============================== 8 passed ==============================
All tests passed. Starting the GREEN runtime...
GREEN demo starting...
[ENTER] next event
a       automatically run all remaining events
q       quit
r       restart scenario
```

## Project Files

- `src/green/models.py`: event data model.
- `src/green/simulator.py`: deterministic event measurements; no accounting.
- `src/green/topology.py`: upstream meter and component graph.
- `src/green/accounting.py`: demo-only boundary-meter arithmetic.
- `src/green/__main__.py`: interactive and automatic console runtime.
- `tests/`: accounting, simulator, and runtime tests.
- `prompts/green_minimal_runtime_implementation.md`: implementation prompt used
	for this project.