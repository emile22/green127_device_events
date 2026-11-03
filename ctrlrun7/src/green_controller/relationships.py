from __future__ import annotations

from collections import defaultdict
from typing import Any

RELATIONSHIP_FAMILIES = {
    "metering": "metered-by",
    "metered-by": "metering",
    "aggregating": "aggregated-by",
    "aggregated-by": "aggregating",
    "powering": "powered-by",
    "powered-by": "powering",
    "enabling": "enabled-by",
    "enabled-by": "enabling",
}


def directional_graph(relationships: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    graph: dict[str, list[dict[str, str]]] = defaultdict(list)
    for relationship in relationships:
        kind = str(relationship["relationship_type"])
        graph[str(relationship["source_energy_object_id"])].append(
            {
                "type": kind,
                "peer": str(relationship["peer_energy_object_id"]),
                "direction": "as-reported",
            }
        )
    return {source: sorted(edges, key=lambda edge: (edge["type"], edge["peer"])) for source, edges in graph.items()}
