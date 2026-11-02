import json

from green.netconf_trace import _energy_object_inventory, format_netconf_trace_entry
from green.models import EventSeries
from green.netconf_trace import format_netconf_trace_entry
from green.simulator import EventSimulator, generate_events
from green.topology import demo_energy_objects
from green.views import (
    event_to_yang,
    filter_yang_instance_to_energy_objects,
    render_compact_event,
    render_json,
    render_relationship_diff,
    render_relationships,
    render_summary,
)


def events_by_sequence():
    return {event.sequence: event for event in generate_events()}


def test_summary_separates_hardware_energy_relationships_and_uc_interpretation():
    event = events_by_sequence()["U9-0"]
    data = event_to_yang(event, demo_energy_objects())
    summary = render_summary(event, data)
    sections = (
        "1. HARDWARE INVENTORY",
        "2. ENERGY OBJECTS",
        "3. ENERGY RELATIONSHIPS",
        "4. UC-SPECIFIC INTERPRETATION",
    )
    assert all(section in summary for section in sections)
    assert [summary.index(section) for section in sections] == sorted(
        summary.index(section) for section in sections
    )


def test_relationship_view_preserves_direction_and_raw_identity_values():
    event = events_by_sequence()["U9-0"]
    data = event_to_yang(event, demo_energy_objects())
    view = render_relationships(data)
    raw = json.dumps(data)

    assert "METERING" in view and "METERED-BY" in view
    assert "POWERING" in view and "POWERED-BY" in view
    assert "ENABLING" in view and "ENABLED-BY" in view
    assert "ietf-power-and-energy:metering" in raw
    assert "ietf-power-and-energy:metered-by" in raw
    assert "source-component-id" in raw
    assert json.loads(render_json(data)) == data


def test_relationship_diff_reports_added_and_removed_directions():
    events = events_by_sequence()
    added = render_relationship_diff(events["U13-0"], events["U13-1"])
    removed = render_relationship_diff(events["U13-2"], events["U13-3"])

    assert "Added relationships:" in added
    assert "eo-upstream-meter METERING -> eo-server-a" in added
    assert "eo-server-a METERED-BY -> eo-upstream-meter" in added
    assert "Removed relationships:" in removed
    assert "eo-upstream-meter METERING -> eo-server-b" in removed
    assert "eo-server-b METERED-BY -> eo-upstream-meter" in removed


def test_compact_event_view_has_short_directional_sections():
    events = events_by_sequence()
    event = events["U9-0"]
    summary = render_compact_event(event, demo_energy_objects(), events["U8-3"])

    assert "[UC 2.9 / U9-0] AP_ACTIVE" in summary
    assert "HW     " in summary
    assert "ENERGY " in summary and "eo-ap-1[ap-1]=18000W/active" in summary
    assert "REL    " in summary and "METERING" in summary and "ENABLING" in summary
    assert "DIFF   " in summary

    final = events["U16-9"]
    compact_hardware = render_compact_event(final, demo_energy_objects(), events["U16-8"]).splitlines()[2]
    assert "transport-module=active" in compact_hardware
    assert "ap-1=" not in compact_hardware


def test_energy_object_inventory_stays_readable_in_narrow_terminal():
    event = events_by_sequence()["U6-0"]
    rows = _energy_object_inventory(event_to_yang(event, demo_energy_objects()), terminal_width=56)

    assert rows is not None
    assert all(len(row) <= 56 for row in rows)
    rendered = "\n".join(rows)
    assert "Relationships: " in rendered
    assert "AGGREGATING(2)" in rendered


def test_selected_uc_summary_and_compact_view_only_show_its_topology():
    simulator = EventSimulator(use_case=EventSeries.UC_2_1)
    scenario = simulator.network.scenarios_by_uc[EventSeries.UC_2_1.value]
    topology_ids = set(scenario.topology_ids)
    visible_ids = frozenset(
        energy_object_id
        for topology in simulator.network.topologies
        if topology.topology_id in topology_ids
        for energy_object_id in topology.energy_object_ids
    )
    event = simulator.next_event()
    assert event is not None
    data = filter_yang_instance_to_energy_objects(
        event_to_yang(event, simulator.energy_objects), visible_ids
    )

    summary = render_summary(event, data, visible_energy_object_ids=visible_ids)
    compact = render_compact_event(
        event,
        simulator.energy_objects,
        None,
        visible_energy_object_ids=visible_ids,
    )
    assert "eo-router-a" in summary
    assert "eo-ap-1" not in summary
    assert "eo-ap-1" not in compact


def test_selected_uc_netconf_trace_filters_objects_and_relationship_peers():
    data = {
        "ietf-hardware:hardware": {
            "component": [
                {"name": "router-A", "class": "iana-hardware:chassis"},
                {"name": "linecard-1", "parent": "router-A", "class": "iana-hardware:module"},
                {"name": "ap-1", "class": "iana-hardware:chassis"},
            ]
        },
        "ietf-power-and-energy:energy-objects": {
            "energy-object": [
                {
                    "id": "eo-router-a",
                    "source-component-id": "router-A",
                    "relationship": [{
                        "type": "ietf-power-and-energy:enabling",
                        "peer": [{"id": "eo-router-a-linecard-1"}, {"id": "eo-ap-1"}],
                    }],
                },
                {"id": "eo-router-a-linecard-1", "source-component-id": "linecard-1"},
                {"id": "eo-ap-1", "source-component-id": "ap-1"},
            ]
        },
    }
    entry = (
        "[2026-11-02T00:00:00Z] NETCONF operational-data request\n"
        "operation: <get>\nmodule: ietf-power-and-energy\n"
        "path: /ietf-power-and-energy:energy-objects\nrequest-xpath: /*\n"
        "status: ok\nreply-data-json:\n"
        + json.dumps(data)
    )

    formatted = format_netconf_trace_entry(entry, {"eo-router-a", "eo-router-a-linecard-1"})

    assert "eo-router-a" in formatted
    assert "linecard-1" in formatted
    assert "eo-ap-1" not in formatted
    assert "ap-1" not in formatted
