from green.models import ComponentState, EventSeries, RelationshipType
from green.topology import SERVER_B_ID, UPSTREAM_METER_ID

from tests.uc.helpers import events_for


def test_fixed_network_values_cumulative_and_enablement_are_preserved():
    events = events_for(EventSeries.UC_2_10)
    assert len(events) == 8
    assert [event.name for event in events[:4]] == [
        "TRAFFIC_HIGH", "TRAFFIC_LOW", "COMPONENT_SLEEP", "TRAFFIC_BURST"
    ]
    meter = [next(m for m in event.measurements if m.energy_object_id == UPSTREAM_METER_ID) for event in events[:4]]
    assert [item.interval_energy_wh for item in meter] == [300, 150, 80, 360]
    assert [item.cumulative_energy_wh for item in meter] == [300, 450, 530, 890]
    assert dict(events[2].component_states)[SERVER_B_ID] is ComponentState.LOW_POWER
    assert dict(events[3].component_states)[SERVER_B_ID] is ComponentState.ACTIVE
    assert all(RelationshipType.ENABLING in {r.relationship_type for r in event.relationships} for event in events)