import json

from green.simulator import generate_events
from green.topology import demo_energy_objects
from green.views import (
    event_to_yang,
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
