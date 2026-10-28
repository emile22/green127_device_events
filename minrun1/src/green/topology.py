from dataclasses import dataclass


@dataclass(frozen=True)
class Topology:
    upstream_meter: str
    components: tuple[str, ...]

    @property
    def nodes(self) -> tuple[str, ...]:
        return (self.upstream_meter, *self.components)

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple((self.upstream_meter, component) for component in self.components)