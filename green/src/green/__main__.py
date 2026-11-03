import argparse
import time
from collections.abc import Callable, Sequence

from green.accounting import AccountingEngine
from green.models import Event
from green.simulator import generate_events
from green.topology import Topology


def run_demo(
    events: Sequence[Event],
    *,
    auto: bool,
    interval: float,
    input_fn: Callable[[], str],
    sleep_fn: Callable[[float], None],
    output_fn: Callable[[str], None],
) -> None:
    topology = Topology("upstream-meter", ("server-A", "server-B"))
    accounting = AccountingEngine()
    index = 0
    automatic = auto

    output_fn("GREEN demo starting...")
    while index < len(events):
        if not automatic:
            output_fn(
                "[ENTER] next event\n"
                "a       automatically run all remaining events\n"
                "q       quit\n"
                "r       restart scenario"
            )
            command = input_fn().strip().lower()
            if command == "a":
                automatic = True
                continue
            if command == "q":
                output_fn("GREEN demo stopped.")
                return
            if command == "r":
                index = 0
                output_fn("GREEN scenario restarted at T0.")
                continue
            if command:
                output_fn("Unknown command. Choose ENTER, a, q, or r.")
                continue

        event = events[index]
        time_id = f"T{index}"
        result = accounting.compute(topology.upstream_meter, event.measurements, topology)

        output_fn(f"[{time_id}] {event.name}")
        output_fn("Raw:")
        for node in topology.nodes:
            output_fn(f"  {node:<16}{event.measurements[node]:>4} Wh")
        output_fn(f"{time_id}  naive={result.naive_total_wh}  accounted={result.accounted_total_wh}")
        output_fn(f"Topology:          {'complete' if result.topology_complete else 'incomplete'}")

        index += 1
        if automatic and index < len(events):
            sleep_fn(interval)

    output_fn("GREEN demo completed.")


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[], str] = input,
    sleep_fn: Callable[[float], None] = time.sleep,
    output_fn: Callable[[str], None] = print,
) -> None:
    parser = argparse.ArgumentParser(description="Run the GREEN energy demo")
    parser.add_argument("--auto", action="store_true", help="run all events without prompting")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--scenario", choices=("pdu",), default="pdu")
    args = parser.parse_args(argv)
    if args.interval < 0:
        parser.error("--interval must be non-negative")

    run_demo(
        generate_events(args.scenario),
        auto=args.auto,
        interval=args.interval,
        input_fn=input_fn,
        sleep_fn=sleep_fn,
        output_fn=output_fn,
    )


if __name__ == "__main__":
    main()