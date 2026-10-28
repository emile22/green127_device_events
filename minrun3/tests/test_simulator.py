from green.models import ComponentState
from green.simulator import EventSimulator
from green.topology import SERVER_A_ID, SERVER_B_ID, UPSTREAM_METER_ID


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


def test_simulator_emits_the_two_series_in_required_order() -> None:
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
    ]
    assert [event.series.value for event in events] == ["UC 2.13"] * 4 + ["UC 2.10"] * 4
    assert [event.name for event in events[:4]] == [
        "RAW_MEASUREMENTS",
        "TOPOLOGY_DISCOVERED",
        "NEXT_MEASUREMENT_INTERVAL",
        "TOPOLOGY_INCOMPLETE",
    ]
    assert [event.name for event in events[4:]] == [
        "TRAFFIC_HIGH",
        "TRAFFIC_LOW",
        "COMPONENT_SLEEP",
        "TRAFFIC_BURST",
    ]


def test_uc_2_13_measurements_and_topology_progression() -> None:
    events = collect_events(EventSimulator())[:4]

    assert values_by_object(events, "interval_energy_wh", UPSTREAM_METER_ID) == [300, 300, 340, 310]
    assert values_by_object(events, "interval_energy_wh", SERVER_A_ID) == [120, 120, 140, 125]
    assert values_by_object(events, "interval_energy_wh", SERVER_B_ID) == [180, 180, 190, 175]
    assert [len(event.metering_relationships) for event in events] == [0, 2, 2, 1]


def test_interval_energy_and_cumulative_energy_are_distinct() -> None:
    events = collect_events(EventSimulator())[4:]

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
    events = collect_events(EventSimulator())[4:]

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