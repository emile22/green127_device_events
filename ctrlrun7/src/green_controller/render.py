from __future__ import annotations

import json
from typing import Any


def render(snapshot: dict[str, Any], view: str, diff: dict[str, Any] | None = None) -> str:
    if view == "raw-json":
        return json.dumps(snapshot, indent=2, ensure_ascii=False)
    if view == "raw-xml":
        return str(snapshot.get("raw_xml", ""))
    if view == "diff":
        return json.dumps(diff or {"added": [], "removed": [], "changed": []}, indent=2)

    hardware = snapshot.get("ietf-hardware:hardware", {}).get("component", [])
    energy = snapshot.get("ietf-power-and-energy:energy-objects", {}).get("energy-object", [])
    relationships = snapshot.get("relationships", [])
    lines = [
        f"Device: {snapshot.get('device', 'unknown')}",
        f"Retrieved: {snapshot.get('retrieved_at', 'unknown')}",
        f"Hardware components: {len(hardware)}",
        f"Energy Objects: {len(energy)}",
        f"Directional relationships: {len(relationships)}",
    ]
    if view in {"summary", "inventory"}:
        lines.extend(["", "HARDWARE INVENTORY"])
        for item in hardware:
            if view == "inventory":
                lines.append(json.dumps(item, ensure_ascii=False))
            else:
                parent = f" parent={item['parent']}" if item.get("parent") else ""
                lines.append(f"- {item.get('name', 'unknown')}{parent} class={item.get('class', 'unknown')}")
    if view in {"summary", "energy-objects"}:
        lines.extend(["", "ENERGY OBJECTS"])
        for item in energy:
            if view == "energy-objects":
                lines.append(json.dumps(item, ensure_ascii=False))
            else:
                correlation = item.get("source-component-id", "unmapped")
                measurements = []
                for container_name, leaves in (("power", ("instantaneous-power",)), ("energy", ("total-energy-consumed",))):
                    values = item.get(container_name, {})
                    for leaf in leaves:
                        if leaf in values:
                            measurements.append(f"{leaf}={values[leaf]}")
                lines.append(f"- {item.get('id', 'unknown')} component={correlation} {' '.join(measurements)}".rstrip())
    if view in {"summary", "relationships"}:
        lines.extend(["", "DIRECTIONAL RELATIONSHIPS"])
        for edge in relationships:
            lines.append(
                f"- {edge['source_energy_object_id']} {edge['relationship_type']} -> {edge['peer_energy_object_id']}"
            )
        if not relationships:
            lines.append("(none reported)")
    if view == "summary" and diff is not None:
        lines.extend(["", "DIFF", json.dumps(diff, ensure_ascii=False)])
    return "\n".join(lines)
