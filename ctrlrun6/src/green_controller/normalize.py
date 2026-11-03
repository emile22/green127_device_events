from __future__ import annotations

from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from typing import Any

from green_controller.models import FieldObservation, NetconfSnapshot

HARDWARE_NS = "urn:ietf:params:xml:ns:yang:ietf-hardware"
ENERGY_NS = "urn:ietf:params:xml:ns:yang:ietf-power-and-energy"

UNITS = {
    "instantaneous-power": "mWatts",
    "nameplate-power": "Watts",
    "total-energy-consumed": "Watt-hours (declared; description states mWh)",
    "total-energy-delivered": "Watt-hours (declared; description states mWh)",
}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(parent: ET.Element, name: str) -> ET.Element | None:
    return next((node for node in list(parent) if _local_name(node.tag) == name), None)


def _text(parent: ET.Element, name: str) -> str | None:
    node = _child(parent, name)
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value or None


def _value(raw: str, leaf: str) -> Any:
    if leaf in {"instantaneous-power", "nameplate-power", "total-energy-consumed", "total-energy-delivered", "parent-rel-pos"}:
        try:
            return int(raw)
        except ValueError:
            return raw
    return raw


def _append_leaves(
    element: ET.Element,
    *,
    module: str,
    path: str,
    device: str,
    retrieved_at: str,
    fields: list[FieldObservation],
) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for child in list(element):
        name = _local_name(child.tag)
        child_path = f"{path}/{name}"
        if list(child):
            normalized[name] = _append_leaves(
                child,
                module=module,
                path=child_path,
                device=device,
                retrieved_at=retrieved_at,
                fields=fields,
            )
        elif child.text is not None:
            raw = child.text.strip()
            if not raw:
                continue
            value = _value(raw, name)
            normalized[name] = value
            fields.append(
                FieldObservation(
                    device=device,
                    retrieved_at=retrieved_at,
                    module=module,
                    data_path=child_path,
                    raw_value=raw,
                    normalized_value=value,
                    classification="YANG-visible",
                    units=UNITS.get(name),
                )
            )
    return normalized


def parse_netconf_xml(raw_xml: str, *, device: str, retrieved_at: str | None = None) -> NetconfSnapshot:
    timestamp = retrieved_at or datetime.now(timezone.utc).isoformat()
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as error:
        raise ValueError(f"NETCONF reply is not valid XML: {error}") from error

    fields: list[FieldObservation] = []
    hardware_container = next(
        (node for node in root.iter() if node.tag == f"{{{HARDWARE_NS}}}hardware"), None
    )
    energy_container = next(
        (node for node in root.iter() if node.tag == f"{{{ENERGY_NS}}}energy-objects"), None
    )

    components: list[dict[str, Any]] = []
    if hardware_container is not None:
        component_list = _child(hardware_container, "component")
        # The YANG list may occur repeatedly as direct sibling elements.
        for component in [node for node in list(hardware_container) if _local_name(node.tag) == "component"]:
            name = _text(component, "name")
            if not name:
                continue
            component_path = f"/ietf-hardware:hardware/component[name='{name}']"
            components.append(
                _append_leaves(
                    component,
                    module="ietf-hardware",
                    path=component_path,
                    device=device,
                    retrieved_at=timestamp,
                    fields=fields,
                )
            )

    energy_objects: list[dict[str, Any]] = []
    relationships: list[dict[str, str]] = []
    if energy_container is not None:
        for energy_object in [node for node in list(energy_container) if _local_name(node.tag) == "energy-object"]:
            object_id = _text(energy_object, "id")
            if not object_id:
                continue
            object_path = f"/ietf-power-and-energy:energy-objects/energy-object[id='{object_id}']"
            normalized = _append_leaves(
                energy_object,
                module="ietf-power-and-energy",
                path=object_path,
                device=device,
                retrieved_at=timestamp,
                fields=fields,
            )
            normalized["device-id"] = device
            for relation in [node for node in list(energy_object) if _local_name(node.tag) == "relationship"]:
                relation_type = _text(relation, "type")
                peers_node = _child(relation, "peer")
                if not relation_type or peers_node is None:
                    continue
                for peer in [node for node in list(relation) if _local_name(node.tag) == "peer"]:
                    peer_id = _text(peer, "id")
                    if not peer_id:
                        continue
                    details = _text(peer, "details")
                    relationship = {
                        "source_energy_object_id": object_id,
                        "relationship_type": relation_type,
                        "peer_energy_object_id": peer_id,
                        "direction": "as-reported",
                    }
                    if details is not None:
                        relationship["details"] = details
                    relationships.append(relationship)
            energy_objects.append(normalized)

    component_by_name = {
        component["name"]: component
        for component in components
        if isinstance(component.get("name"), str)
    }
    object_by_id = {item["id"]: item for item in energy_objects if isinstance(item.get("id"), str)}
    for energy_object in energy_objects:
        source_name = energy_object.get("source-component-id")
        if isinstance(source_name, str) and source_name in component_by_name:
            component = component_by_name[source_name]
            energy_object["hardware-correlation"] = {
                key: component.get(key)
                for key in ("name", "uuid", "class", "parent", "parent-rel-pos")
                if key in component
            }

    normalized_data = {
        "device": device,
        "retrieved_at": timestamp,
        "ietf-hardware:hardware": {"component": components},
        "ietf-power-and-energy:energy-objects": {"energy-object": energy_objects},
        "relationships": relationships,
        "identifier_counts": {
            "device_ids": len({device}),
            "energy_object_ids": len(object_by_id),
            "hardware_component_names": len(component_by_name),
            "hardware_uuids": len({item.get("uuid") for item in components if item.get("uuid")}),
            "relationship_peers": len(relationships),
        },
    }
    return NetconfSnapshot(
        device=device,
        retrieved_at=timestamp,
        raw_xml=raw_xml,
        normalized=normalized_data,
        fields=tuple(fields),
    )
