import argparse
import time
from collections.abc import Callable, Sequence

from green.accounting import AccountingEngine
from green.models import AccountingResult, SimulatedEvent
from green.simulator import EventSimulator
from green.topology import RelationshipGraph, build_demo_topology


def run_demo(
    simulator: EventSimulator,
    *,
    auto: bool,
    interval: float,
    input_fn: Callable[[], str],
    sleep_fn: Callable[[float], None],
    output_fn: Callable[[str], None],
) -> None:
    accounting = AccountingEngine()
    output_fn("GREEN demo starting...")

    while simulator.has_next:
        next_event = simulator.peek_next()
        if next_event is not None and next_event.sequence == "U13-0":
            output_fn("--- SERIES 1: UC 2.13 Double Accounting ---")
        elif next_event is not None and next_event.sequence == "U10-0":
            output_fn("--- SERIES 2: UC 2.10 Fixed Network Energy Saving ---")

        if not auto:
            output_fn(
                "[ENTER] next event\n"
                "a       automatically run all remaining events\n"
                "q       quit\n"
                "r       restart scenario"
            )
            command = input_fn().strip().lower()
            if command == "a":
                auto = True
                output_fn("Automatic mode enabled.")
                continue
            if command == "q":
                output_fn("GREEN demo stopped.")
                return
            if command == "r":
                simulator.reset()
                output_fn("GREEN demo restarted at UC 2.13 / U13-0.")
                continue
            if command:
                output_fn("Unknown command. Choose ENTER, a, q, or r.")
                continue

        event = simulator.next_event()
        if event is None:
            break
        topology, boundary = build_demo_topology(relationships=event.metering_relationships)
        result = accounting.compute(
            boundary,
            event.measurements,
            topology,
            series=event.series.value,
            event_sequence=event.sequence,
            event_name=event.name,
        )
        _display_event(event, result, topology, output_fn)

        if event.sequence == "U13-3":
            output_fn("==================================================")
            output_fn("UC 2.13 series completed")
            output_fn("Starting UC 2.10 — Fixed Network Energy Saving")
            output_fn("==================================================")

        if auto and simulator.has_next:
            sleep_fn(interval)

    output_fn("GREEN demo completed.")


def _display_event(
    event: SimulatedEvent,
    result: AccountingResult,
    topology: RelationshipGraph,
    output_fn: Callable[[str], None],
) -> None:
    output_fn(f"[{event.series.value} / {event.sequence}] {event.name}")
    output_fn("State:")
    for object_id, state in event.component_states:
        energy_object = topology.objects_by_id.get(object_id)
        component = energy_object.hardware_component_name if energy_object else None
        output_fn(f"  {component or object_id:<16}{state.value}")

    output_fn("Interval energy:")
    for measurement in event.measurements:
        energy_object = topology.objects_by_id.get(measurement.energy_object_id)
        component = energy_object.hardware_component_name if energy_object else None
        output_fn(f"  {component or measurement.energy_object_id:<16}{measurement.interval_energy_wh:>5} Wh")

    if any(measurement.cumulative_energy_wh is not None for measurement in event.measurements):
        output_fn("Cumulative energy:")
        for measurement in event.measurements:
            energy_object = topology.objects_by_id.get(measurement.energy_object_id)
            component = energy_object.hardware_component_name if energy_object else None
            cumulative = measurement.cumulative_energy_wh
            output_fn(f"  {component or measurement.energy_object_id:<16}{cumulative:>5} Wh")

    output_fn(f"Naive total:       {result.naive_total_wh} Wh")
    if result.accounted_total_wh is None:
        output_fn("Accounted total:   unavailable")
    else:
        output_fn(f"Accounted total:   {result.accounted_total_wh} Wh")
    output_fn(f"Topology:          {result.topology_status.value}")

    for exclusion in result.excluded_measurements:
        energy_object = topology.objects_by_id.get(exclusion.measurement.energy_object_id)
        component = energy_object.hardware_component_name if energy_object else None
        output_fn(f"Excluded {component or exclusion.measurement.energy_object_id}: {exclusion.reason}")
    for warning in result.warnings:
        output_fn(f"Warning: {warning}")
    for error in result.errors:
        output_fn(f"Topology error: {error}")


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
        EventSimulator(),
        auto=args.auto,
        interval=args.interval,
        input_fn=input_fn,
        sleep_fn=sleep_fn,
        output_fn=output_fn,
    )


if __name__ == "__main__":
    main()