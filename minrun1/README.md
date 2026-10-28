# GREEN Minimal Runtime

Standalone implementation of the minimal GREEN runtime. It includes a
deterministic event simulator and demo-only boundary-meter arithmetic; it does
not implement full UC 2.13 accounting or network management protocols.

No Python interpreter version is pinned or selected by editor configuration.
The project accepts Python 3.10 or newer and uses the `python` command from the
current shell.

## Install and run

From this directory:

```powershell
python -m pip install -e ".[test]"
python -m green
```

The default mode pauses before each event. Press ENTER to run one event, `a`
to run the remaining events automatically, `q` to quit, or `r` to restart at
T0. Automatic mode waits one second between events by default. To run without
input, use `python -m green --auto --interval 1`; use `--interval 0` to disable
the delay.

Run the unit tests with:

```powershell
pytest -v
```

To show verbose test names and then start the interactive runtime in the same
console, run:

```powershell
python run.py
```

The runtime starts only if all tests pass, and the launcher uses the same
Python interpreter for both commands.