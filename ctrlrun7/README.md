# GREEN Controller Processing (green7)

This executable controller builds processing, aggregation, provenance, coverage, and deterministic recommendations on the read-only observer. `allrun5/` and `ctrlrun6/` are read-only inputs. Recommendations are never sent to devices.

## Setup

From `ctrlrun7/`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Connection settings load from `install/runtime/netconf/connection.env` by default, then `allrun5/runtime/netconf/connection.env`; explicit `NETCONF_*` environment values override the files. Credentials are never printed or hard-coded. `run.py` automatically re-launches through `ctrlrun7/.venv` when present. Run:

```powershell
py run.py
py run.py --once
py run.py --watch --interval 1
py run.py --once --show-processing
py run.py --help
python -m green_controller --once
python -m green_controller --watch --interval 1
python -m green_controller --once --show-processing
python -m green_controller --once --fixture ..\ctrlrun6\tests\fixtures\netconf_reply.xml
python -m green_controller --help
pytest -v
```

`--once` and `--watch` collect through NETCONF `<get>` only. The fixture option supports deterministic processing tests when Netopeer2 is unavailable. The controller writes `docs/representation_coverage.md`, `docs/requirement_to_yang_coverage.md`, and `docs/green8_input.json`. Coverage labels are observations, not gap declarations.

During `--watch`, press `q` to stop cleanly. The controller never sends recommendations or device-control operations.

With no mode argument, `run.py` and `python -m green_controller` default to `--once`. The introductory line explains that processing uses a current NETCONF snapshot and event identity may not be present in device YANG. Watch mode prints its initial view and then only non-empty changes.
