from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
import os
from pathlib import Path
import sys
import time
from typing import Sequence

from green_controller.catalog import load_event_catalog
from green_controller.collector import (
    observe_event_catalog,
    store_event_observations,
    store_snapshot,
    write_observation_catalog,
)
from green_controller.diff import has_changes, snapshot_diff
from green_controller.netconf_client import NetconfClient, NetconfUnavailable
from green_controller.normalize import parse_netconf_xml
from green_controller.render import render


VIEWS = ("summary", "inventory", "energy-objects", "relationships", "raw-json", "raw-xml", "diff")


def _q_pressed() -> bool:
    if not sys.stdin.isatty():
        return False
    if os.name == "nt":
        import msvcrt

        pressed = False
        while msvcrt.kbhit():
            key = msvcrt.getwch()
            if key.lower() == "q":
                pressed = True
        return pressed

    import select

    readable, _, _ = select.select([sys.stdin], [], [], 0)
    return bool(readable and sys.stdin.readline().strip().lower() == "q")


def _wait_for_interval(interval: float, q_pressed=None) -> bool:
    check_q = q_pressed or _q_pressed
    deadline = time.monotonic() + interval
    while True:
        if check_q():
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(0.1, remaining))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only GREEN NETCONF observer")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="collect the full event catalog once")
    mode.add_argument("--watch", action="store_true", help="collect current state repeatedly")
    parser.add_argument("--interval", type=float, default=1.0, help="watch interval in seconds")
    parser.add_argument("--view", choices=VIEWS, default="summary", help="controller view to render")
    parser.add_argument("--output", type=Path, default=Path("logs"), help="raw and normalized snapshot directory")
    parser.add_argument("--fixture", type=Path, help="use a saved NETCONF reply instead of opening a live session")
    return parser


def _one_live_snapshot(
    output: Path,
    view: str,
    previous: dict | None = None,
    *,
    suppress_unchanged: bool = False,
) -> dict:
    with NetconfClient.connect_from_environment() as client:
        from green_controller.collector import collect_once

        snapshot = collect_once(client)
    store_snapshot(snapshot, output)
    diff = snapshot_diff(previous, snapshot.normalized)
    if suppress_unchanged and previous is not None and not has_changes(diff):
        return snapshot.normalized
    print(render({**snapshot.normalized, "raw_xml": snapshot.raw_xml}, view, diff))
    return snapshot.normalized


class FixtureClient:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.device = "fixture-device"

    def get(self) -> str:
        return self.path.read_text(encoding="utf-8")


def _catalog_once(output: Path, view: str, fixture: Path | None) -> int:
    context = NetconfClient.connect_from_environment() if fixture is None else nullcontext(FixtureClient(fixture))
    print(
        "Event labels come from allrun5/docs/event_catalog.md; each snapshot is fetched via NETCONF <get>.",
        flush=True,
    )
    with context as client:
        observations = observe_event_catalog(
            client,
            progress=lambda index, total, event: print(
                f"[{index:02d}/{total}] Collected {event.uc} {event.event_id} {event.event_name}",
                flush=True,
            ),
        )
    if not observations:
        raise NetconfUnavailable("allrun5 event catalog is empty")
    store_event_observations(observations, output / "events")
    store_snapshot(observations[-1].snapshot, output)
    write_observation_catalog(observations, Path("docs/observation_catalog.md"))
    latest = observations[-1].snapshot
    diff = snapshot_diff(None, latest.normalized)
    print(f"NETCONF GETs recorded: {len(observations)} (one for each allrun5 catalog event)")
    print(render({**latest.normalized, "raw_xml": latest.raw_xml}, view, diff))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.interval <= 0:
        parser.error("--interval must be greater than zero")
    try:
        if args.once:
            return _catalog_once(args.output, args.view, args.fixture)
        if args.fixture is not None:
            parser.error("--fixture is supported with --once only")
        print("Watch mode active. Press q to stop.", flush=True)
        previous = None
        while True:
            view = args.view if previous is None else ("diff" if args.view == "summary" else args.view)
            previous = _one_live_snapshot(
                args.output,
                view,
                previous,
                suppress_unchanged=view == "diff",
            )
            if _wait_for_interval(args.interval):
                print("\nGREEN Controller observer stopped by q.")
                return 0
    except KeyboardInterrupt:
        print("\nGREEN Controller observer stopped.")
        return 0
    except (NetconfUnavailable, OSError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
