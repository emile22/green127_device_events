# green6 Observer Notes

The controller reads RFC 8348 hardware and GREEN Energy Object data using ncclient `<get>` only. It never imports allrun5 runtime code and never sends configuration or control RPCs.

On Windows, `py .\ctrlrun6\run.py` defaults to one live observation (`--once`); pass `--watch --interval 1` to poll repeatedly. The wrapper automatically relaunches through `ctrlrun6/.venv` when that environment exists, even if another venv is currently activated. Connection settings load from `install/runtime/netconf/connection.env` by default, then `allrun5/runtime/netconf/connection.env`; explicit `NETCONF_*` environment values override the file. Credentials are never printed or hard-coded.

Watch mode polls the current NETCONF snapshot; it does not replay the allrun5 event catalog or show its UC/event labels. It prints a full summary for its first poll, then only non-empty diffs. No output between polls means the observed Energy Object set has not changed. Press `q` at any time during watch mode to stop cleanly.

The local simulator event catalog contains 61 Group A events, but event IDs are not fields in the current YANG data. `--once` therefore issues one GET per catalog reference and explicitly records that event correlation is a controller-side reference. It does not claim that a reply contains an event ID. The current final-state snapshot may be identical across these GETs.

For each event the generated observation catalog lists YANG-visible fields observed in the reply, exact source-component-to-hardware correlations derived from those leaves, simulator-only metadata, and expected YANG fields unavailable in the current snapshot. `unavailable` is not a gap finding.

During `--once`, the CLI prints a flushed `[n/61] Collected UC/event` progress line after each successful NETCONF GET.

`instantaneous-power` is retained in declared mWatts. The module declares Watt-hours for total energy while its description refers to mWh; raw values are retained without rescaling.
