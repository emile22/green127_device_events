from green.__main__ import main, run_demo
from green.simulator import generate_events


def run_with_commands(commands: list[str]) -> tuple[list[str], list[float]]:
    command_iterator = iter(commands)
    output: list[str] = []
    sleep_calls: list[float] = []

    run_demo(
        generate_events(),
        auto=False,
        interval=1.0,
        input_fn=lambda: next(command_iterator),
        sleep_fn=sleep_calls.append,
        output_fn=output.append,
    )
    return output, sleep_calls


def test_enter_runs_exactly_one_event_then_prompts_again() -> None:
    output, sleep_calls = run_with_commands(["", "q"])

    assert any("[T0] TRAFFIC_HIGH" in line for line in output)
    assert not any("[T1]" in line for line in output)
    assert sum("[ENTER] next event" in line for line in output) == 2
    assert sleep_calls == []


def test_a_runs_remaining_events_without_prompting_again() -> None:
    output, sleep_calls = run_with_commands(["", "a"])

    assert [line for line in output if line.startswith("[T")] == [
        "[T0] TRAFFIC_HIGH",
        "[T1] TRAFFIC_LOW",
        "[T2] COMPONENT_SLEEP server-B",
        "[T3] TRAFFIC_BURST",
    ]
    assert sum("[ENTER] next event" in line for line in output) == 2
    assert sleep_calls == [1.0, 1.0]


def test_q_stops_without_running_the_next_event() -> None:
    output, sleep_calls = run_with_commands(["q"])

    assert "GREEN demo stopped." in output
    assert not any(line.startswith("[T") for line in output)
    assert sleep_calls == []


def test_r_restarts_at_t0_and_returns_to_interactive_mode() -> None:
    output, sleep_calls = run_with_commands(["", "r", "", "q"])

    assert sum("[T0] TRAFFIC_HIGH" in line for line in output) == 2
    assert "GREEN scenario restarted at T0." in output
    assert sleep_calls == []


def test_auto_starts_without_reading_input() -> None:
    output: list[str] = []
    sleep_calls: list[float] = []

    def unexpected_input() -> str:
        raise AssertionError("automatic mode must not read input")

    main(
        ["--auto", "--interval", "0.5"],
        input_fn=unexpected_input,
        sleep_fn=sleep_calls.append,
        output_fn=output.append,
    )

    assert sum(line.startswith("[T") for line in output) == 4
    assert sleep_calls == [0.5, 0.5, 0.5]
    assert "T0  naive=600  accounted=300" in output
    assert "Topology:          complete" in output