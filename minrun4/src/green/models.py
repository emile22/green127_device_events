from dataclasses import dataclass
from enum import Enum


class RelationshipType(str, Enum):
    METERING = "metering"
    METERED_BY = "metered-by"
    AGGREGATING = "aggregating"
    AGGREGATED_BY = "aggregated-by"
    POWERING = "powering"
    POWERED_BY = "powered-by"


class MetricType(str, Enum):
    ENERGY_CONSUMED = "energy-consumed"


class ComponentState(str, Enum):
    ACTIVE = "active"
    LOW_POWER = "low-power"
    OFF = "off"


class EventSeries(str, Enum):
    UC_2_13 = "UC 2.13"
    UC_2_10 = "UC 2.10"
    UC_2_1 = "UC 2.1"
    UC_2_14 = "UC 2.14"


class TopologyStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete-topology"
    INVALID = "invalid-topology"


@dataclass(frozen=True)
class EnergyObject:
    device_id: str
    energy_object_id: str
    hardware_component_name: str | None
    hardware_component_uuid: str | None


@dataclass(frozen=True)
class EnergyRelationship:
    relationship_id: str
    relationship_type: RelationshipType
    source_energy_object_id: str
    peer_energy_object_id: str
    provenance: str


@dataclass(frozen=True)
class AccountingBoundary:
    boundary_id: str
    root_energy_object_id: str
    energy_object_ids: tuple[str, ...]


@dataclass(frozen=True)
class RawEnergyMeasurement:
    measurement_id: str
    device_id: str
    energy_object_id: str
    metric_type: MetricType
    interval_energy_wh: int
    cumulative_energy_wh: int | None
    unit: str
    time_step: str
    interval_duration_seconds: int
    timestamp_utc: str
    provenance: str
    freshness: str
    accuracy_percent: float | None = None


@dataclass(frozen=True)
class RawPowerMeasurement:
    measurement_id: str
    device_id: str
    energy_object_id: str
    instantaneous_power_w: int
    timestamp_utc: str
    provenance: str
    freshness: str


@dataclass(frozen=True)
class SimulatedEvent:
    series: EventSeries
    sequence: str
    name: str
    component_states: tuple[tuple[str, ComponentState], ...]
    measurements: tuple[RawEnergyMeasurement, ...]
    metering_relationships: tuple[EnergyRelationship, ...]
    explanation: str = ""
    metadata: tuple[tuple[str, str], ...] = ()
    power_measurements: tuple[RawPowerMeasurement, ...] = ()


@dataclass(frozen=True)
class ExcludedMeasurement:
    measurement: RawEnergyMeasurement
    reason: str
    relationship_path: tuple[EnergyRelationship, ...]


@dataclass(frozen=True)
class AccountingResult:
    series: str
    event_sequence: str
    event_name: str
    boundary: AccountingBoundary
    time_step: str
    raw_measurements: tuple[RawEnergyMeasurement, ...]
    naive_total_wh: int
    accounted_total_wh: int | None
    included_measurements: tuple[RawEnergyMeasurement, ...]
    excluded_measurements: tuple[ExcludedMeasurement, ...]
    relationships_used: tuple[EnergyRelationship, ...]
    topology_status: TopologyStatus
    warnings: tuple[str, ...]
    errors: tuple[str, ...]