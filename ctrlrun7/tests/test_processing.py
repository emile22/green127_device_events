from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from green_controller.aggregation import (
    IncompatibleMeasurements,
    directed_metering_edges,
    metering_reachable,
    numeric_aggregate,
)
import green_controller.cli as cli
from green_controller.normalize import parse_netconf_xml
from green_controller.processing import process_snapshot


FIXTURE = Path(__file__).parent / "fixtures" / "netconf_reply.xml"


def fixture_snapshot():
    return parse_netconf_xml(
        FIXTURE.read_text(encoding="utf-8"),
        device="fixture-device",
        retrieved_at="2026-10-31T00:00:00+00:00",
    )


def test_power_transformation_and_aggregate_keep_provenance(tmp_path: Path) -> None:
    result = process_snapshot(fixture_snapshot().normalized, tmp_path)
    power = result["derived_values"]["instantaneous_power"]
    provenance = next(item for item in result["provenance"] if item["name"] == "observed-power-dashboard-statistics")

    assert power["sum_watts"] == "420"
    assert power["average_watts"] == "420"
    assert power["status"] == "derived-dashboard-statistic; not accounting-authoritative"
    assert provenance["inputs"][0]["object_id"] == "eo-router-a"
    assert provenance["source_yang_paths"][0].endswith("/power/instantaneous-power")
    assert provenance["transformation"]
    assert provenance["status"] == "derived"


def test_cumulative_energy_without_interval_semantics_is_not_summed(tmp_path: Path) -> None:
    result = process_snapshot(fixture_snapshot().normalized, tmp_path)
    energy = result["derived_values"]["interval_energy"]
    provenance = next(item for item in result["provenance"] if item["name"] == "interval-energy-accounting")

    assert energy["status"] == "incomplete"
    assert energy["accounted_total"] is None
    assert energy["cumulative_values"][0]["raw_value"] == "123456"
    assert provenance["value"] is None
    assert provenance["status"] == "incomplete"


def test_numeric_aggregation_rejects_mixed_units_and_intervals() -> None:
    with pytest.raises(IncompatibleMeasurements):
        numeric_aggregate([
            {"value": 100, "unit": "mWatts", "interval": None},
            {"value": 1, "unit": "Watts", "interval": None},
        ])
    with pytest.raises(IncompatibleMeasurements):
        numeric_aggregate([
            {"value": 100, "unit": "Wh", "interval": "t0/t1"},
            {"value": 120, "unit": "Wh", "interval": "t1/t2"},
        ])


def test_relationship_traversal_uses_only_metering_direction() -> None:
    relations = [
        {"source_energy_object_id": "meter", "relationship_type": "metering", "peer_energy_object_id": "server"},
        {"source_energy_object_id": "agg", "relationship_type": "aggregating", "peer_energy_object_id": "server"},
        {"source_energy_object_id": "psu", "relationship_type": "powering", "peer_energy_object_id": "server"},
    ]
    edges = directed_metering_edges(relations)
    paths = metering_reachable("meter", edges)
    assert paths == {"server": ["meter metering server"]}
    assert directed_metering_edges(relations[1:]) == []


def test_every_group_a_use_case_has_read_only_recommendation_and_coverage_handoff(tmp_path: Path) -> None:
    result = process_snapshot(fixture_snapshot().normalized, tmp_path)
    recommendations = result["recommendations"]
    assert len(recommendations) == 14
    assert len({item["uc"] for item in recommendations}) == 14
    assert all(item["execution_status"] == "prepared-only; no device operation performed" for item in recommendations)
    assert all("edit-config" not in item["recommendation"].lower() for item in recommendations)

    handoff = json.loads((tmp_path / "docs" / "green8_input.json").read_text(encoding="utf-8"))
    assert len(handoff) == 14
    required = {
        "uc", "uc_full_name", "event_ids", "requirement", "scope", "searched_modules",
        "searched_paths", "coverage", "workaround", "impact", "example_runtime_value",
    }
    assert all(required <= item.keys() for item in handoff)
    assert all(not ({"gap_id", "gap_classification", "proposed_yang"} & item.keys()) for item in handoff)
    assert result["coverage"]["requirements"] == 14


def test_network_view_keeps_exact_direction_and_unknown_event_identity(tmp_path: Path) -> None:
    result = process_snapshot(fixture_snapshot().normalized, tmp_path)
    assert result["controller_network_view"]["event_identity"] == "unavailable in current YANG snapshot"
    edges = result["relationship_context"]["directional_edges"]
    assert any(edge["source_energy_object_id"] == "eo-router-a" and edge["relationship_type"] == "metering" for edge in edges)
    assert not any(edge.get("derived_inverse") for edge in edges)


def test_watch_loop_exits_cleanly_when_q_is_requested(tmp_path: Path, monkeypatch, capsys) -> None:
    class FakeContext:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(cli.NetconfClient, "connect_from_environment", lambda: FakeContext())
    monkeypatch.setattr(cli, "_process_cycle", lambda *args, **kwargs: {})
    monkeypatch.setattr(cli, "_wait_for_interval", lambda interval: True)

    result = cli.main(["--watch", "--interval", "1", "--output", str(tmp_path)])
    output = capsys.readouterr().out
    assert result == 0
    assert "Press q to stop" in output
    assert "stopped by q" in output
