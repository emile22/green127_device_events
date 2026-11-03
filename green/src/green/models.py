from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Event:
    name: str
    measurements: Mapping[str, int]