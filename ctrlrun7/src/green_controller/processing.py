from __future__ import annotations

from decimal import Decimal
from typing import Any

from green_controller.aggregation import directed_metering_edges, metering_reachable, numeric_aggregate
from green_controller.coverage import write_coverage_artifacts
from green_controller.decisions import recommendations_for_all_use_cases
from green_controller.provenance import derived_value


def filter_energy_objects(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    objects = snapshot.get("ietf-power-and-energy:energy-objects", {}).get("energy-object", [])
    return [item for item in objects if isinstance(item, dict) and isinstance(item.get("id"), str)]


def process_snapshot(snapshot: dict[str, Any], project_root) -> dict[str, Any]:
    objects = filter_energy_objects(snapshot)
    relationships = snapshot.get("relationships", [])
    fields = snapshot.get("field_observations", [])
    # Snapshots store field observations separately only when exported by the collector;
    # reconstruct source paths for raw normalized leaves when processing a saved snapshot.
    power_inputs = []
    energy_inputs = []
    source_paths: list[str] = []
    object_by_id = {item["id"]: item for item in objects}
    for item in objects:
        power = item.get("power", {}).get("instantaneous-power")
        if isinstance(power, (int, float, str)):
            raw_path = f"/ietf-power-and-energy:energy-objects/energy-object[id='{item['id']}']/power/instantaneous-power"
            source_paths.append(raw_path)
            power_inputs.append({"object_id": item["id"], "raw_value": str(power), "unit": "mWatts", "interval": None, "source_path": raw_path})
        energy = item.get("energy", {}).get("total-energy-consumed")
        if isinstance(energy, (int, float, str)):
            raw_path = f"/ietf-power-and-energy:energy-objects/energy-object[id='{item['id']}']/energy/total-energy-consumed"
            source_paths.append(raw_path)
            energy_inputs.append({"object_id": item["id"], "raw_value": str(energy), "unit": "Watt-hours", "interval": None, "source_path": raw_path})

    raw_power_aggregate = numeric_aggregate(
        [{"value": input_item["raw_value"], "unit": input_item["unit"], "interval": input_item["interval"]} for input_item in power_inputs]
    )
    power_display = None
    if raw_power_aggregate["status"] == "derived":
        power_display = {
            "count": raw_power_aggregate["count"],
            "sum_watts": str(Decimal(raw_power_aggregate["sum"]) / Decimal(1000)),
            "average_watts": str(Decimal(raw_power_aggregate["average"]) / Decimal(1000)),
            "minimum_milliwatts": raw_power_aggregate["minimum"],
            "peak_milliwatts": raw_power_aggregate["peak"],
            "status": "derived-dashboard-statistic; not accounting-authoritative",
            "unit_note": "per-object values are YANG-declared mWatts; overlaps are not inferred",
        }

    # total-energy-consumed has no interval or reset timestamp in the current
    # snapshot, so these cumulative values are preserved but never summed.
    energy_summary = {
        "status": "incomplete" if energy_inputs else "unavailable",
        "cumulative_values": energy_inputs,
        "accounted_total": None,
        "reason": "YANG snapshot does not provide compatible interval boundaries/reset semantics",
    }

    metering_edges = directed_metering_edges(relationships)
    metering_paths = {
        root: metering_reachable(root, metering_edges)
        for root in sorted({edge["source"] for edge in metering_edges})
    }
    by_type: dict[str, int] = {}
    for relationship in relationships:
        kind = str(relationship.get("relationship_type", "unknown")).rsplit(":", 1)[-1]
        by_type[kind] = by_type.get(kind, 0) + 1

    provenance = []
    if power_display is not None:
        provenance.append(
            derived_value(
                name="observed-power-dashboard-statistics",
                value=power_display,
                unit="Watts and mWatts",
                inputs=power_inputs,
                source_paths=[item["source_path"] for item in power_inputs],
                relationship_edges=metering_edges,
                transformation="mWatts / 1000 for display; aggregate values remain non-authoritative",
                status="derived",
                event_id=None,
            )
        )
    provenance.append(
        derived_value(
            name="interval-energy-accounting",
            value=None,
            unit="Watt-hours",
            inputs=energy_inputs,
            source_paths=[item["source_path"] for item in energy_inputs],
            relationship_edges=metering_edges,
            transformation="no aggregation: interval/reset semantics unavailable in the snapshot",
            status=energy_summary["status"],
            event_id=None,
        )
    )

    candidates = write_coverage_artifacts(project_root)
    coverage_summary = {
        "requirements": len(candidates),
        "by_status": {
            status: sum(item["coverage"] == status for item in candidates)
            for status in ("complete", "partial", "absent", "ambiguous")
        },
    }
    return {
        "collected_observations": {
            "device": snapshot.get("device"),
            "retrieved_at": snapshot.get("retrieved_at"),
            "hardware_components": len(snapshot.get("ietf-hardware:hardware", {}).get("component", [])),
            "energy_objects": len(objects),
            "relationship_count": len(relationships),
        },
        "filtered_energy_objects": objects,
        "relationship_context": {
            "relationships_by_type": by_type,
            "directional_edges": relationships,
            "metering_paths": metering_paths,
        },
        "derived_values": {"instantaneous_power": power_display, "interval_energy": energy_summary},
        "provenance": provenance,
        "recommendations": recommendations_for_all_use_cases(),
        "coverage": coverage_summary,
        "controller_network_view": {
            "device": snapshot.get("device"),
            "energy_objects": objects,
            "relationships": relationships,
            "event_identity": "unavailable in current YANG snapshot",
        },
    }
