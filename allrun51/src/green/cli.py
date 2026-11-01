import argparse
import time
from collections.abc import Callable, Sequence
from pathlib import Path

from green.accounting import AccountingEngine
from green.catalog import UC_CATALOG, USE_CASES_BY_SERIES
from green.models import AccountingResult, EventSeries, SimulatedEvent
from green.netconf_bridge import set_netconf_trace_enabled, write_operational_snapshot
from green.netconf_trace import NetconfTraceTailer
from green.simulator import EventSimulator
from green.topology import RelationshipGraph, build_demo_topology
from green.views import (
    event_to_yang,
    fetch_netconf_xml,
    render_json,
    render_compact_event,
    render_relationship_diff,
    render_relationships,
    render_summary,
)

_VIEW_COMMANDS = {"summary", "relationships", "json", "xml", "diff"}


def run_demo(
    simulator: EventSimulator,
    *,
    auto: bool,
    interval: float,
    input_fn: Callable[[], str],
    sleep_fn: Callable[[float], None],
    output_fn: Callable[[str], None],
    snapshot_fn: Callable[[SimulatedEvent], None] | None = None,
    trace_fn: Callable[[bool], Path] | None = None,
    xml_fn: Callable[[], str] | None = None,
) -> None:
    accounting = AccountingEngine()
    set_trace = trace_fn or set_netconf_trace_enabled
    read_xml = xml_fn or fetch_netconf_xml
    trace_enabled = False
    trace_tailer: NetconfTraceTailer | None = None
    current_event: SimulatedEvent | None = None
    previous_event: SimulatedEvent | None = None
    current_data: dict[str, object] | None = None
    output_fn("GREEN allrun51 demo starting...")

    def disable_trace() -> None:
        nonlocal trace_enabled, trace_tailer
        if not trace_enabled:
            return
        try:
            trace_path = set_trace(False)
        except OSError as error:
            output_fn(f"NETCONF trace could not be disabled: {error}")
        else:
            output_fn(f"NETCONF trace disabled: {trace_path}")
        trace_enabled = False
        if trace_tailer is not None:
            trace_tailer.stop()
            trace_tailer = None

    def show_view(command: str) -> None:
        if command == "xml":
            try:
                output_fn(read_xml())
            except Exception as error:
                output_fn(f"NETCONF XML view unavailable: {error}")
            return
        if current_event is None or current_data is None:
            output_fn(f"{command} view unavailable before the first event.")
            return
        if command == "summary":
            output_fn(render_summary(current_event, current_data))
        elif command == "relationships":
            output_fn(render_relationships(current_data))
        elif command == "json":
            output_fn(render_json(current_data))
        elif command == "diff":
            output_fn(render_relationship_diff(previous_event, current_event))

    while simulator.has_next:
        next_spec = simulator.peek_next()
        if next_spec is None:
            break
        next_series = next_spec.series
    # Print a separator at each use-case boundary.
        if current_event is None or current_event.series != next_series:
            output_fn(f"--- {next_series.value} {USE_CASES_BY_SERIES[next_series].title} ---")

        if not auto:
            output_fn("Enter next | a auto | d netconf | summary / relationships / json / xml / diff | r restart | q quit")
            command = input_fn().strip().lower()
            if command == "a":
                auto = True
                output_fn("Automatic mode enabled.")
                continue
            if command == "d":
                next_trace_state = not trace_enabled
                try:
                    trace_path = set_trace(next_trace_state)
                except OSError as error:
                    output_fn(f"NETCONF trace could not be updated: {error}")
                    continue
                trace_enabled = next_trace_state
                if trace_enabled:
                    trace_tailer = NetconfTraceTailer(trace_path, output_fn)
                    trace_tailer.start()
                    output_fn(f"NETCONF trace enabled (live view): {trace_path}")
                else:
                    if trace_tailer is not None:
                        trace_tailer.stop()
                        trace_tailer = None
                    output_fn(f"NETCONF trace disabled: {trace_path}")
                continue
            if command == "q":
                disable_trace()
                output_fn("GREEN allrun51 demo stopped.")
                return
            if command == "r":
                simulator.reset()
                current_event = None
                previous_event = None
                current_data = None
                output_fn("All Group A state reset to UC 2.1 / U1-0.")
                continue
            if command in _VIEW_COMMANDS:
                show_view(command)
                continue
            if command:
                output_fn("Unknown command. Choose ENTER, a, d, summary, relationships, json, xml, diff, r, or q.")
                continue

        event = simulator.next_event()
        if event is None:
            break
        if snapshot_fn is not None:
            try:
                snapshot_fn(event)
            except OSError as error:
                output_fn(f"NETCONF snapshot warning: {error}")

        topology, boundary = build_demo_topology(relationships=event.relationships)
        result = None
        if event.series in (EventSeries.UC_2_13, EventSeries.UC_2_10):
            result = accounting.compute(
                boundary,
                event.measurements,
                topology,
                series=event.series.value,
                event_sequence=event.sequence,
                event_name=event.name,
            )
        data = event_to_yang(event, simulator.energy_objects)
        prior_event = current_event
        previous_event, current_event = current_event, event
        current_data = data
        _display_event(event, result, topology, output_fn, prior_event)

        next_spec = simulator.peek_next()
        if next_spec is None:
            output_fn(f"{event.series.value} complete")
        elif next_spec.series != event.series:
            output_fn(f"{event.series.value} complete -> {next_spec.series.value} {USE_CASES_BY_SERIES[next_spec.series].title}")

        if auto and simulator.has_next:
            sleep_fn(interval)

    disable_trace()
    output_fn("Group A completed: 14 use cases")
    output_fn("Group B deferred: 2 use cases")


def _display_event(
    event: SimulatedEvent,
    result: AccountingResult | None,
    topology: RelationshipGraph,
    output_fn: Callable[[str], None],
    previous: SimulatedEvent | None,
) -> None:
    for line in render_compact_event(event, topology.energy_objects, previous, result).splitlines():
        output_fn(line)


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[], str] = input,
    sleep_fn: Callable[[float], None] = time.sleep,
    output_fn: Callable[[str], None] = print,
    snapshot_fn: Callable[[SimulatedEvent], None] | None = write_operational_snapshot,
    trace_fn: Callable[[bool], Path] | None = None,
    xml_fn: Callable[[], str] | None = None,
) -> None:
    parser = argparse.ArgumentParser(description="Run the GREEN allrun51 event simulator")
    parser.add_argument("--auto", action="store_true", help="run all remaining events without prompts")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args(argv)
    if args.interval < 0:
        parser.error("--interval must be non-negative")

    set_trace = trace_fn or set_netconf_trace_enabled
    try:
        set_trace(False)
    except OSError as error:
        output_fn(f"NETCONF trace could not be reset: {error}")
    run_demo(
        EventSimulator(),
        auto=args.auto,
        interval=args.interval,
        input_fn=input_fn,
        sleep_fn=sleep_fn,
        output_fn=output_fn,
        snapshot_fn=snapshot_fn,
        trace_fn=set_trace,
        xml_fn=xml_fn,
    )


if __name__ == "__main__":
    main()
