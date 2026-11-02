from collections import defaultdict, deque
from collections.abc import Iterable, Sequence

from green.models import (
    AccountingBoundary,
    EnergyObject,
    EnergyRelationship,
    RelationshipType,
)


UPSTREAM_METER_ID = "eo-upstream-meter"
SERVER_A_ID = "eo-server-a"
SERVER_B_ID = "eo-server-b"
ROUTER_A_ID = "eo-router-a"
ROUTER_B_ID = "eo-router-b"
LINECARD_1_ID = "eo-router-a-linecard-1"
LINECARD_2_ID = "eo-router-a-linecard-2"
NON_CRITICAL_PORT_ID = "eo-router-b-non-critical-port"


class RelationshipGraph:
    def __init__(
        self,
        energy_objects: Iterable[EnergyObject],
        relationships: Iterable[EnergyRelationship],
    ) -> None:
        self.energy_objects = tuple(energy_objects)
        self.relationships = tuple(relationships)
        self.objects_by_id = {obj.energy_object_id: obj for obj in self.energy_objects}
        self._metering_edges: dict[str, list[tuple[str, EnergyRelationship]]] = defaultdict(list)
        for relationship in self.relationships:
            edge = self._directed_metering_edge(relationship)
            if edge is not None:
                parent, child = edge
                if parent in self.objects_by_id and child in self.objects_by_id:
                    self._metering_edges[parent].append((child, relationship))
        self.validation_errors = self._validate()

    @property
    def energy_object_ids(self) -> frozenset[str]:
        return frozenset(self.objects_by_id)

    @staticmethod
    def _directed_metering_edge(
        relationship: EnergyRelationship,
    ) -> tuple[str, str] | None:
        if relationship.relationship_type == RelationshipType.METERING:
            return relationship.source_energy_object_id, relationship.peer_energy_object_id
        if relationship.relationship_type == RelationshipType.METERED_BY:
            return relationship.peer_energy_object_id, relationship.source_energy_object_id
        return None

    def _validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        object_ids = [obj.energy_object_id for obj in self.energy_objects]
        if len(set(object_ids)) != len(object_ids):
            errors.append("duplicate energy_object_id in Energy Objects")

        for relationship in self.relationships:
            if relationship.source_energy_object_id not in self.objects_by_id:
                errors.append(
                    f"relationship {relationship.relationship_id} references unknown source "
                    f"{relationship.source_energy_object_id}"
                )
            if relationship.peer_energy_object_id not in self.objects_by_id:
                errors.append(
                    f"relationship {relationship.relationship_id} references unknown peer "
                    f"{relationship.peer_energy_object_id}"
                )

        colors: dict[str, int] = {}
        stack: list[str] = []
        cycle_errors: set[str] = set()

        def visit(node: str) -> None:
            colors[node] = 1
            stack.append(node)
            for peer, _ in self._metering_edges.get(node, ()):
                if colors.get(peer, 0) == 1:
                    cycle = stack[stack.index(peer):] + [peer]
                    cycle_errors.add(f"metering cycle detected: {' -> '.join(cycle)}")
                elif colors.get(peer, 0) == 0:
                    visit(peer)
            stack.pop()
            colors[node] = 2

        for object_id in self.objects_by_id:
            if colors.get(object_id, 0) == 0:
                visit(object_id)
        errors.extend(sorted(cycle_errors))
        return tuple(errors)

    def metering_paths_from(
        self,
        root_energy_object_id: str,
    ) -> dict[str, tuple[EnergyRelationship, ...]]:
        if root_energy_object_id not in self.objects_by_id:
            return {}
        paths: dict[str, tuple[EnergyRelationship, ...]] = {root_energy_object_id: ()}
        pending = deque([root_energy_object_id])
        while pending:
            parent = pending.popleft()
            for child, relationship in self._metering_edges.get(parent, ()):
                if child not in paths:
                    paths[child] = paths[parent] + (relationship,)
                    pending.append(child)
        paths.pop(root_energy_object_id)
        return paths


def demo_energy_objects() -> tuple[EnergyObject, ...]:
    device_id = "pdu-1"
    return (
        EnergyObject(
            device_id,
            UPSTREAM_METER_ID,
            "upstream-meter",
            "00000000-0000-4000-8000-000000000001",
        ),
        EnergyObject(
            device_id,
            SERVER_A_ID,
            "server-A",
            "00000000-0000-4000-8000-000000000002",
        ),
        EnergyObject(
            device_id,
            SERVER_B_ID,
            "server-B",
            "00000000-0000-4000-8000-000000000003",
        ),
        EnergyObject(
            "router-A",
            ROUTER_A_ID,
            "router-A",
            "00000000-0000-4000-8000-000000000010",
        ),
        EnergyObject(
            "router-A",
            LINECARD_1_ID,
            "linecard-1",
            "00000000-0000-4000-8000-000000000011",
                "router-A",
                1,
        ),
        EnergyObject(
            "router-A",
            LINECARD_2_ID,
            "linecard-2",
            "00000000-0000-4000-8000-000000000012",
                "router-A",
                2,
        ),
        EnergyObject(
            "router-B",
            ROUTER_B_ID,
            "router-B",
            "00000000-0000-4000-8000-000000000020",
        ),
        EnergyObject(
            "router-B",
            NON_CRITICAL_PORT_ID,
            "non-critical-port",
            "00000000-0000-4000-8000-000000000021",
            "router-B",
            1,
        ),
    )


def demo_metering_relationships() -> tuple[EnergyRelationship, ...]:
    provenance = "explicit-demo-topology"
    return (
        EnergyRelationship(
            "rel-meter-server-a",
            RelationshipType.METERING,
            UPSTREAM_METER_ID,
            SERVER_A_ID,
            provenance,
        ),
        EnergyRelationship(
            "rel-meter-server-b",
            RelationshipType.METERING,
            UPSTREAM_METER_ID,
            SERVER_B_ID,
            provenance,
        ),
    )


def demo_accounting_boundary() -> AccountingBoundary:
    return AccountingBoundary(
        "rack-1",
        UPSTREAM_METER_ID,
        (UPSTREAM_METER_ID, SERVER_A_ID, SERVER_B_ID),
    )


def build_demo_topology(
    *,
    include_metering: bool = True,
    relationships: Sequence[EnergyRelationship] | None = None,
) -> tuple[RelationshipGraph, AccountingBoundary]:
    if relationships is None:
        selected_relationships = demo_metering_relationships() if include_metering else ()
    else:
        selected_relationships = tuple(relationships)
    graph = RelationshipGraph(demo_energy_objects(), selected_relationships)
    return graph, demo_accounting_boundary()