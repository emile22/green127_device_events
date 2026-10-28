from green.models import Event


_PDU_EVENTS = (
    Event("TRAFFIC_HIGH", {"upstream-meter": 300, "server-A": 120, "server-B": 180}),
    Event("TRAFFIC_LOW", {"upstream-meter": 150, "server-A": 60, "server-B": 90}),
    Event("COMPONENT_SLEEP server-B", {"upstream-meter": 80, "server-A": 60, "server-B": 20}),
    Event("TRAFFIC_BURST", {"upstream-meter": 360, "server-A": 150, "server-B": 210}),
)


def generate_events(scenario: str = "pdu") -> tuple[Event, ...]:
    if scenario != "pdu":
        raise ValueError(f"unsupported scenario: {scenario}")
    return _PDU_EVENTS