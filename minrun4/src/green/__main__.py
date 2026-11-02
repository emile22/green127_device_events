import argparse
import time
from collections.abc import Callable, Sequence
from pathlib import Path

from green.accounting import AccountingEngine
from green.models import AccountingResult, EventSeries, SimulatedEvent
from green.netconf_bridge import set_netconf_trace_enabled, write_operational_snapshot
from green.netconf_trace import NetconfTraceTailer
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
    snapshot_fn: Callable[[SimulatedEvent], None] | None = None,
    trace_fn: Callable[[bool], Path] | None = None,
) -> None:
    accounting = AccountingEngine()
    set_trace = trace_fn or set_netconf_trace_enabled
    trace_enabled = False
    trace_tailer: NetconfTraceTailer | None = None
    output_fn("GREEN demo starting...")

    def disable_trace() -> None:
        nonlocal trace_enabled, trace_tailer
        if not trace_enabled:
            return
        try:
            set_trace(False)
        except OSError as error:
            output_fn(f"NETCONF trace could not be disabled: {error}")
        trace_enabled = False
        if trace_tailer is not None:
            trace_tailer.stop()
            trace_tailer = None

    while simulator.has_next:
        next_event = simulator.peek_next()
        series_start = {
            "U13-0": ("SERIES 1 — UC 2.13 Double Accounting", EventSeries.UC_2_13),
            "U10-0": ("SERIES 2 — UC 2.10 Fixed Network Energy Saving", EventSeries.UC_2_10),
            "U1-0": ("SERIES 3 — UC 2.1 Incremental GREEN Deployment", EventSeries.UC_2_1),
            "U14-0": ("SERIES 4 — UC 2.14 Power Shortage / Resilience", EventSeries.UC_2_14),
        }
        if next_event is not None and next_event.sequence in series_start:
            title, _ = series_start[next_event.sequence]
            output_fn("==================================================")
            output_fn(title)
            output_fn("==================================================")

        if not auto:
            output_fn(
                "[ENTER] next event\n"
                "a       automatically run all remaining events\n"
                "d       toggle NETCONF message trace\n"
                "q       quit\n"
                "r       restart scenario"
            )
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
                    output_fn(f"NETCONF message trace enabled (live view): {trace_path}")
                else:
                    if trace_tailer is not None:
                        trace_tailer.stop()
                        trace_tailer = None
                    output_fn(f"NETCONF message trace disabled: {trace_path}")
                continue
            if command == "q":
                disable_trace()
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

        if snapshot_fn is not None:
            try:
                snapshot_fn(event)
            except OSError as error:
                output_fn(f"NETCONF snapshot warning: {error}")

        topology, boundary = build_demo_topology(relationships=event.metering_relationships)
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
        _display_event(event, result, topology, output_fn)

        next_series = {
            "U13-3": ("UC 2.13 Double Accounting", "UC 2.10 Fixed Network Energy Saving"),
            "U10-3": ("UC 2.10 Fixed Network Energy Saving", "UC 2.1 Incremental GREEN Deployment"),
            "U1-3": ("UC 2.1 Incremental GREEN Deployment", "UC 2.14 Power Shortage / Resilience"),
        }
        if event.sequence in next_series:
            completed, following = next_series[event.sequence]
            output_fn("==================================================")
            output_fn(f"{completed} completed")
            output_fn(f"Starting {following}")
            output_fn("==================================================")

        if auto and simulator.has_next:
            sleep_fn(interval)

    disable_trace()
    output_fn("GREEN demo completed.")


def _display_event(
    event: SimulatedEvent,
    result: AccountingResult | None,
    topology: RelationshipGraph,
    output_fn: Callable[[str], None],
) -> None:
    output_fn("-" * 50)
    output_fn(f"[{event.series.value} / {event.sequence}] {event.name}")
    output_fn(event.explanation)
    if event.component_states:
        output_fn("State:")
        for object_id, state in event.component_states:
            energy_object = topology.objects_by_id.get(object_id)
            component = energy_object.hardware_component_name if energy_object else None
            output_fn(f"  {component or object_id:<22}{state.value}")

    if event.measurements:
        output_fn("Interval energy:")
        for measurement in event.measurements:
            energy_object = topology.objects_by_id.get(measurement.energy_object_id)
            component = energy_object.hardware_component_name if energy_object else None
            output_fn(f"  {component or measurement.energy_object_id:<22}{measurement.interval_energy_wh:>5} Wh")

    if any(measurement.cumulative_energy_wh is not None for measurement in event.measurements):
        output_fn("Cumulative energy:")
        for measurement in event.measurements:
            energy_object = topology.objects_by_id.get(measurement.energy_object_id)
            component = energy_object.hardware_component_name if energy_object else None
            cumulative = measurement.cumulative_energy_wh
            output_fn(f"  {component or measurement.energy_object_id:<22}{cumulative:>5} Wh")

    if event.power_measurements:
        output_fn("Instantaneous power:")
        for measurement in event.power_measurements:
            energy_object = topology.objects_by_id.get(measurement.energy_object_id)
            component = energy_object.hardware_component_name if energy_object else None
            output_fn(f"  {component or measurement.energy_object_id:<22}{measurement.instantaneous_power_w:>5} W")

    if event.metadata:
        output_fn("Scenario metadata:")
        for key, value in event.metadata:
            output_fn(f"  {key}: {value}")

    if result is None:
        output_fn("Accounting:       not applicable for this use-case event")
    else:
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
    snapshot_fn: Callable[[SimulatedEvent], None] | None = write_operational_snapshot,
    trace_fn: Callable[[bool], Path] | None = None,
) -> None:
    parser = argparse.ArgumentParser(description="Run the GREEN energy demo")
    parser.add_argument("--auto", action="store_true", help="run all events without prompting")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--scenario", choices=("pdu",), default="pdu")
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
    )


if __name__ == "__main__":
    main()