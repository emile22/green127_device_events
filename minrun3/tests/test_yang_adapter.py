import json
from pathlib import Path

from green.accounting import AccountingEngine
from green.models import ComponentState
from green.simulator import EventSimulator
from green.topology import (
    build_demo_topology,
    demo_energy_objects,
    demo_metering_relationships,
)
from green.yang_adapter import from_yang_instance, to_yang_instance


def get_event(sequence: str):
    simulator = EventSimulator()
    while (event := simulator.next_event()) is not None:
        if event.sequence == sequence:
            return event
    raise AssertionError(f"missing simulator event: {sequence}")


def test_energy_objects_map_to_actual_green_and_rfc8348_nodes() -> None:
    objects = demo_energy_objects()
    relationships = demo_metering_relationships()
    event = get_event("U10-3")

    instance = to_yang_instance(
        objects,
        relationships,
        event.measurements,
        event.component_states,
    )

    hardware_components = instance["ietf-hardware:hardware"]["component"]
    assert {component["name"] for component in hardware_components} == {
        "upstream-meter",
        "server-A",
        "server-B",
    }
    assert all(component["class"] == "iana-hardware:energy-object" for component in hardware_components)

    yang_objects = instance["ietf-power-and-energy:energy-objects"]["energy-object"]
    by_id = {item["id"]: item for item in yang_objects}
    assert by_id["eo-upstream-meter"]["source-component-id"] == "upstream-meter"
    assert by_id["eo-upstream-meter"]["source-component-id"] != objects[0].hardware_component_uuid
    assert by_id["eo-upstream-meter"]["energy"]["total-energy-consumed"] == 890
    assert by_id["eo-server-a"]["energy"]["total-energy-consumed"] == 390
    assert by_id["eo-server-b"]["energy"]["total-energy-consumed"] == 500
    assert by_id["eo-server-b"]["power-state"]["oper"] == (
        "ietf-power-and-energy:power-state-on"
    )


def test_metering_relationship_maps_to_schema_identity_and_local_peer_ids() -> None:
    instance = to_yang_instance(demo_energy_objects(), demo_metering_relationships())
    yang_objects = instance["ietf-power-and-energy:energy-objects"]["energy-object"]
    upstream = next(item for item in yang_objects if item["id"] == "eo-upstream-meter")

    assert upstream["relationship"] == [
        {
            "type": "ietf-power-and-energy:metering",
            "peer": [
                {"id": "eo-server-a", "details": "explicit-demo-topology"},
                {"id": "eo-server-b", "details": "explicit-demo-topology"},
            ],
        }
    ]


def test_round_trip_preserves_python_ids_hardware_correlation_and_relationships() -> None:
    objects = demo_energy_objects()
    relationships = demo_metering_relationships()
    instance = to_yang_instance(objects, relationships)

    decoded_objects, decoded_relationships = from_yang_instance(
        instance,
        device_id="pdu-1",
    )

    assert decoded_objects == objects
    assert {
        (
            relationship.relationship_type,
            relationship.source_energy_object_id,
            relationship.peer_energy_object_id,
            relationship.provenance,
        )
        for relationship in decoded_relationships
    } == {
        (
            relationship.relationship_type,
            relationship.source_energy_object_id,
            relationship.peer_energy_object_id,
            relationship.provenance,
        )
        for relationship in relationships
    }


def test_traffic_low_maps_cumulative_energy_without_changing_topology() -> None:
    objects = demo_energy_objects()
    relationships = demo_metering_relationships()
    event = get_event("U10-1")

    instance = to_yang_instance(
        objects,
        relationships,
        event.measurements,
        event.component_states,
    )
    yang_objects = instance["ietf-power-and-energy:energy-objects"]["energy-object"]
    by_id = {item["id"]: item for item in yang_objects}

    assert by_id["eo-upstream-meter"]["energy"]["total-energy-consumed"] == 450
    assert by_id["eo-upstream-meter"]["relationship"][0]["peer"] == [
        {"id": "eo-server-a", "details": "explicit-demo-topology"},
        {"id": "eo-server-b", "details": "explicit-demo-topology"},
    ]
    assert by_id["eo-server-b"]["power-state"]["oper"] == (
        "ietf-power-and-energy:power-state-on"
    )


def test_yang_mapping_does_not_change_uc_2_13_accounting() -> None:
    event = get_event("U13-1")
    topology, boundary = build_demo_topology(relationships=event.metering_relationships)
    result = AccountingEngine().compute(
        boundary,
        event.measurements,
        topology,
        series=event.series.value,
        event_sequence=event.sequence,
        event_name=event.name,
    )

    to_yang_instance(demo_energy_objects(), event.metering_relationships, event.measurements)

    assert (result.naive_total_wh, result.accounted_total_wh) == (600, 300)


def test_representative_json_examples_match_adapter_output() -> None:
    examples = Path(__file__).parents[1] / "examples"
    hardware_data = json.loads((examples / "hardware-instance.json").read_text())
    energy_data = json.loads((examples / "pdu-instance.json").read_text())
    combined_data = {**hardware_data, **energy_data}

    event = get_event("U10-3")
    generated_data = to_yang_instance(
        demo_energy_objects(),
        demo_metering_relationships(),
        event.measurements,
        event.component_states,
    )

    assert combined_data == generated_data