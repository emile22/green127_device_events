from __future__ import annotations

import json
import hashlib
from pathlib import Path

from green_controller.catalog import load_event_catalog
from green_controller.collector import (
    observe_event_catalog,
    store_snapshot,
    write_observation_catalog,
)
import green_controller.cli as cli
import green_controller.collector as collector
from green_controller.diff import snapshot_diff
from green_controller.models import NetconfSnapshot
from green_controller.normalize import parse_netconf_xml
import green_controller.netconf_client as netconf_client
from green_controller.netconf_client import NetconfClient, NetconfUnavailable
from green_controller.relationships import directional_graph
from green_controller.render import render


FIXTURE = Path(__file__).parent / "fixtures" / "netconf_reply.xml"


class FixtureClient:
    device = "fixture-router"

    def __init__(self) -> None:
        self.calls = 0
        self.xml = FIXTURE.read_text(encoding="utf-8")

    def get(self) -> str:
        self.calls += 1
        return self.xml


def snapshot(xml: str | None = None, *, retrieved_at: str = "2026-10-31T00:00:00+00:00") -> NetconfSnapshot:
    return parse_netconf_xml(xml or FIXTURE.read_text(encoding="utf-8"), device="fixture-router", retrieved_at=retrieved_at)


def test_normalization_keeps_identifiers_and_explicit_hardware_mapping_separate() -> None:
    result = snapshot()
    normalized = result.normalized
    component = normalized["ietf-hardware:hardware"]["component"][1]
    energy = normalized["ietf-power-and-energy:energy-objects"]["energy-object"][0]

    assert component["name"] == "linecard-1"
    assert component["uuid"] == "00000000-0000-4000-8000-000000000011"
    assert component["parent"] == "router-A"
    assert energy["id"] == "eo-router-a"
    assert energy["source-component-id"] == "router-A"
    assert energy["hardware-correlation"]["uuid"] != energy["id"]
    assert energy["device-id"] == "fixture-router"


def test_raw_and_normalized_values_are_retained_with_schema_units() -> None:
    result = snapshot()
    assert result.raw_xml.startswith("<rpc-reply")
    power = next(field for field in result.fields if field.data_path.endswith("/instantaneous-power"))
    energy = next(field for field in result.fields if field.data_path.endswith("/total-energy-consumed"))

    assert power.raw_value == "420000"
    assert power.normalized_value == 420000
    assert power.units == "mWatts"
    assert energy.raw_value == "123456"
    assert energy.normalized_value == 123456
    assert energy.units == "Watt-hours (declared; description states mWh)"


def test_missing_telemetry_stays_absent_instead_of_becoming_zero() -> None:
    result = snapshot()
    linecard = result.normalized["ietf-power-and-energy:energy-objects"]["energy-object"][1]
    assert "power" not in linecard
    assert "energy" not in linecard
    assert not any(
        field.data_path.startswith("/ietf-power-and-energy:energy-objects/energy-object[id='eo-linecard-1']")
        and field.data_path.endswith(("/instantaneous-power", "/total-energy-consumed"))
        for field in result.fields
    )


def test_relationship_graph_preserves_direction_and_does_not_synthesize_inverses() -> None:
    result = snapshot()
    graph = directional_graph(result.normalized["relationships"])
    assert graph["eo-router-a"] == [
        {"type": "enabling", "peer": "eo-linecard-1", "direction": "as-reported"},
        {"type": "metering", "peer": "eo-upstream-meter", "direction": "as-reported"},
    ]
    assert "eo-linecard-1" not in graph
    assert {edge["relationship_type"] for edge in result.normalized["relationships"]} == {
        "metering", "enabling", "powering", "aggregating"
    }


def test_diff_reports_measurement_changes() -> None:
    before = snapshot(retrieved_at="2026-10-31T00:00:00+00:00").normalized
    xml = FIXTURE.read_text(encoding="utf-8").replace("420000", "410000")
    after = snapshot(xml, retrieved_at="2026-10-31T00:00:01+00:00").normalized
    diff = snapshot_diff(before, after)
    assert diff["changed"][0]["id"] == "eo-router-a"
    assert diff["changed"][0]["before"]["power"]["instantaneous-power"] == 420000
    assert diff["changed"][0]["after"]["power"]["instantaneous-power"] == 410000


def test_watch_prints_initial_summary_then_only_nonempty_diffs(tmp_path: Path, monkeypatch, capsys) -> None:
    base_data = {
        "device": "fixture-router",
        "retrieved_at": "2026-10-31T00:00:00+00:00",
        "ietf-hardware:hardware": {"component": []},
        "ietf-power-and-energy:energy-objects": {
            "energy-object": [{"id": "eo-router-a", "source-component-id": "router-A"}]
        },
        "relationships": [],
    }
    base = NetconfSnapshot("fixture-router", "t0", "<data/>", base_data, ())
    changed_data = {
        **base_data,
        "ietf-power-and-energy:energy-objects": {
            "energy-object": [{"id": "eo-router-a", "source-component-id": "router-A", "power": {"instantaneous-power": 410000}}]
        },
    }
    changed = NetconfSnapshot("fixture-router", "t1", "<data/>", changed_data, ())

    class FakeContext:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(cli.NetconfClient, "connect_from_environment", lambda: FakeContext())
    snapshots = iter((base, base, changed))
    monkeypatch.setattr(collector, "collect_once", lambda client: next(snapshots))

    first = cli._one_live_snapshot(tmp_path, "summary")
    assert "Device: fixture-router" in capsys.readouterr().out
    second = cli._one_live_snapshot(tmp_path, "diff", first, suppress_unchanged=True)
    assert second == first
    assert capsys.readouterr().out == ""
    cli._one_live_snapshot(tmp_path, "diff", second, suppress_unchanged=True)
    changed_output = capsys.readouterr().out
    assert '"id": "eo-router-a"' in changed_output
    assert '"changed"' in changed_output


def test_watch_loop_exits_cleanly_when_q_is_requested(tmp_path: Path, monkeypatch, capsys) -> None:
    class FakeContext:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(cli.NetconfClient, "connect_from_environment", lambda: FakeContext())
    monkeypatch.setattr(cli, "_one_live_snapshot", lambda *args, **kwargs: {})
    monkeypatch.setattr(cli, "_wait_for_interval", lambda interval: True)

    result = cli.main(["--watch", "--interval", "1", "--output", str(tmp_path)])
    output = capsys.readouterr().out
    assert result == 0
    assert "Press q to stop" in output
    assert "stopped by q" in output


def test_event_catalog_observation_issues_one_get_for_each_group_a_event(tmp_path: Path) -> None:
    client = FixtureClient()
    progress = []
    observations = observe_event_catalog(
        client,
        progress=lambda index, total, event: progress.append((index, total, event.event_id)),
    )
    events = load_event_catalog()
    assert len(events) == 122
    assert len(observations) == 122
    assert client.calls == 122
    assert len(progress) == 122
    assert progress[0] == (1, 122, "U1-0")
    assert progress[-1] == (122, 122, "U16-9")
    assert observations[0].event.event_id == "U1-0"
    assert observations[-1].event.event_id == "U16-9"
    assert "catalog reference only" in observations[0].correlation

    destination = tmp_path / "observation_catalog.md"
    write_observation_catalog(observations, destination)
    report = destination.read_text(encoding="utf-8")
    assert "U1-0" in report and "U16-4" in report
    assert "YANG-visible" in report and "controller-metadata-only" in report
    assert "GAP-" not in report
    assert "| gap" not in report.lower()


def test_one_shot_explains_catalog_labels_before_collection_progress(tmp_path: Path, capsys) -> None:
    result = cli._catalog_once(tmp_path / "logs", "summary", FIXTURE)
    lines = capsys.readouterr().out.splitlines()
    assert result == 0
    assert lines[0] == (
        "Event labels come from allrun5/docs/event_catalog.md; each snapshot is fetched via NETCONF <get>."
    )
    assert lines[1].startswith("[001/122] Collected UC 2.1 U1-0 LEGACY_BASELINE")


def test_snapshot_files_keep_raw_xml_and_normalized_json(tmp_path: Path) -> None:
    result = snapshot()
    store_snapshot(result, tmp_path)
    assert (tmp_path / "latest.xml").read_text(encoding="utf-8") == result.raw_xml
    stored = json.loads((tmp_path / "latest.json").read_text(encoding="utf-8"))
    assert stored["device"] == "fixture-router"
    assert stored["ietf-power-and-energy:energy-objects"]["energy-object"][0]["id"] == "eo-router-a"


def test_all_required_read_only_views_render() -> None:
    result = snapshot()
    data = {**result.normalized, "raw_xml": result.raw_xml}
    for view in ("summary", "inventory", "energy-objects", "relationships", "raw-json", "raw-xml", "diff"):
        assert render(data, view, snapshot_diff(None, result.normalized))


def test_missing_credentials_fail_clearly(monkeypatch) -> None:
    monkeypatch.setattr(netconf_client, "_connection_config_paths", lambda: ())
    for key in ("NETCONF_USERNAME", "NETCONF_PASSWORD"):
        monkeypatch.delenv(key, raising=False)
    try:
        NetconfClient.connect_from_environment()
    except NetconfUnavailable as error:
        assert "NETCONF_USERNAME" in str(error)
    else:
        raise AssertionError("missing credentials should prevent a live session")


def test_local_connection_file_is_used_by_default_and_environment_overrides(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "connection.env"
    config.write_text(
        "NETCONF_HOST=192.0.2.10\nNETCONF_PORT=830\nNETCONF_USERNAME=file-user\nNETCONF_PASSWORD=file-secret\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(netconf_client, "_connection_config_paths", lambda: (config,))
    for key in ("NETCONF_HOST", "NETCONF_PORT", "NETCONF_USERNAME", "NETCONF_PASSWORD", "NETCONF_DEVICE_ID"):
        monkeypatch.delenv(key, raising=False)

    calls = []

    class FakeSession:
        def close_session(self) -> None:
            pass

    def fake_connect_ssh(**kwargs):
        calls.append(kwargs)
        return FakeSession()

    from ncclient import manager

    monkeypatch.setattr(manager, "connect_ssh", fake_connect_ssh)
    client = NetconfClient.connect_from_environment()
    assert client.device == "192.0.2.10"
    assert calls[-1]["username"] == "file-user"
    assert calls[-1]["password"] == "file-secret"

    monkeypatch.setenv("NETCONF_HOST", "localhost")
    monkeypatch.setenv("NETCONF_USERNAME", "environment-user")
    client = NetconfClient.connect_from_environment()
    assert client.device == "localhost"
    assert calls[-1]["host"] == "localhost"
    assert calls[-1]["username"] == "environment-user"


def test_read_only_baseline_hashes_match_and_controller_adds_no_yang() -> None:
    repository = Path(__file__).resolve().parents[2]
    manifest = repository / "install" / "yang" / "yang-modules-manifest.txt"
    entries = [
        [part.strip() for part in line.split("|")]
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    assert len(entries) == 6
    for _, _, source_path, expected_hash, *_ in entries:
        source = repository / source_path
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash
    assert not list((repository / "ctrlrun6").rglob("*.yang"))
