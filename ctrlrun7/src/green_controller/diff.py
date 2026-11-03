from __future__ import annotations

from typing import Any


def snapshot_diff(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    if previous is None:
        return {"added": ["initial snapshot"], "removed": [], "changed": []}

    def object_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
        objects = snapshot.get("ietf-power-and-energy:energy-objects", {}).get("energy-object", [])
        return {str(item["id"]): item for item in objects if isinstance(item, dict) and "id" in item}

    before = object_map(previous)
    after = object_map(current)
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    changed = []
    for object_id in sorted(before.keys() & after.keys()):
        if before[object_id] != after[object_id]:
            changed.append({"id": object_id, "before": before[object_id], "after": after[object_id]})
    return {"added": added, "removed": removed, "changed": changed}


def has_changes(diff: dict[str, Any]) -> bool:
    return any(diff.get(key) for key in ("added", "removed", "changed"))


def has_changes(diff: dict[str, Any]) -> bool:
    return any(diff.get(key) for key in ("added", "removed", "changed"))
