from green.models import ComponentState, EventSeries
from green.simulator import EventSimulator
from green.topology import (
    LINECARD_1_ID,
    LINECARD_2_ID,
    NON_CRITICAL_PORT_ID,
    ROUTER_A_ID,
    ROUTER_B_ID,
    SERVER_A_ID,
    SERVER_B_ID,
    UPSTREAM_METER_ID,
)


def collect_events(simulator: EventSimulator):
    events = []
    while (event := simulator.next_event()) is not None:
        events.append(event)
    return events


def values_by_object(events, field: str, object_id: str) -> list[int]:
    return [
        getattr(next(item for item in event.measurements if item.energy_object_id == object_id), field)
        for event in events
    ]


def test_simulator_emits_all_four_series_in_required_order() -> None:
    events = collect_events(EventSimulator())

    assert [event.sequence for event in events] == [
        "U13-0",
        "U13-1",
        "U13-2",
        "U13-3",
        "U10-0",
        "U10-1",
        "U10-2",
        "U10-3",
        "U1-0",
        "U1-1",
        "U1-2",
        "U1-3",
        "U14-0",
        "U14-1",
        "U14-2",
        "U14-3",
        "U14-4",
    ]
    assert [event.series for event in events] == (
        [EventSeries.UC_2_13] * 4
        + [EventSeries.UC_2_10] * 4
        + [EventSeries.UC_2_1] * 4
        + [EventSeries.UC_2_14] * 5
    )
    assert [event.name for event in events[:4]] == [
        "RAW_MEASUREMENTS",
        "TOPOLOGY_DISCOVERED",
        "NEXT_MEASUREMENT_INTERVAL",
        "TOPOLOGY_INCOMPLETE",
    ]
    assert [event.name for event in events[4:8]] == [
        "TRAFFIC_HIGH",
        "TRAFFIC_LOW",
        "COMPONENT_SLEEP",
        "TRAFFIC_BURST",
    ]
    assert len(events) == 17


def test_every_event_has_one_short_deterministic_explanation() -> None:
    events = collect_events(EventSimulator())

    assert all(event.explanation for event in events)
    assert all(len(event.explanation.split()) < 20 for event in events)
    assert all(event.explanation.count(".") == 1 for event in events)


def test_uc_2_13_measurements_and_topology_progression() -> None:
    events = collect_events(EventSimulator())[:4]

    assert values_by_object(events, "interval_energy_wh", UPSTREAM_METER_ID) == [300, 300, 340, 310]
    assert values_by_object(events, "interval_energy_wh", SERVER_A_ID) == [120, 120, 140, 125]
    assert values_by_object(events, "interval_energy_wh", SERVER_B_ID) == [180, 180, 190, 175]
    assert [len(event.metering_relationships) for event in events] == [0, 2, 2, 1]


def test_interval_energy_and_cumulative_energy_are_distinct() -> None:
    events = collect_events(EventSimulator())[4:8]

    assert values_by_object(events, "cumulative_energy_wh", UPSTREAM_METER_ID) == [300, 450, 530, 890]
    assert values_by_object(events, "cumulative_energy_wh", SERVER_A_ID) == [120, 180, 240, 390]
    assert values_by_object(events, "cumulative_energy_wh", SERVER_B_ID) == [180, 270, 290, 500]
    assert values_by_object(events, "interval_energy_wh", UPSTREAM_METER_ID) != values_by_object(
        events, "cumulative_energy_wh", UPSTREAM_METER_ID
    )
    assert all(
        measurement.cumulative_energy_wh is None
        for event in collect_events(EventSimulator())[:4]
        for measurement in event.measurements
    )


def test_component_state_tracks_sleep_and_burst() -> None:
    events = collect_events(EventSimulator())[4:8]

    server_b_states = [dict(event.component_states)[SERVER_B_ID] for event in events]

    assert server_b_states == [
        ComponentState.ACTIVE,
        ComponentState.ACTIVE,
        ComponentState.LOW_POWER,
        ComponentState.ACTIVE,
    ]


def test_restart_resets_simulator_counters_and_component_states() -> None:
    simulator = EventSimulator()
    for _ in range(4):
        simulator.next_event()
    first_u10 = simulator.next_event()
    assert first_u10 is not None
    assert first_u10.sequence == "U10-0"

    simulator.reset()
    restarted = simulator.next_event()

    assert restarted is not None
    assert restarted.sequence == "U13-0"
    for _ in range(3):
        simulator.next_event()
    restarted_u10 = simulator.next_event()
    assert restarted_u10 is not None
    assert restarted_u10.sequence == "U10-0"
    assert values_by_object((restarted_u10,), "cumulative_energy_wh", UPSTREAM_METER_ID) == [300]
    assert dict(restarted_u10.component_states)[SERVER_B_ID] is ComponentState.ACTIVE


def test_uc_2_1_legacy_and_partial_deployment_never_synthesize_missing_data() -> None:
    events = collect_events(EventSimulator())[8:12]
    legacy, component, device, mixed = events

    assert legacy.measurements == ()
    assert legacy.power_measurements == ()
    assert dict(legacy.metadata)["classification"] == "baseline-only"
    assert {measurement.energy_object_id for measurement in component.power_measurements} == {
        LINECARD_1_ID
    }
    assert LINECARD_2_ID not in {
        measurement.energy_object_id
        for measurement in component.measurements + component.power_measurements
    }
    assert dict(device.metadata)["baseline-power-w"] == "500"
    assert dict(device.metadata)["observed-power-w"] == "420"
    assert dict(device.metadata)["power-reduction-percent"] == "16"
    assert dict(mixed.metadata)["router-A-deployment"] == "partially-green-enabled"
    assert dict(mixed.metadata)["router-B-deployment"] == "fully-green-enabled"


def test_uc_2_14_grid_battery_critical_and_recovery_transitions() -> None:
    events = collect_events(EventSimulator())[12:]
    normal, failure, battery, critical, restored = events

    assert dict(normal.metadata)["power-source"] == "grid"
    assert dict(failure.metadata)["power-source"] == "battery"
    assert dict(failure.metadata)["battery-level-percent"] == "100"
    assert dict(battery.metadata)["battery-level-percent"] == "55"
    assert dict(battery.component_states)[ROUTER_B_ID] is ComponentState.LOW_POWER
    assert dict(battery.component_states)[NON_CRITICAL_PORT_ID] is ComponentState.OFF
    assert dict(critical.metadata)["battery-level-percent"] == "15"
    assert dict(critical.metadata)["critical-service"] == "active"
    assert dict(critical.metadata)["non-critical-service"] == "disabled"
    assert dict(critical.component_states)[ROUTER_A_ID] is ComponentState.ACTIVE
    assert dict(restored.metadata)["power-source"] == "grid"
    assert dict(restored.metadata)["battery"] == "charging"
    assert dict(restored.component_states)[ROUTER_B_ID] is ComponentState.ACTIVE