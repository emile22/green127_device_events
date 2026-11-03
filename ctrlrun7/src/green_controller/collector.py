from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from green_controller.catalog import load_event_catalog
from green_controller.diff import snapshot_diff
from green_controller.models import EventObservation, NetconfSnapshot
from green_controller.normalize import parse_netconf_xml


class NetconfGetter(Protocol):
    device: str

    def get(self) -> str: ...


def collect_once(client: NetconfGetter) -> NetconfSnapshot:
    return parse_netconf_xml(client.get(), device=client.device)


def observe_event_catalog(client: NetconfGetter) -> tuple[EventObservation, ...]:
    observations: list[EventObservation] = []
    for event in load_event_catalog():
        snapshot = collect_once(client)
        observations.append(
            EventObservation(
                event=event,
                snapshot=snapshot,
                correlation=(
                    "catalog reference only; the NETCONF schema does not expose this simulator event ID"
                ),
            )
        )
    return tuple(observations)


def store_snapshot(snapshot: NetconfSnapshot, output_dir: Path, *, name: str = "latest") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{name}.xml").write_text(snapshot.raw_xml, encoding="utf-8")
    (output_dir / f"{name}.json").write_text(
        json.dumps(snapshot.normalized, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def store_event_observations(
    observations: tuple[EventObservation, ...], output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for observation in observations:
        store_snapshot(observation.snapshot, output_dir, name=observation.event.event_id)


def write_observation_catalog(
    observations: tuple[EventObservation, ...], destination: Path
) -> None:
    rows = [
        "# GREEN Controller Observation Catalog",
        "",
        "Each row references a deterministic allrun5 catalog event and the corresponding NETCONF collection. The current schema does not expose simulator event IDs, so the association is a catalog reference, not a claim that the device returned that event identity.",
        "",
        "| UC | Event | Observed requirement | YANG module/path if visible | Classification | Controller metadata | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    previous: dict | None = None
    for observation in observations:
        event = observation.event
        normalized = observation.snapshot.normalized
        fields = observation.snapshot.fields
        source_components = sum(
            bool(item.get("source-component-id"))
            for item in normalized["ietf-power-and-energy:energy-objects"]["energy-object"]
        )
        visible_paths: set[str] = set()
        unavailable = []
        for requirement in (part.strip() for part in event.expected_yang.split(",")):
            if not requirement or requirement.lower() == "none":
                continue
            key = requirement.lower()
            matches = []
            if "inventory" in key:
                matches = [
                    field for field in fields
                    if field.module == "ietf-hardware" and "/component[" in field.data_path
                ]
            elif "source-component-id" in key:
                matches = [field for field in fields if field.data_path.endswith("/source-component-id")]
            elif "relationship" in key:
                matches = [field for field in fields if "/relationship/" in field.data_path or "/peer/" in field.data_path]
            elif key == "oper":
                matches = [field for field in fields if field.data_path.endswith("/oper")]
            else:
                matches = [field for field in fields if field.data_path.lower().endswith("/" + key)]
            if matches:
                visible_paths.update(f"{field.module}:{field.data_path}" for field in matches)
            else:
                unavailable.append(requirement)
        metadata = event.simulator_metadata.strip()
        if metadata.lower() in {"", "none"}:
            metadata = "none declared"
        classifications = []
        if visible_paths:
            classifications.append("YANG-visible")
        if source_components:
            classifications.append("derived-from-YANG")
        if metadata.lower() != "none declared":
            classifications.append("controller-metadata-only")
        if unavailable:
            classifications.append("unavailable")
        if not classifications:
            classifications.append("unavailable")
        diff = snapshot_diff(previous, normalized)
        diff_note = (
            "initial snapshot"
            if previous is None
            else f"diff: {len(diff['added'])} added, {len(diff['removed'])} removed, {len(diff['changed'])} changed Energy Objects"
        )
        rows.append(
            "| {uc} {title} | {event_id} {name} | {description} | {paths} | {classifications} | {metadata} | {notes} |".format(
                uc=event.uc,
                title=event.title.replace("|", "\\|"),
                event_id=event.event_id,
                name=event.event_name.replace("|", "\\|"),
                description=event.description.replace("|", "\\|"),
                paths="<br>".join(sorted(visible_paths)) if visible_paths else "none observed",
                classifications=", ".join(classifications),
                metadata=metadata.replace("|", "\\|"),
                notes=(
                    f"{observation.correlation}; {diff_note}; unavailable expected fields: "
                    f"{', '.join(unavailable) if unavailable else 'none'}"
                ).replace("|", "\\|"),
            )
        )
        previous = normalized
    rows.extend(
        [
            "",
            "Classification is limited to YANG-visible, derived-from-YANG, controller-metadata-only, and unavailable. Unavailable means the current NETCONF snapshot did not contain the expected value; it is not a YANG gap assessment.",
            "",
        ]
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rows), encoding="utf-8")
