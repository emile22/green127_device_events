from green.accounting import AccountingEngine
from green.simulator import generate_events
from green.topology import Topology


def test_demo_accounting_uses_upstream_boundary() -> None:
    topology = Topology("upstream-meter", ("server-A", "server-B"))
    engine = AccountingEngine()
    expected = ((600, 300), (300, 150), (160, 80), (720, 360))

    results = [
        engine.compute(topology.upstream_meter, event.measurements, topology)
        for event in generate_events()
    ]

    assert [(result.naive_total_wh, result.accounted_total_wh) for result in results] == list(expected)
    assert all(result.topology_complete for result in results)