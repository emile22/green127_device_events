# GREEN Minimal Runtime

A small, deterministic Python demo of GREEN energy measurements and topology.
It does not implement the full UC 2.13 accounting logic or any network
management protocol.

## Run

From this directory, install the package and test dependency:

```powershell
python -m pip install -e ".[test]"
python -m green
```

The default mode pauses before each event. Press ENTER to run one event, `a`
to run the remaining events automatically, `q` to quit, or `r` to restart at
T0. Automatic mode waits one second between events by default. To run without
input, use `python -m green --auto --interval 1`; use `--interval 0` to disable
the delay. The only supported scenario is `pdu`.

Run the unit tests with:

```powershell
pytest -v
```