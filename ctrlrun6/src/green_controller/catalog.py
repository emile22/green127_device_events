from __future__ import annotations

from pathlib import Path

from green_controller.models import EventReference


def repository_root() -> Path:
    package_file = Path(__file__).resolve()
    root = package_file.parents[3]
    if not (root / "allrun5").is_dir():
        raise FileNotFoundError(f"read-only allrun5 baseline is missing under {root}")
    return root


def load_event_catalog(path: Path | None = None) -> tuple[EventReference, ...]:
    source = path or repository_root() / "allrun5" / "docs" / "event_catalog.md"
    events: list[EventReference] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9 or not cells[0].startswith("UC 2."):
            continue
        if cells[2] == "Event ID" or not cells[2].startswith("U"):
            continue
        events.append(
            EventReference(
                uc=cells[0],
                title=cells[1],
                event_id=cells[2],
                event_name=cells[3],
                description=cells[4],
                relationship_families=cells[6],
                expected_yang=cells[7],
                simulator_metadata=cells[8],
            )
        )
    if len(events) != 61:
        raise ValueError(f"expected 61 allrun5 Group A events, found {len(events)} in {source}")
    return tuple(events)
