from __future__ import annotations

from pathlib import Path

from green.catalog import UC_CATALOG, relationships_for_profiles
from green.topology import demo_energy_objects


CAPABILITY_DEMO_SELECTIONS = (
    ("UC 2.9", "eo-ap-baseband", "Stable AP subsystem identity for future radio/baseband power-state capability examples."),
    ("UC 2.9", "eo-ap-radio-24", "Existing 2.4 GHz radio component exercises a low-power WLAN mode."),
    ("UC 2.9", "eo-ap-radio-5", "Existing 5 GHz radio component exercises per-radio mode capability."),
    ("UC 2.10", "eo-switch-fabric", "Existing switch fabric is the functional enabler for the line-card example."),
    ("UC 2.10", "eo-router-a-linecard-1", "Existing line card is the dependent component in the enabling relationship."),
    ("UC 2.16", "eo-transport-module", "Existing transport module participates in overlay/underlay coordination."),
    ("UC 2.16", "eo-dependent-ip-function", "Existing dependent IP function is the overlay-side functional peer."),
    ("UC 2.16", "eo-router-a", "Existing router is an additional hardware-backed peer of the transport module."),
)


def readiness_rows() -> list[dict[str, str]]:
    objects = {item.energy_object_id: item for item in demo_energy_objects()}
    use_cases = {item.series.value: item for item in UC_CATALOG}
    rows = []
    for uc, energy_object_id, reason in CAPABILITY_DEMO_SELECTIONS:
        energy_object = objects[energy_object_id]
        use_case = use_cases[uc]
        relationships = {}
        event_ids = []
        for event in use_case.events:
            event_relationships = relationships_for_profiles(event.relationship_profiles)
            selected_relationships = [
                relationship
                for relationship in event_relationships
                if energy_object_id in {
                    relationship.source_energy_object_id,
                    relationship.peer_energy_object_id,
                }
            ]
            if selected_relationships:
                event_ids.append(event.sequence)
            for relationship in selected_relationships:
                source = objects[relationship.source_energy_object_id]
                peer = objects[relationship.peer_energy_object_id]
                relationships[
                    f"{source.energy_object_id} ({source.hardware_component_name}) "
                    f"{relationship.relationship_type.value} -> "
                    f"{peer.energy_object_id} ({peer.hardware_component_name})"
                ] = None
        rows.append(
            {
                "uc": uc,
                "uc_title": use_case.title,
                "event_ids": ", ".join(event_ids),
                "hardware_component_name": energy_object.hardware_component_name or "",
                "hardware_component_uuid": energy_object.hardware_component_uuid or "",
                "energy_object_id": energy_object.energy_object_id,
                "source_component_id": energy_object.hardware_component_name or "",
                "relevant_relationships": "; ".join(sorted(relationships)) or "none in selected events",
                "reason": reason,
            }
        )
    return rows


def render_readiness_document() -> str:
    rows = readiness_rows()
    lines = [
        "# Capability-Discovery Readiness for Future caprun10+",
        "",
        "This is a stable-identity readiness inventory only. allrun5 does not implement RFC 9196, `ietf-system-capabilities`, `ietf-power-state-capabilities`, capability callbacks, or capability-gated control. UC2.11 classification remains simulator/controller metadata.",
        "",
        "The selected Energy Objects map to RFC 8348 Components by the existing `source-component-id` leafref. Component names and UUIDs are distinct and sourced from the allrun5 topology registry.",
        "",
        "| UC | UC title | Event IDs | hardware_component_name | hardware_component_uuid | energy_object_id | source_component_id | relevant_relationships | reason_selected_for_future_capability_demo |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {uc} | {title} | {events} | `{name}` | `{uuid}` | `{eo}` | `{source}` | {relationships} | {reason} |".format(
                uc=row["uc"],
                title=row["uc_title"].replace("|", "\\|"),
                events=row["event_ids"],
                name=row["hardware_component_name"],
                uuid=row["hardware_component_uuid"],
                eo=row["energy_object_id"],
                source=row["source_component_id"],
                relationships=row["relevant_relationships"].replace("|", "\\|"),
                reason=row["reason"],
            )
        )
    lines.extend(
        [
            "",
            "Future capability data belongs to separate caprun10+ work. This document does not imply that a selected component advertises any specific power-state capability today.",
            "",
        ]
    )
    return "\n".join(lines)


def write_readiness_document(destination: Path | None = None) -> Path:
    target = destination or Path(__file__).resolve().parents[2] / "docs" / "capability_discovery_readiness.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_readiness_document(), encoding="utf-8")
    return target
