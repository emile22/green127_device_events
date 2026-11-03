from __future__ import annotations

from collections import defaultdict, deque
from decimal import Decimal
from typing import Any


class IncompatibleMeasurements(ValueError):
    pass


def numeric_aggregate(values: list[dict[str, Any]], *, value_key: str = "value") -> dict[str, Any]:
    if not values:
        return {"status": "incomplete", "count": 0, "sum": None, "average": None, "minimum": None, "peak": None, "unit": None}
    units = {item.get("unit") for item in values}
    intervals = {item.get("interval") for item in values}
    if len(units) != 1:
        raise IncompatibleMeasurements(f"cannot aggregate units: {sorted(map(str, units))}")
    if len(intervals) > 1:
        raise IncompatibleMeasurements("cannot aggregate different measurement intervals")
    numbers = [Decimal(str(item[value_key])) for item in values]
    return {
        "status": "derived",
        "count": len(numbers),
        "sum": str(sum(numbers)),
        "average": str(sum(numbers) / Decimal(len(numbers))),
        "minimum": str(min(numbers)),
        "peak": str(max(numbers)),
        "unit": next(iter(units)),
        "interval": next(iter(intervals)),
    }


def directed_metering_edges(relationships: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = []
    for item in relationships:
        kind = str(item.get("relationship_type", "")).rsplit(":", 1)[-1]
        source = str(item.get("source_energy_object_id", ""))
        peer = str(item.get("peer_energy_object_id", ""))
        if kind == "metering":
            edges.append({"source": source, "target": peer, "as_reported": kind})
        elif kind == "metered-by":
            edges.append({"source": peer, "target": source, "as_reported": kind})
    return edges


def metering_reachable(root: str, edges: list[dict[str, str]]) -> dict[str, list[str]]:
    graph: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in edges:
        graph[edge["source"]].append(edge)
    paths: dict[str, list[str]] = {}
    pending = deque([(root, [])])
    visited = {root}
    while pending:
        current, path = pending.popleft()
        for edge in graph[current]:
            target = edge["target"]
            if target in visited:
                continue
            next_path = path + [f"{edge['source']} {edge['as_reported']} {target}"]
            paths[target] = next_path
            visited.add(target)
            pending.append((target, next_path))
    return paths
