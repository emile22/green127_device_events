import json

from green.cli import run_demo
from green.simulator import EventSimulator


def test_full_stream_json_filters_to_current_use_case_topology() -> None:
    commands = iter(["", "json", "q"])
    output: list[str] = []
    simulator = EventSimulator()

    run_demo(
        simulator,
        auto=False,
        interval=0,
        input_fn=lambda: next(commands),
        sleep_fn=lambda _: None,
        output_fn=output.append,
        snapshot_fn=None,
    )

    json_output = next(item for item in output if item.startswith("{"))
    data = json.loads(json_output)
    actual_ids = {
        item["id"]
        for item in data["ietf-power-and-energy:energy-objects"]["energy-object"]
    }

    event = EventSimulator().next_event()
    assert event is not None
    scenario = simulator.network.scenarios_by_uc[event.series.value]
    selected_topologies = set(scenario.topology_ids)
    expected_ids = {
        energy_object_id
        for topology in simulator.network.topologies
        if topology.topology_id in selected_topologies
        for energy_object_id in topology.energy_object_ids
    }
    assert actual_ids == expected_ids
