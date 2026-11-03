from __future__ import annotations

from typing import Any


def derived_value(
    *,
    name: str,
    value: Any,
    unit: str | None,
    inputs: list[dict[str, Any]],
    source_paths: list[str],
    relationship_edges: list[dict[str, Any]],
    transformation: str,
    status: str,
    event_id: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "value": value,
        "unit": unit,
        "inputs": inputs,
        "source_yang_paths": source_paths,
        "relationship_edges": relationship_edges,
        "transformation": transformation,
        "event_id": event_id,
        "status": status,
    }
