import json
import os
from pathlib import Path

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
            / "state"
            / "netconf"
            / "operational.json"
        )

    snapshot = to_yang_instance(
        demo_energy_objects(),
        event.metering_relationships,
        event.measurements,
        event.component_states,
        event.power_measurements,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination.with_suffix(destination.suffix + ".tmp")
    temporary_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(destination)
    return destination