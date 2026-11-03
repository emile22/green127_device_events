from dataclasses import dataclass
from typing import Mapping

from green.topology import Topology


@dataclass(frozen=True)
class AccountingResult:
    naive_total_wh: int
    accounted_total_wh: int
    topology_complete: bool


class AccountingEngine:
    """Demo-only boundary-meter arithmetic; this is not UC 2.13 accounting."""

    def compute(
        self,
        boundary: str,
        measurements: Mapping[str, int],
        topology: Topology,
    ) -> AccountingResult:
        if boundary != topology.upstream_meter:
            raise ValueError("boundary must be the topology's upstream meter")
        if boundary not in measurements:
            raise ValueError(f"missing boundary measurement: {boundary}")

        return AccountingResult(
            naive_total_wh=sum(measurements.values()),
            accounted_total_wh=measurements[boundary],
            topology_complete=all(node in measurements for node in topology.nodes),
        )