import json
import xml.etree.ElementTree as ET

from green.cli import visible_energy_object_ids_for_use_case
from green.models import EventSeries
from green.netconf_trace import format_netconf_trace_entry
from green.simulator import EventSimulator, generate_events
from green.topology import demo_energy_objects
from green.views import (
    event_to_yang,
    filter_netconf_xml_to_energy_objects,
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

    selected_diff = render_relationship_diff(
        events["U13-0"],
        events["U13-1"],
        {"eo-upstream-meter", "eo-server-a"},
    )
    assert "eo-server-a METERED-BY -> eo-upstream-meter" in selected_diff
    assert "eo-server-b" not in selected_diff


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


def test_selected_uc_filters_summary_compact_and_trace_tables():
    simulator = EventSimulator(use_case=EventSeries.UC_2_1)
    visible_ids = visible_energy_object_ids_for_use_case(
        EventSeries.UC_2_1,
        simulator.energy_objects,
    )
    simulator.next_event()
    event = simulator.next_event()
    assert event is not None
    all_data = event_to_yang(event, simulator.energy_objects)
    data = filter_yang_instance_to_energy_objects(all_data, visible_ids)

    summary = render_summary(event, data, visible_energy_object_ids=visible_ids)
    compact = render_compact_event(
        event,
        simulator.energy_objects,
        None,
        visible_energy_object_ids=visible_ids,
    )
    trace_entry = (
        "[2026-11-02T00:00:00Z] NETCONF operational-data request\n"
        "operation: <get>\nmodule: ietf-power-and-energy\n"
        "path: /ietf-power-and-energy:energy-objects\nrequest-xpath: /*\n"
        "status: ok\nreply-data-json:\n"
        + json.dumps(all_data)
    )
    trace = format_netconf_trace_entry(trace_entry, visible_ids)
    json_view = render_json(data)
    filtered_ids = {
        item["id"]
        for item in data["ietf-power-and-energy:energy-objects"]["energy-object"]
    }

    assert "eo-router-a-linecard-2" in visible_ids
    assert "eo-router-a-linecard-2" in filtered_ids
    assert "eo-ap-1" not in filtered_ids
    assert "eo-ap-1" not in json_view
    assert "eo-ap-1" not in summary
    assert "eo-ap-1" not in compact
    assert "eo-ap-1" not in trace
    assert "linecard-1" in summary
    assert "linecard-1" in trace


def test_selected_uc_xml_filters_objects_and_relationship_peers():
    xml = """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <nc:data>
        <hw:hardware xmlns:hw="urn:ietf:params:xml:ns:yang:ietf-hardware">
            <hw:component><hw:name>router-A</hw:name></hw:component>
            <hw:component><hw:name>linecard-1</hw:name><hw:parent>router-A</hw:parent></hw:component>
            <hw:component><hw:name>ap-1</hw:name></hw:component>
        </hw:hardware>
        <pae:energy-objects xmlns:pae="urn:ietf:params:xml:ns:yang:ietf-power-and-energy">
            <pae:energy-object><pae:id>eo-router-a</pae:id>
                <pae:source-component-id>router-A</pae:source-component-id>
                <pae:relationship><pae:type>pae:enabling</pae:type>
                    <pae:peer><pae:id>eo-linecard</pae:id></pae:peer>
                    <pae:peer><pae:id>eo-ap</pae:id></pae:peer>
                </pae:relationship>
            </pae:energy-object>
            <pae:energy-object><pae:id>eo-linecard</pae:id>
                <pae:source-component-id>linecard-1</pae:source-component-id></pae:energy-object>
            <pae:energy-object><pae:id>eo-ap</pae:id>
                <pae:source-component-id>ap-1</pae:source-component-id></pae:energy-object>
        </pae:energy-objects>
    </nc:data>
</nc:rpc-reply>"""

    filtered = filter_netconf_xml_to_energy_objects(
        xml,
        {"eo-router-a", "eo-linecard"},
    )
    root = ET.fromstring(filtered)
    hardware_ns = "urn:ietf:params:xml:ns:yang:ietf-hardware"
    energy_ns = "urn:ietf:params:xml:ns:yang:ietf-power-and-energy"
    object_ids = {
        item.findtext(f"{{{energy_ns}}}id")
        for item in root.findall(f".//{{{energy_ns}}}energy-object")
    }
    peer_ids = {
        item.findtext(f"{{{energy_ns}}}id")
        for item in root.findall(f".//{{{energy_ns}}}relationship/{{{energy_ns}}}peer")
    }
    component_names = {
        item.findtext(f"{{{hardware_ns}}}name")
        for item in root.findall(f".//{{{hardware_ns}}}component")
    }

    assert object_ids == {"eo-router-a", "eo-linecard"}
    assert peer_ids == {"eo-linecard"}
    assert component_names == {"router-A", "linecard-1"}
