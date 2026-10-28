# Minimal GREEN Runtime Implementation Guide

For a **minimal implementation including runtime**, keep the first runnable version extremely small:

```text
Python process
   |
   +-- event simulator
   |      TRAFFIC_HIGH
   |      TRAFFIC_LOW
   |      COMPONENT_SLEEP
   |      TRAFFIC_BURST
   |
   +-- raw measurements
   |
   +-- topology graph
   |
   +-- accounting engine
   |
   +-- console output
```

No NETCONF server, REST API, database, Docker, YANG Push, or async runtime yet.

## Minimal repository

```text
green/
├── pyproject.toml
├── README.md
├── src/
│   └── green/
│       ├── __init__.py
│       ├── models.py
│       ├── topology.py
│       ├── accounting.py
│       ├── simulator.py
│       └── __main__.py
└── tests/
    ├── test_accounting.py
  ├── test_simulator.py
  └── test_runtime.py
```

The important addition compared with the previous prompt is:

```text
__main__.py
```

That gives a real runtime entry point:

```powershell
python -m green
```

## Minimal runtime behavior

`__main__.py` creates the topology once:

```text
upstream-meter
      |
    meters
      |
  +---+---+
  |       |
server-A server-B
```

The runtime drives the four events in order, with interactive control by default:

```text
T0 TRAFFIC_HIGH
T1 TRAFFIC_LOW
T2 COMPONENT_SLEEP
T3 TRAFFIC_BURST
```

For each event:

```text
Event
  ↓
Simulator generates measurements
  ↓
AccountingEngine.compute(boundary, measurements, topology)
  ↓
Console displays result
```

Example output:

```text
GREEN demo starting...

[T0] TRAFFIC_HIGH

Raw:
  upstream-meter   300 Wh
  server-A         120 Wh
  server-B         180 Wh

Naive total:       600 Wh
Accounted total:   300 Wh
Topology:          complete

[T1] TRAFFIC_LOW

Raw:
  upstream-meter   150 Wh
  server-A          60 Wh
  server-B          90 Wh

Naive total:       300 Wh
Accounted total:   150 Wh

[T2] COMPONENT_SLEEP server-B

Raw:
  upstream-meter    80 Wh
  server-A           60 Wh
  server-B           20 Wh

Naive total:       160 Wh
Accounted total:    80 Wh

[T3] TRAFFIC_BURST

Raw:
  upstream-meter   360 Wh
  server-A         150 Wh
  server-B         210 Wh

Naive total:       720 Wh
Accounted total:   360 Wh

GREEN demo completed.
```

## Minimal Python environment

Use a virtual environment:

```powershell
cd green

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install pytest
```

Then make the project installable:

```powershell
pip install -e .
```

The runtime becomes:

```powershell
python -m green
```

and tests:

```powershell
pytest -v
```

## Minimal `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "green"
version = "0.1.0"
requires-python = ">=3.11"

[project.optional-dependencies]
test = ["pytest>=8"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

Then preferably install tests using:

```powershell
pip install -e ".[test]"
```

## What `simulator.py` should do

Keep it deliberately simple and deterministic.

Conceptually:

```python
EVENTS = [
    ("TRAFFIC_HIGH",      300, 120, 180),
    ("TRAFFIC_LOW",       150,  60,  90),
    ("COMPONENT_SLEEP",    80,  60,  20),
    ("TRAFFIC_BURST",     360, 150, 210),
]
```

It should **not calculate accounting**.

It only turns:

```text
TRAFFIC_LOW
```

into:

```text
upstream-meter = 150 Wh
server-A        = 60 Wh
server-B        = 90 Wh
```

That separation is important:

```text
simulator
    produces facts

accounting
    interprets facts
```

## Interactive console mode

**Default mode must pause before every simulated event.** Running
`python -m green` starts in interactive mode. At each pause, display:

```text
[ENTER] next event
a       automatically run all remaining events
q       quit
r       restart scenario
```

Handle commands as follows:

- An empty line (ENTER) executes exactly the next event, displays its result,
  then returns to the prompt.
- `a` runs all remaining events sequentially without prompting again. Apply the
  configured interval between events, but not before the first or after the
  last remaining event. The default automatic interval may be 1 second.
- `q` stops cleanly without executing another event.
- `r` resets the event index to T0 and returns to interactive mode.

After every executed event display its sequence and name, raw measurements,
naive total, accounted total, and topology status.

Support direct automatic execution without input:

```powershell
python -m green --auto --interval 1
```

This runs all events from T0 in automatic mode. Keep the CLI small; support
`--auto`, `--interval`, and `--scenario pdu`. Allow `--interval 0` to disable
automatic delays.

Keep the event runner independently testable by injecting its input and sleep
functions (or equivalent test seams). Unit tests must use scripted input and a
no-op sleep function; they must never wait for real user input or real-time
delays. Cover next-event stepping, automatic completion, clean quit, restart,
and automatic startup with no input.

## Acceptance criterion

The first runtime milestone must support both interactive and automatic runs:

```powershell
PS> python -m green
```

pauses before T0 and displays the four controls. Pressing ENTER executes only
T0 and returns to the prompt. The other controls follow the behavior above.

```powershell
PS> python -m green --auto --interval 1
```

runs all four events without input and produces:

```text
T0  naive=600  accounted=300
T1  naive=300  accounted=150
T2  naive=160  accounted=80
T3  naive=720  accounted=360
```

Unit tests exercise all console controls with scripted input and no-op sleeps;
they do not require a terminal or wait for real-time delays. Also:

```powershell
PS> pytest -v
```

returns all tests passing.

Only **after this works** add the next runtime layer:

```text
Python objects
     ↓
YANG adapter
     ↓
NETCONF/RESTCONF simulator
```

Do not introduce NETCONF into the first executable prototype.
