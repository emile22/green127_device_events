# GREEN Controller Observer (green6)

This observer reads the allrun5 device simulator through NETCONF and does not import simulator internals or issue control operations. The renamed `allrun5/` tree is the read-only baseline.

## Setup

From `ctrlrun6/`, create a Python 3.11 environment and install the package/test dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

The observer loads connection settings from `install/runtime/netconf/connection.env` by default, then `allrun5/runtime/netconf/connection.env`. Explicit `NETCONF_HOST`, `NETCONF_PORT`, `NETCONF_USERNAME`, and `NETCONF_PASSWORD` environment variables override the local settings. Credentials are never printed or hard-coded. For a live one-shot catalog observation:

```powershell
python -m green_controller --once
python -m green_controller --watch --interval 1
python -m green_controller --help
pytest -v
```

`--once` opens one NETCONF session and issues one `<get>` for each of the 61 allrun5 catalog events. The YANG tree does not expose simulator event IDs, so each event association is explicitly a controller catalog reference, not a claim that the device reported that event. Raw XML and normalized JSON are stored under `logs/`; the generated catalog is under `docs/`.

The observer preserves reported relationship direction. Missing leaves remain absent and are never converted to zero. `instantaneous-power` is retained in the module's declared mWatts. The module declares Watt-hours for total energy while its description says mWh; this observer records the raw value and documents both statements without rescaling.
