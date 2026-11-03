from __future__ import annotations

import argparse
from contextlib import nullcontext
import os
from pathlib import Path
import sys
import time
from typing import Sequence

from green_controller.collector import collect_once, store_snapshot
from green_controller.diff import has_changes, snapshot_diff
from green_controller.netconf_client import NetconfClient, NetconfUnavailable
from green_controller.normalize import parse_netconf_xml
from green_controller.processing import process_snapshot
from green_controller.render_processing import render_processing


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
    parser = argparse.ArgumentParser(description="Read-only GREEN controller processing and decision preparation")
    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument("--once", action="store_true", help="collect and process one NETCONF snapshot")
    mode.add_argument("--watch", action="store_true", help="collect and process snapshots repeatedly")
    parser.add_argument("--interval", type=float, default=1.0, help="watch interval in seconds")
    parser.add_argument("--output", type=Path, default=Path("logs"), help="raw and normalized snapshot directory")
    parser.add_argument("--fixture", type=Path, help="use a saved NETCONF reply for deterministic processing")
    parser.add_argument("--show-processing", action="store_true", help="include the full processing record")
    return parser


class FixtureClient:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.device = "fixture-device"

    def get(self) -> str:
        return self.path.read_text(encoding="utf-8")


def _process_cycle(client, output: Path, project_root: Path, previous: dict | None, details: bool) -> dict:
    snapshot = collect_once(client)
    store_snapshot(snapshot, output)
    result = process_snapshot(snapshot.normalized, project_root)
    diff = snapshot_diff(previous, snapshot.normalized)
    if previous is not None and not has_changes(diff):
        return snapshot.normalized
    result["diff"] = diff
    print(render_processing(result, details=details))
    return snapshot.normalized


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.once and not args.watch:
        args.once = True
    if args.interval <= 0:
        parser.error("--interval must be greater than zero")
    try:
        print(
            "Processing the current allrun5 NETCONF snapshot; simulator event identity is not exposed by device YANG.",
            flush=True,
        )
        project_root = Path(__file__).resolve().parents[2]
        output = args.output if args.output.is_absolute() else project_root / args.output
        context = (
            NetconfClient.connect_from_environment()
            if args.fixture is None
            else nullcontext(FixtureClient(args.fixture))
        )
        with context as client:
            previous = None
            if args.watch:
                print("Watch mode active. Press q to stop.", flush=True)
            while True:
                previous = _process_cycle(client, output, project_root, previous, args.show_processing)
                if args.once:
                    return 0
                if _wait_for_interval(args.interval):
                    print("\nGREEN Controller processor stopped by q.")
                    return 0
    except KeyboardInterrupt:
        print("\nGREEN Controller processor stopped.")
        return 0
    except (NetconfUnavailable, OSError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
