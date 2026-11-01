import json
import os
import threading
from collections.abc import Callable
from pathlib import Path
from textwrap import wrap

from green.energy_observability import build_observability_registry


_TRACE_WIDTH = 72


def _wrap_line(text: str, width: int = _TRACE_WIDTH) -> list[str]:
    indentation = text[: len(text) - len(text.lstrip())]
    content = text.strip()
    if not content:
        return [""]
    return wrap(
        content,
        width=max(1, width - len(indentation)),
        initial_indent=indentation,
        subsequent_indent=indentation,
        break_long_words=True,
        break_on_hyphens=False,
    )


def _hardware_inventory(data: object) -> list[str] | None:
    if not isinstance(data, dict):
        return None
    hardware = data.get("ietf-hardware:hardware")
    if not isinstance(hardware, dict):
        return None
    components = hardware.get("component")
    if not isinstance(components, list):
        return None

    rows = ["HARDWARE INVENTORY", f"{'Component':<22} {'Class':<16} UUID"]
    rows.append(f"{'-' * 22} {'-' * 16} --------")
    for component in components:
        if not isinstance(component, dict):
            continue
        name = str(component.get("name", "unknown"))
        component_class = str(component.get("class", "unknown")).rsplit(":", 1)[-1]
        uuid = str(component.get("uuid", ""))
        uuid_suffix = f"...{uuid[-4:]}" if uuid else "-"
        rows.extend(_wrap_line(f"{name:<22} {component_class:<16} {uuid_suffix}"))
    return rows


def _energy_object_inventory(data: object) -> list[str] | None:
    if not isinstance(data, dict):
        return None
    energy_objects = data.get("ietf-power-and-energy:energy-objects")
    if not isinstance(energy_objects, dict):
        return None
    objects = energy_objects.get("energy-object")
    if not isinstance(objects, list):
        return None

    column_widths = (20, 17, 7, 9, 14)

    def table_row(cells: list[str]) -> list[str]:
        wrapped_cells = [
            wrap(
                cell,
                width=width,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]
            for cell, width in zip(cells, column_widths, strict=True)
        ]
        row_count = max(map(len, wrapped_cells))
        return [
            " ".join(
                (wrapped_cells[column][row] if row < len(wrapped_cells[column]) else "")
                .ljust(column_widths[column])
                for column in range(len(column_widths))
            ).rstrip()
            for row in range(row_count)
        ]

    rows = [
        "GREEN ENERGY OBJECTS",
        *table_row(["Energy Object", "Source component", "Power", "State", "Relationships"]),
        "-" * _TRACE_WIDTH,
    ]
    observability = build_observability_registry()
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_id = str(item.get("id", "unknown"))
        hardware_name = str(item.get("source-component-id", "-"))
        profile = observability.get(object_id)
        power_data = item.get("power")
        power_value = power_data.get("instantaneous-power") if isinstance(power_data, dict) else None
        power = profile.display_power(power_value) if profile else "UNKNOWN"
        state_data = item.get("power-state")
        state = state_data.get("oper") if isinstance(state_data, dict) else None
        state = str(state).rsplit(":", 1)[-1] if state is not None else None
        if state and state.startswith("power-state-"):
            state = state.removeprefix("power-state-")
        state = profile.display_state(state.upper() if state else None) if profile else "UNKNOWN"
        relationships: list[str] = []
        relationship_data = item.get("relationship")
        if isinstance(relationship_data, list):
            for relationship in relationship_data:
                if not isinstance(relationship, dict):
                    continue
                relationship_type = str(relationship.get("type", "unknown")).rsplit(":", 1)[-1]
                peers = relationship.get("peer")
                peer_count = len(peers) if isinstance(peers, list) else 0
                relationships.append(f"{relationship_type.upper()}({peer_count})")
        relationship_text = (
            profile.display_relationships(",".join(relationships) if relationships else None)
            if profile
            else "UNKNOWN"
        )
        rows.extend(table_row([object_id, hardware_name, power, state, relationship_text]))
    return rows


def format_netconf_trace_entry(entry: str) -> str:
    lines = entry.splitlines()
    header = next(
        (line for line in lines if line.startswith("[") and "] " in line),
        "[unknown time] trace record",
    )
    timestamp, _, record_type = header[1:].partition("] ")
    context = next((line for line in lines if line.startswith("UC ")), "NETCONF GET")

    fields: dict[str, str] = {}
    for line in lines[1:]:
        key, separator, value = line.partition(":")
        if separator and key in {"operation", "module", "path", "request-xpath", "status"}:
            fields[key] = value.strip()

    payload = entry.partition("reply-data-json:")[2].strip()
    data: object | None = None
    try:
        data = json.loads(payload)
        formatted_payload = json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        formatted_payload = payload or "(empty)"
    inventory = _hardware_inventory(data)
    energy_inventory = _energy_object_inventory(data)

    operation = fields.get("operation", record_type)
    status = fields.get("status", "unknown").upper()
    panel = ["NETCONF TRACE", *_wrap_line(context)]
    panel.extend(_wrap_line(f"{operation} | {status} | {timestamp}"))
    panel.extend(_wrap_line(f"Module: {fields.get('module', 'unknown')}"))
    panel.extend(_wrap_line(f"Path: {fields.get('path', 'unknown')}"))
    panel.extend(_wrap_line(f"Filter: {fields.get('request-xpath', '(not provided)')}"))
    if inventory is not None and energy_inventory is not None:
        panel.append("Reply: HARDWARE INVENTORY")
        for line in inventory[1:]:
            panel.extend(_wrap_line(line))
        panel.append("")
        for line in energy_inventory:
            panel.extend(_wrap_line(line))
    elif energy_inventory is not None:
        for line in energy_inventory:
            panel.extend(_wrap_line(line))
    elif inventory is not None:
        panel.append("Reply: HARDWARE INVENTORY")
        for line in inventory[1:]:
            panel.extend(_wrap_line(line))
    else:
        panel.append("Reply / JSON:")
        for line in formatted_payload.splitlines() or ["(empty)"]:
            panel.extend(_wrap_line(line))
    panel.append("-" * _TRACE_WIDTH)
    return "\n".join(panel)


class NetconfTraceTailer:
    def __init__(
        self,
        trace_path: Path,
        output_fn: Callable[[str], None],
        poll_interval: float = 0.1,
    ) -> None:
        self.trace_path = trace_path
        self.output_fn = output_fn
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        try:
            self._start_offset = trace_path.stat().st_size
        except FileNotFoundError:
            self._start_offset = 0

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._tail, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join()
        self._thread = None

    def _tail(self) -> None:
        stream = None
        pending = ""
        offset = self._start_offset
        while not self._stop_event.is_set():
            if stream is None:
                try:
                    stream = self.trace_path.open("r", encoding="utf-8")
                    stream.seek(offset)
                except FileNotFoundError:
                    self._stop_event.wait(self.poll_interval)
                    continue
            pending, offset = self._read_entries(stream, pending, offset)
            self._stop_event.wait(self.poll_interval)

        if stream is None:
            try:
                stream = self.trace_path.open("r", encoding="utf-8")
                stream.seek(offset)
            except FileNotFoundError:
                return
        pending, _ = self._read_entries(stream, pending, offset)
        if pending.strip():
            self.output_fn(format_netconf_trace_entry(pending))
        stream.close()

    def _read_entries(self, stream, pending: str, offset: int) -> tuple[str, int]:
        chunk = stream.read()
        offset = stream.tell()
        pending += chunk
        while "\n\n" in pending:
            entry, pending = pending.split("\n\n", 1)
            if entry.strip():
                self.output_fn(format_netconf_trace_entry(entry))
        return pending, offset