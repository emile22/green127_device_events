import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from green.catalog import USE_CASES_BY_SERIES
from green.models import SimulatedEvent
from green.topology import demo_energy_objects
from green.yang_adapter import to_yang_instance


def write_operational_snapshot(
    event: SimulatedEvent,
    destination: Path | None = None,
) -> Path:
    """Atomically publish schema-shaped data for the local Sysrepo provider."""
    if destination is None:
        configured_path = os.environ.get("GREEN_NETCONF_STATE_FILE")
        destination = (
            Path(configured_path)
            if configured_path
            else Path(__file__).resolve().parents[2]
            / "runtime"
            / "operational.json"
        )

    snapshot = to_yang_instance(
        demo_energy_objects(),
        event.relationships,
        event.measurements,
        event.component_states,
        event.power_measurements,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    trace_enabled_path = Path(f"{destination}.netconf-trace-enabled")
    try:
        trace_enabled = trace_enabled_path.read_text(encoding="ascii").strip() == "1"
    except FileNotFoundError:
        trace_enabled = False

    series = event.series.value
    title = USE_CASES_BY_SERIES[event.series].title
    if trace_enabled:
        context_path = Path(f"{destination}.netconf-context")
        context_path.write_text(
            f"{series} - {title} | {event.sequence} {event.name}\n",
            encoding="utf-8",
        )
    _write_text_atomically(destination, json.dumps(snapshot, indent=2) + "\n")
    if trace_enabled:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        trace_path = _trace_path(destination)
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with trace_path.open("a", encoding="utf-8", newline="\n") as trace_file:
            trace_file.write(
                "------------------------------------------------------------------------\n"
                f"{series} - {title} | {event.sequence} {event.name}\n"
                "------------------------------------------------------------------------\n"
                f"[{timestamp}] GREEN runtime snapshot published\n"
                "operation: runtime snapshot\n"
                "module: GREEN simulator\n"
                "path: /green/scenario/current\n"
                "request-xpath: (runtime event)\n"
                "status: published\n"
                "reply-data-json:\n"
                f"{json.dumps(snapshot, indent=2)}\n\n"
            )
    return destination


def set_netconf_trace_enabled(
    enabled: bool,
    destination: Path | None = None,
) -> Path:
    """Toggle provider tracing and return the path of its message log."""
    if destination is None:
        configured_path = os.environ.get("GREEN_NETCONF_STATE_FILE")
        destination = (
            Path(configured_path)
            if configured_path
            else Path(__file__).resolve().parents[2]
            / "runtime"
            / "operational.json"
        )

    control_path = Path(f"{destination}.netconf-trace-enabled")
    trace_path = _trace_path(destination)
    control_path.parent.mkdir(parents=True, exist_ok=True)
    _write_text_atomically(control_path, "1\n" if enabled else "0\n", encoding="ascii")
    return trace_path


def _write_text_atomically(
    destination: Path,
    contents: str,
    *,
    encoding: str = "utf-8",
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding=encoding, newline="\n") as output_file:
            output_file.write(contents)
            output_file.flush()
            os.fsync(output_file.fileno())
        for attempt in range(8):
            try:
                os.replace(temporary_path, destination)
                return
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(0.01 * (attempt + 1))
    finally:
        temporary_path.unlink(missing_ok=True)


def _trace_path(destination: Path) -> Path:
    configured_path = os.environ.get("GREEN_NETCONF_TRACE_FILE")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[2] / "logs" / "netconf-trace.log"