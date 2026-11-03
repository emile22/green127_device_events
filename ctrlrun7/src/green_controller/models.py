from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EventReference:
    uc: str
    title: str
    event_id: str
    event_name: str
    description: str
    expected_yang: str
    simulator_metadata: str
    relationship_families: str


@dataclass(frozen=True)
class FieldObservation:
    device: str
    retrieved_at: str
    module: str
    data_path: str
    raw_value: str
    normalized_value: Any
    classification: str
    units: str | None = None


@dataclass(frozen=True)
class NetconfSnapshot:
    device: str
    retrieved_at: str
    raw_xml: str
    normalized: dict[str, Any]
    fields: tuple[FieldObservation, ...]


@dataclass(frozen=True)
class EventObservation:
    event: EventReference
    snapshot: NetconfSnapshot
    correlation: str
