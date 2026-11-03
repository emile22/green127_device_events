# GREEN YANG Gap Analysis Tool

This tool analyzes the read-only green7 handoff and actual repository YANG schemas. It assigns GAP IDs and adds experimental YANG only when a candidate meets the evidence rule. Upstream modules are copied byte-for-byte into `yang/upstream/`; no upstream schema is edited.

## Run

From `gaprun8/` in Python 3.11:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
py run.py
py run.py analyze
py run.py validate
py run.py report
py run.py --help
python -m green_gap_tool analyze
python -m green_gap_tool validate
python -m green_gap_tool report
python -m green_gap_tool --help
pytest -v
```

With no subcommand, `py run.py` defaults to `analyze`. `analyze` requires `../ctrlrun7/docs/green8_input.json`. `validate` runs pyang and uses WSL yanglint for the representative JSON instance when available. Runtime NETCONF validation is separate; the tool never sends device configuration.

This CLI runs one selected subcommand and exits; it has no interactive watch loop, so `q` is not applicable.
