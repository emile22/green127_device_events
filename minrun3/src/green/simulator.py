from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from green.models import (
    ComponentState,
    EnergyObject,
    EnergyRelationship,
    EventSeries,
    MetricType,
    RawEnergyMeasurement,
    SimulatedEvent,
)
from green.topology import (
    SERVER_A_ID,
    SERVER_B_ID,
    UPSTREAM_METER_ID,
    demo_energy_objects,
    demo_metering_relationships,
)


@dataclass(frozen=True)
class _EventDefinition:
    series: EventSeries
    sequence: str
    name: str
    interval_energy_wh: tuple[tuple[str, int], ...]
    component_states: tuple[tuple[str, ComponentState], ...]
    metering_relationships: tuple[EnergyRelationship, ...]
    cumulative_enabled: bool = False


_ACTIVE_STATES = (
    (SERVER_A_ID, ComponentState.ACTIVE),
    (SERVER_B_ID, ComponentState.ACTIVE),
)

_FULL_METERING = demo_metering_relationships()
_PARTIAL_METERING = (_FULL_METERING[0],)

_UC_2_13_EVENTS = (
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-0",
        "RAW_MEASUREMENTS",
        ((UPSTREAM_METER_ID, 300), (SERVER_A_ID, 120), (SERVER_B_ID, 180)),
        _ACTIVE_STATES,
        (),
    ),
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-1",
        "TOPOLOGY_DISCOVERED",
        ((UPSTREAM_METER_ID, 300), (SERVER_A_ID, 120), (SERVER_B_ID, 180)),
        _ACTIVE_STATES,
        _FULL_METERING,
    ),
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-2",
        "NEXT_MEASUREMENT_INTERVAL",
        ((UPSTREAM_METER_ID, 340), (SERVER_A_ID, 140), (SERVER_B_ID, 190)),
        _ACTIVE_STATES,
        _FULL_METERING,
    ),
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-3",
        "TOPOLOGY_INCOMPLETE",
        ((UPSTREAM_METER_ID, 310), (SERVER_A_ID, 125), (SERVER_B_ID, 175)),
        _ACTIVE_STATES,
        _PARTIAL_METERING,
    ),
)

_UC_2_10_EVENTS = (
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-0",
        "TRAFFIC_HIGH",
        ((UPSTREAM_METER_ID, 300), (SERVER_A_ID, 120), (SERVER_B_ID, 180)),
        _ACTIVE_STATES,
        _FULL_METERING,
        cumulative_enabled=True,
    ),
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-1",
        "TRAFFIC_LOW",
        ((UPSTREAM_METER_ID, 150), (SERVER_A_ID, 60), (SERVER_B_ID, 90)),
        _ACTIVE_STATES,
        _FULL_METERING,
        cumulative_enabled=True,
    ),
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-2",
        "COMPONENT_SLEEP",
        ((UPSTREAM_METER_ID, 80), (SERVER_A_ID, 60), (SERVER_B_ID, 20)),
        ((SERVER_A_ID, ComponentState.ACTIVE), (SERVER_B_ID, ComponentState.LOW_POWER)),
        _FULL_METERING,
        cumulative_enabled=True,
    ),
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-3",
        "TRAFFIC_BURST",
        ((UPSTREAM_METER_ID, 360), (SERVER_A_ID, 150), (SERVER_B_ID, 210)),
        _ACTIVE_STATES,
        _FULL_METERING,
        cumulative_enabled=True,
    ),
)

_EVENTS = _UC_2_13_EVENTS + _UC_2_10_EVENTS


class EventSimulator:
    def __init__(self, energy_objects: tuple[EnergyObject, ...] | None = None) -> None:
        self.energy_objects = energy_objects or demo_energy_objects()
        self.reset()

    @property
    def has_next(self) -> bool:
        return self._index < len(_EVENTS)

    def peek_next(self) -> _EventDefinition | None:
        if not self.has_next:
            return None
        return _EVENTS[self._index]

    def reset(self) -> None:
        self._index = 0
        self._cumulative_energy_wh = {
            energy_object.energy_object_id: 0 for energy_object in self.energy_objects
        }
        self._component_states = {
            SERVER_A_ID: ComponentState.ACTIVE,
            SERVER_B_ID: ComponentState.ACTIVE,
        }

    def next_event(self) -> SimulatedEvent | None:
        if not self.has_next:
            return None

        event_index = self._index
        definition = _EVENTS[event_index]
        sequence = definition.sequence
        interval_values = dict(definition.interval_energy_wh)
        self._component_states.update(dict(definition.component_states))
        timestamp = (
            datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=event_index)
        ).isoformat()
        measurements: list[RawEnergyMeasurement] = []

        for energy_object in self.energy_objects:
            energy_object_id = energy_object.energy_object_id
            interval_energy_wh = interval_values[energy_object_id]
            cumulative_energy_wh = None
            if definition.cumulative_enabled:
                cumulative_energy_wh = (
                    self._cumulative_energy_wh[energy_object_id] + interval_energy_wh
                )
                self._cumulative_energy_wh[energy_object_id] = cumulative_energy_wh
            measurements.append(
                RawEnergyMeasurement(
                    measurement_id=f"{sequence}:{energy_object_id}",
                    device_id=energy_object.device_id,
                    energy_object_id=energy_object_id,
                    metric_type=MetricType.ENERGY_CONSUMED,
                    interval_energy_wh=interval_energy_wh,
                    cumulative_energy_wh=cumulative_energy_wh,
                    unit="Wh",
                    time_step=sequence,
                    interval_duration_seconds=3600,
                    timestamp_utc=timestamp,
                    provenance=f"{definition.series.value}-event-simulator",
                    freshness="fresh",
                )
            )

        self._index += 1
        return SimulatedEvent(
            series=definition.series,
            sequence=sequence,
            name=definition.name,
            component_states=tuple(self._component_states.items()),
            measurements=tuple(measurements),
            metering_relationships=definition.metering_relationships,
        )


def generate_events() -> tuple[SimulatedEvent, ...]:
    simulator = EventSimulator()
    events: list[SimulatedEvent] = []
    while (event := simulator.next_event()) is not None:
        events.append(event)
    return tuple(events)