from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from green.models import (
    ComponentState,
    EnergyObject,
    EnergyRelationship,
    EventSeries,
    MetricType,
    RawPowerMeasurement,
    RawEnergyMeasurement,
    SimulatedEvent,
)
from green.topology import (
    SERVER_A_ID,
    SERVER_B_ID,
    ROUTER_A_ID,
    ROUTER_B_ID,
    LINECARD_1_ID,
    LINECARD_2_ID,
    NON_CRITICAL_PORT_ID,
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
    explanation: str = ""
    metadata: tuple[tuple[str, str], ...] = ()
    instantaneous_power_w: tuple[tuple[str, int], ...] = ()


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
        explanation="Measurements exist, but missing topology prevents reliable de-duplication.",
    ),
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-1",
        "TOPOLOGY_DISCOVERED",
        ((UPSTREAM_METER_ID, 300), (SERVER_A_ID, 120), (SERVER_B_ID, 180)),
        _ACTIVE_STATES,
        _FULL_METERING,
        explanation="Metering relationships now reveal which downstream measurements are already represented upstream.",
    ),
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-2",
        "NEXT_MEASUREMENT_INTERVAL",
        ((UPSTREAM_METER_ID, 340), (SERVER_A_ID, 140), (SERVER_B_ID, 190)),
        _ACTIVE_STATES,
        _FULL_METERING,
        explanation="New values prove de-duplication depends on topology rather than numerical equality.",
    ),
    _EventDefinition(
        EventSeries.UC_2_13,
        "U13-3",
        "TOPOLOGY_INCOMPLETE",
        ((UPSTREAM_METER_ID, 310), (SERVER_A_ID, 125), (SERVER_B_ID, 175)),
        _ACTIVE_STATES,
        _PARTIAL_METERING,
        explanation="A missing relationship makes the energy accounting boundary incomplete again.",
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
        explanation="High traffic keeps both components active and produces the highest normal energy demand.",
    ),
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-1",
        "TRAFFIC_LOW",
        ((UPSTREAM_METER_ID, 150), (SERVER_A_ID, 60), (SERVER_B_ID, 90)),
        _ACTIVE_STATES,
        _FULL_METERING,
        cumulative_enabled=True,
        explanation="Lower traffic reduces component activity and measured energy consumption.",
    ),
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-2",
        "COMPONENT_SLEEP",
        ((UPSTREAM_METER_ID, 80), (SERVER_A_ID, 60), (SERVER_B_ID, 20)),
        ((SERVER_A_ID, ComponentState.ACTIVE), (SERVER_B_ID, ComponentState.LOW_POWER)),
        _FULL_METERING,
        cumulative_enabled=True,
        explanation="Low traffic lets server-B enter low-power mode and reduce consumption.",
    ),
    _EventDefinition(
        EventSeries.UC_2_10,
        "U10-3",
        "TRAFFIC_BURST",
        ((UPSTREAM_METER_ID, 360), (SERVER_A_ID, 150), (SERVER_B_ID, 210)),
        _ACTIVE_STATES,
        _FULL_METERING,
        cumulative_enabled=True,
        explanation="A sudden traffic burst wakes server-B and sharply increases energy consumption.",
    ),
)

_UC_2_1_EVENTS = (
    _EventDefinition(
        EventSeries.UC_2_1,
        "U1-0",
        "LEGACY_BASELINE",
        (),
        (),
        (),
        explanation="A legacy router has only reference power data and no GREEN telemetry.",
        metadata=(
            ("baseline-power-w", "500"),
            ("baseline-source", "vendor-datasheet"),
            ("green-telemetry", "unavailable"),
            ("classification", "baseline-only"),
        ),
    ),
    _EventDefinition(
        EventSeries.UC_2_1,
        "U1-1",
        "COMPONENT_GREEN_ENABLED",
        (),
        ((LINECARD_1_ID, ComponentState.ACTIVE),),
        (),
        explanation="One component gains GREEN telemetry while the remainder of the router stays legacy.",
        metadata=(
            ("linecard-1-status", "measured"),
            ("linecard-2-status", "legacy-unmeasured"),
        ),
        instantaneous_power_w=((LINECARD_1_ID, 120),),
    ),
    _EventDefinition(
        EventSeries.UC_2_1,
        "U1-2",
        "DEVICE_GREEN_ENABLED",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE),),
        (),
        explanation="Device-wide GREEN measurements now allow comparison against the original legacy baseline.",
        metadata=(
            ("baseline-power-w", "500"),
            ("baseline-source", "vendor-datasheet"),
            ("observed-power-w", "420"),
            ("power-delta-w", "-80"),
            ("power-reduction-percent", "16"),
            ("classification", "measured"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 420),),
    ),
    _EventDefinition(
        EventSeries.UC_2_1,
        "U1-3",
        "NETWORK_MIXED_DEPLOYMENT",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE), (ROUTER_B_ID, ComponentState.ACTIVE)),
        (),
        explanation="The network now combines partially migrated and fully GREEN-enabled devices.",
        metadata=(
            ("router-A-deployment", "partially-green-enabled"),
            ("router-B-deployment", "fully-green-enabled"),
            ("router-A-data-classification", "measured"),
            ("router-B-data-classification", "measured"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 420), (ROUTER_B_ID, 380)),
    ),
)

_UC_2_14_EVENTS = (
    _EventDefinition(
        EventSeries.UC_2_14,
        "U14-0",
        "GRID_NORMAL",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE), (ROUTER_B_ID, ComponentState.ACTIVE),
         (NON_CRITICAL_PORT_ID, ComponentState.ACTIVE)),
        (),
        explanation="Normal grid power lets every component and service operate without energy restrictions.",
        metadata=(
            ("power-source", "grid"),
            ("critical-service", "active"),
            ("non-critical-service", "active"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 500), (ROUTER_B_ID, 400)),
    ),
    _EventDefinition(
        EventSeries.UC_2_14,
        "U14-1",
        "GRID_FAILURE",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE), (ROUTER_B_ID, ComponentState.ACTIVE),
         (NON_CRITICAL_PORT_ID, ComponentState.ACTIVE)),
        (),
        explanation="Grid power fails, so the simulated network switches to its backup energy source.",
        metadata=(
            ("power-source", "battery"),
            ("battery-level-percent", "100"),
            ("critical-service", "active"),
            ("non-critical-service", "active"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 480), (ROUTER_B_ID, 390)),
    ),
    _EventDefinition(
        EventSeries.UC_2_14,
        "U14-2",
        "BATTERY_OPERATION",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE), (ROUTER_B_ID, ComponentState.LOW_POWER),
         (NON_CRITICAL_PORT_ID, ComponentState.OFF)),
        (),
        explanation="Falling battery capacity triggers energy-saving actions while normal connectivity remains available.",
        metadata=(
            ("power-source", "battery"),
            ("battery-level-percent", "55"),
            ("critical-service", "active"),
            ("non-critical-port", "disabled"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 420), (ROUTER_B_ID, 250)),
    ),
    _EventDefinition(
        EventSeries.UC_2_14,
        "U14-3",
        "ENERGY_CRITICAL",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE), (ROUTER_B_ID, ComponentState.LOW_POWER),
         (NON_CRITICAL_PORT_ID, ComponentState.OFF)),
        (),
        explanation="Critical battery levels disable non-essential functions while preserving essential network service.",
        metadata=(
            ("power-source", "battery"),
            ("battery-level-percent", "15"),
            ("network-mode", "constrained"),
            ("critical-service", "active"),
            ("non-critical-service", "disabled"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 380), (ROUTER_B_ID, 200)),
    ),
    _EventDefinition(
        EventSeries.UC_2_14,
        "U14-4",
        "GRID_RESTORED",
        (),
        ((ROUTER_A_ID, ComponentState.ACTIVE), (ROUTER_B_ID, ComponentState.ACTIVE),
         (NON_CRITICAL_PORT_ID, ComponentState.ACTIVE)),
        (),
        explanation="Grid power returns, restoring normal operation while the backup battery begins recharging.",
        metadata=(
            ("power-source", "grid"),
            ("battery", "charging"),
            ("critical-service", "active"),
            ("non-critical-service", "active"),
        ),
        instantaneous_power_w=((ROUTER_A_ID, 500), (ROUTER_B_ID, 400)),
    ),
)

_EVENTS = _UC_2_13_EVENTS + _UC_2_10_EVENTS + _UC_2_1_EVENTS + _UC_2_14_EVENTS


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
            energy_object.energy_object_id: ComponentState.ACTIVE
            for energy_object in self.energy_objects
        }

    def next_event(self) -> SimulatedEvent | None:
        if not self.has_next:
            return None

        event_index = self._index
        definition = _EVENTS[event_index]
        sequence = definition.sequence
        objects_by_id = {obj.energy_object_id: obj for obj in self.energy_objects}
        self._component_states.update(dict(definition.component_states))
        timestamp = (
            datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=event_index)
        ).isoformat()
        measurements: list[RawEnergyMeasurement] = []

        for energy_object_id, interval_energy_wh in definition.interval_energy_wh:
            energy_object = objects_by_id[energy_object_id]
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

        power_measurements = tuple(
            RawPowerMeasurement(
                measurement_id=f"{sequence}:power:{energy_object_id}",
                device_id=objects_by_id[energy_object_id].device_id,
                energy_object_id=energy_object_id,
                instantaneous_power_w=power_w,
                timestamp_utc=timestamp,
                provenance=f"{definition.series.value}-event-simulator",
                freshness="fresh",
            )
            for energy_object_id, power_w in definition.instantaneous_power_w
        )

        self._index += 1
        return SimulatedEvent(
            series=definition.series,
            sequence=sequence,
            name=definition.name,
            component_states=definition.component_states,
            measurements=tuple(measurements),
            metering_relationships=definition.metering_relationships,
            explanation=definition.explanation,
            metadata=definition.metadata,
            power_measurements=power_measurements,
        )


def generate_events() -> tuple[SimulatedEvent, ...]:
    simulator = EventSimulator()
    events: list[SimulatedEvent] = []
    while (event := simulator.next_event()) is not None:
        events.append(event)
    return tuple(events)