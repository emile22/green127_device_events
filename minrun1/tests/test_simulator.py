from green.simulator import generate_events


def test_pdu_scenario_emits_deterministic_measurements() -> None:
    events = generate_events("pdu")

    assert [event.name for event in events] == [
        "TRAFFIC_HIGH",
        "TRAFFIC_LOW",
        "COMPONENT_SLEEP server-B",
        "TRAFFIC_BURST",
    ]
    assert events[0].measurements == {
        "upstream-meter": 300,
        "server-A": 120,
        "server-B": 180,
    }


def test_unknown_scenario_is_rejected() -> None:
    try:
        generate_events("unknown")
    except ValueError as error:
        assert "unsupported scenario" in str(error)
    else:
        raise AssertionError("unknown scenarios must be rejected")