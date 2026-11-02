import pytest
from pathlib import Path

from green.__main__ import main, run_demo
from green.netconf_bridge import set_netconf_trace_enabled, write_operational_snapshot
from green.netconf_trace import format_netconf_trace_entry
from green.simulator import EventSimulator
import run
from run import pause_for_review


def run_with_commands(commands: list[str]):
    command_iterator = iter(commands)
    output: list[str] = []
    sleep_calls: list[float] = []

    run_demo(
        EventSimulator(),
        auto=False,
        interval=1.0,
        input_fn=lambda: next(command_iterator),
        sleep_fn=sleep_calls.append,
        output_fn=output.append,
    )
    return output, sleep_calls


def event_lines(output: list[str]) -> list[str]:
    return [line for line in output if line.startswith("[UC ")]


def test_enter_runs_exactly_one_event_then_prompts_again() -> None:
    output, sleep_calls = run_with_commands(["", "q"])

    assert event_lines(output) == ["[UC 2.13 / U13-0] RAW_MEASUREMENTS"]
    assert "Naive total:       600 Wh" in output
    assert "Accounted total:   unavailable" in output
    assert any("incomplete" in line for line in output), repr(output)
    assert sum("[ENTER] next event" in line for line in output) == 2
    assert sleep_calls == []


def test_dash_separator_precedes_every_event_header() -> None:
    output, _ = run_with_commands(["", "a"])
    event_positions = [index for index, line in enumerate(output) if line.startswith("[UC ")]

    assert len(event_positions) == 17
    assert all(output[index - 1] == "-" * 50 for index in event_positions)


def test_a_runs_remaining_events_without_prompting_again() -> None:
    output, sleep_calls = run_with_commands(["", "a"])

    assert event_lines(output) == [
        "[UC 2.13 / U13-0] RAW_MEASUREMENTS",
        "[UC 2.13 / U13-1] TOPOLOGY_DISCOVERED",
        "[UC 2.13 / U13-2] NEXT_MEASUREMENT_INTERVAL",
        "[UC 2.13 / U13-3] TOPOLOGY_INCOMPLETE",
        "[UC 2.10 / U10-0] TRAFFIC_HIGH",
        "[UC 2.10 / U10-1] TRAFFIC_LOW",
        "[UC 2.10 / U10-2] COMPONENT_SLEEP",
        "[UC 2.10 / U10-3] TRAFFIC_BURST",
        "[UC 2.1 / U1-0] LEGACY_BASELINE",
        "[UC 2.1 / U1-1] COMPONENT_GREEN_ENABLED",
        "[UC 2.1 / U1-2] DEVICE_GREEN_ENABLED",
        "[UC 2.1 / U1-3] NETWORK_MIXED_DEPLOYMENT",
        "[UC 2.14 / U14-0] GRID_NORMAL",
        "[UC 2.14 / U14-1] GRID_FAILURE",
        "[UC 2.14 / U14-2] BATTERY_OPERATION",
        "[UC 2.14 / U14-3] ENERGY_CRITICAL",
        "[UC 2.14 / U14-4] GRID_RESTORED",
    ]
    assert sum("[ENTER] next event" in line for line in output) == 2
    assert sleep_calls == [1.0] * 15
    assert "GREEN demo completed." in output
    assert "UC 2.13 Double Accounting completed" in output
    assert "UC 2.10 Fixed Network Energy Saving completed" in output
    assert "UC 2.1 Incremental GREEN Deployment completed" in output
    assert any("critical-service: active" in line for line in output)


def test_q_stops_without_running_the_next_event() -> None:
    output, sleep_calls = run_with_commands(["q"])

    assert "GREEN demo stopped." in output
    assert event_lines(output) == []
    assert sleep_calls == []


def test_d_toggles_netconf_trace_without_advancing_event() -> None:
    trace_states: list[bool] = []
    commands = iter(["d", "", "d", "q"])
    output: list[str] = []

    run_demo(
        EventSimulator(),
        auto=False,
        interval=1.0,
        input_fn=lambda: next(commands),
        sleep_fn=lambda _: None,
        output_fn=output.append,
        snapshot_fn=None,
        trace_fn=lambda enabled: trace_states.append(enabled) or Path("trace.log"),
    )

    assert trace_states == [True, False]
    assert event_lines(output) == ["[UC 2.13 / U13-0] RAW_MEASUREMENTS"]
    assert any("NETCONF message trace enabled" in line for line in output)
    assert any("NETCONF message trace disabled" in line for line in output)


def test_netconf_trace_toggle_uses_provider_control_path(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "operational.json"
    control_path = Path(f"{snapshot_path}.netconf-trace-enabled")

    trace_path = set_netconf_trace_enabled(True, snapshot_path)
    assert trace_path == Path(f"{snapshot_path}.netconf-trace.log")
    assert control_path.read_text(encoding="ascii") == "1\n"

    set_netconf_trace_enabled(False, snapshot_path)
    assert control_path.read_text(encoding="ascii") == "0\n"


def test_netconf_trace_formatter_displays_readable_reply() -> None:
    entry = """[2026-10-30T09:33:00Z] NETCONF operational-data request
------------------------------------------------------------------------
UC 2.13 - Double Accounting | U13-1 TOPOLOGY_DISCOVERED
------------------------------------------------------------------------
operation: <get>
module: ietf-power-and-energy
path: /ietf-power-and-energy:energy-objects
request-xpath: /ietf-power-and-energy:*
status: ok
reply-data-json:
{"example:payload":{"id":"eo-upstream-meter"}}
"""

    formatted = format_netconf_trace_entry(entry)

    assert "NETCONF TRACE" in formatted
    assert "UC 2.13 - Double Accounting | U13-1 TOPOLOGY_DISCOVERED" in formatted
    assert "<get> | OK | 2026-10-30T09:33:00Z" in formatted
    assert "Filter: /ietf-power-and-energy:*" in formatted
    assert '"id": "eo-upstream-meter"' in formatted
    assert all(len(line) <= 72 for line in formatted.splitlines())
    assert formatted.isascii()


def test_netconf_trace_renders_hardware_reply_as_inventory() -> None:
    entry = """[2026-10-30T09:33:00Z] NETCONF operational-data request
------------------------------------------------------------------------
UC 2.13 - Double Accounting | U13-1 TOPOLOGY_DISCOVERED
------------------------------------------------------------------------
operation: <get>
module: ietf-hardware
path: /ietf-hardware:hardware
request-xpath: /ietf-hardware:hardware
status: ok
reply-data-json:
{"ietf-hardware:hardware":{"component":[{"name":"upstream-meter","class":"iana-hardware:energy-object","uuid":"00000000-0000-4000-8000-000000000001"},{"name":"server-A","class":"iana-hardware:energy-object","uuid":"00000000-0000-4000-8000-000000000002"},{"name":"server-B","class":"iana-hardware:energy-object","uuid":"00000000-0000-4000-8000-000000000003"}]}}
"""

    formatted = format_netconf_trace_entry(entry)

    assert "Reply: HARDWARE INVENTORY" in formatted
    assert "Component" in formatted and "Class" in formatted and "UUID" in formatted
    assert "upstream-meter" in formatted and "energy-object" in formatted
    assert "...0001" in formatted and "...0002" in formatted and "...0003" in formatted
    assert "Reply / JSON:" not in formatted
    assert all(len(line) <= 72 for line in formatted.splitlines())


def test_netconf_trace_renders_energy_objects_as_inventory() -> None:
    entry = """[2026-10-30T09:33:00Z] NETCONF operational-data request
------------------------------------------------------------------------
UC 2.13 - Double Accounting | U13-1 TOPOLOGY_DISCOVERED
------------------------------------------------------------------------
operation: <get>
module: ietf-power-and-energy
path: /ietf-power-and-energy:energy-objects
request-xpath: /ietf-power-and-energy:*
status: ok
reply-data-json:
{"ietf-power-and-energy:energy-objects":{"energy-object":[{"id":"eo-upstream-meter","source-component-id":"upstream-meter","relationship":[{"type":"ietf-power-and-energy:metering","peer":[{"id":"eo-server-a"},{"id":"eo-server-b"}]}]},{"id":"eo-server-a","source-component-id":"server-A","power":{"instantaneous-power":"120000"},"power-state":{"oper":"ietf-power-and-energy:power-state-on"}},{"id":"eo-server-b","source-component-id":"server-B","power":{"instantaneous-power":"90000"},"power-state":{"oper":"ietf-power-and-energy:power-state-sleep"}}]}}
"""

    formatted = format_netconf_trace_entry(entry)

    assert "GREEN ENERGY OBJECTS" in formatted
    assert "Energy Object" in formatted and "Source component" in formatted
    assert "Power" in formatted and "State" in formatted and "Relationships" in formatted
    assert "eo-upstream-meter" in formatted and "upstream-meter" in formatted
    assert "METERING(2)" in formatted
    assert "eo-server-a" in formatted and "120000" in formatted and "ON" in formatted
    assert "eo-server-b" in formatted and "90000" in formatted and "SLEEP" in formatted
    assert "Reply / JSON:" not in formatted
    assert all(len(line) <= 72 for line in formatted.splitlines())


def test_d_mode_logs_and_prettifies_runtime_snapshots_for_all_use_cases(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "operational.json"
    commands = iter(["d", "", "a"])
    output: list[str] = []

    run_demo(
        EventSimulator(),
        auto=False,
        interval=0,
        input_fn=lambda: next(commands),
        sleep_fn=lambda _: None,
        output_fn=output.append,
        snapshot_fn=lambda event: write_operational_snapshot(event, snapshot_path),
        trace_fn=lambda enabled: set_netconf_trace_enabled(enabled, snapshot_path),
    )

    trace = Path(f"{snapshot_path}.netconf-trace.log").read_text(encoding="utf-8")
    for uc_title in (
        "UC 2.13 - Double Accounting",
        "UC 2.10 - Fixed Network Energy Saving",
        "UC 2.1 - Incremental GREEN Deployment",
        "UC 2.14 - Power Shortage / Resilience",
    ):
        assert uc_title in trace
        assert any(uc_title in line for line in output)
    assert trace.count("operation: runtime snapshot") == 17
    assert any("runtime snapshot" in line and "UC 2.13" in line for line in output)
    assert any("GREEN ENERGY OBJECTS" in line for line in output)
    assert any("Reply: HARDWARE INVENTORY" in line for line in output)
    combined_snapshot = next(
        line for line in output if "runtime snapshot" in line and "UC 2.13" in line
    )
    assert combined_snapshot.index("Reply: HARDWARE INVENTORY") < combined_snapshot.index(
        "GREEN ENERGY OBJECTS"
    )


def test_r_restarts_complete_demo_and_resets_uc_2_10_counters() -> None:
    commands = [""] * 6 + ["r"] + [""] * 5 + ["q"]
    output, sleep_calls = run_with_commands(commands)
    cumulative_sections = [
        output[index + 1:index + 4]
        for index, line in enumerate(output)
        if line == "Cumulative energy:"
    ]

    assert event_lines(output).count("[UC 2.13 / U13-0] RAW_MEASUREMENTS") == 2
    assert event_lines(output).count("[UC 2.10 / U10-0] TRAFFIC_HIGH") == 2
    assert cumulative_sections[0] == cumulative_sections[2]
    assert cumulative_sections[0][0].strip().endswith("300 Wh")
    assert "GREEN demo restarted at UC 2.13 / U13-0." in output
    assert sleep_calls == []


def test_auto_starts_without_input_or_real_sleep() -> None:
    output: list[str] = []
    sleep_calls: list[float] = []

    def unexpected_input() -> str:
        raise AssertionError("automatic mode must not request input")

    snapshots = []
    trace_states: list[bool] = []

    main(
        ["--auto", "--interval", "0.25"],
        input_fn=unexpected_input,
        sleep_fn=sleep_calls.append,
        output_fn=output.append,
        snapshot_fn=snapshots.append,
        trace_fn=lambda enabled: trace_states.append(enabled) or Path("trace.log"),
    )

    assert len(event_lines(output)) == 17
    assert sleep_calls == [0.25] * 16
    assert len(snapshots) == 17
    assert snapshots[-1].sequence == "U14-4"
    assert trace_states == [False]
    assert "[UC 2.13 / U13-0] RAW_MEASUREMENTS" in event_lines(output)
    assert "[UC 2.10 / U10-3] TRAFFIC_BURST" in event_lines(output)
    assert "GREEN demo completed." in output


def test_negative_interval_is_rejected() -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["--interval", "-1"],
            input_fn=lambda: "",
            snapshot_fn=lambda event: None,
        )

    assert error.value.code == 2


def test_review_pause_uses_injected_input() -> None:
    prompts: list[str] = []

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return ""

    pause_for_review("Press ENTER to close", fake_input)

    assert prompts == ["Press ENTER to close"]


def test_launcher_prefers_project_virtualenv(tmp_path: Path, monkeypatch) -> None:
    environment_dir = tmp_path / ".venv"
    local_python = environment_dir / (
        Path("Scripts") / "python.exe" if run.os.name == "nt" else Path("bin") / "python"
    )
    local_python.parent.mkdir(parents=True)
    local_python.touch()
    monkeypatch.setattr(run, "__file__", str(tmp_path / "run.py"))

    assert run.project_python() == str(local_python)


@pytest.mark.parametrize(
    ("test_returncode", "runtime_returncode", "expected_returncode"),
    [(0, 0, 0), (0, 3, 3), (2, None, 2)],
)
def test_launcher_stops_netconf_services_on_exit(
    monkeypatch,
    test_returncode: int,
    runtime_returncode: int | None,
    expected_returncode: int,
) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        commands.append(command)
        if "pytest" in command:
            return type("Result", (), {"returncode": test_returncode})()
        if "green" in command:
            return type("Result", (), {"returncode": runtime_returncode})()
        return type("Result", (), {"returncode": 0, "stdout": "stopped", "stderr": ""})()

    monkeypatch.setattr(run, "project_python", lambda: "project-python")
    monkeypatch.setattr(run, "ensure_netconf_services", lambda: True)
    monkeypatch.setattr(run.subprocess, "run", fake_run)
    monkeypatch.setattr(run, "pause_for_review", lambda *_args: None)

    assert run.main([]) == expected_returncode
    assert commands[-1][0] == "wsl.exe"
    assert "scripts/wsl-netconf-stop.sh" in commands[-1][-1]
    assert commands.count(["project-python", "-m", "green"]) == int(test_returncode == 0)


def test_launcher_passes_auto_interval_to_runtime(tmp_path: Path, monkeypatch) -> None:
    commands: list[list[str]] = []
    working_directories: list[Path | None] = []

    def fake_run(command: list[str], **kwargs):
        commands.append(command)
        working_directories.append(kwargs.get("cwd"))
        if "pytest" in command:
            return type("Result", (), {"returncode": 0})()
        return type("Result", (), {"returncode": 0, "stdout": "stopped", "stderr": ""})()

    project_dir = tmp_path / "minrun4"
    project_dir.mkdir()
    monkeypatch.setattr(run, "__file__", str(project_dir / "run.py"))
    monkeypatch.setattr(run, "project_python", lambda: "project-python")
    monkeypatch.setattr(run, "ensure_netconf_services", lambda: True)
    monkeypatch.setattr(run.subprocess, "run", fake_run)
    monkeypatch.setattr(run, "pause_for_review", lambda *_args: None)

    assert run.main(["--auto", "--interval", "0"]) == 0
    assert commands[1] == ["project-python", "-m", "green", "--auto", "--interval", "0.0"]
    assert working_directories[:2] == [project_dir, project_dir]


def test_ensure_netconf_services_starts_stack_when_health_check_fails(monkeypatch, capsys) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        commands.append(command)
        if "systemctl show-environment" in command[-1]:
            return type("Result", (), {"returncode": 1, "stdout": "", "stderr": ""})()
        if "systemctl show" in command[-1]:
            return type("Result", (), {"returncode": 0, "stdout": "321\n654\n", "stderr": ""})()
        return type("Result", (), {"returncode": 0, "stdout": "Netopeer2 is listening", "stderr": ""})()

    monkeypatch.setattr(run.subprocess, "run", fake_run)

    assert run.ensure_netconf_services()
    assert len(commands) == 3
    assert "systemctl is-active" in commands[0][-1]
    wsl_project = run._wsl_project_path(Path(run.__file__).resolve().parent)
    assert f"SRPD_PLUGINS_PATH={wsl_project}/netconf/plugins" in commands[0][-1]
    assert f"GREEN_NETCONF_STATE_FILE={wsl_project}/state/netconf/operational.json" in commands[0][-1]
    assert "scripts/wsl-netconf-start.sh" in commands[1][-1]
    output = capsys.readouterr().out
    assert "WSL NETCONF ready (Netopeer2 TCP/830)." in output
    assert "WSL service PIDs: sysrepo-plugind=321, netopeer2=654." in output
    assert "eo-router-a/router-A" in output
    assert "eo-router-a-linecard-1/linecard-1 (pos 1)" in output
    assert "eo-router-a-linecard-2" in output
    assert "pos 2" in output
    assert "[siblings]" in output
    assert all(len(line) <= 88 for line in output.splitlines())


def test_launcher_stops_without_running_tests_when_service_start_fails(monkeypatch) -> None:
    stop_calls: list[bool] = []

    def unexpected_run(*_args, **_kwargs):
        raise AssertionError("pytest/runtime must not run when NETCONF startup fails")

    monkeypatch.setattr(run, "ensure_netconf_services", lambda: False)
    monkeypatch.setattr(run, "stop_netconf_services", lambda: stop_calls.append(True))
    monkeypatch.setattr(run.subprocess, "run", unexpected_run)

    assert run.main([]) == 1
    assert stop_calls == [True]