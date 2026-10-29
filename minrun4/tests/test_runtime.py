import pytest

from green.__main__ import main, run_demo
from green.simulator import EventSimulator
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

    main(
        ["--auto", "--interval", "0.25"],
        input_fn=unexpected_input,
        sleep_fn=sleep_calls.append,
        output_fn=output.append,
        snapshot_fn=snapshots.append,
    )

    assert len(event_lines(output)) == 17
    assert sleep_calls == [0.25] * 16
    assert len(snapshots) == 17
    assert snapshots[-1].sequence == "U14-4"
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