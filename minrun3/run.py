import argparse
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path


def project_python() -> str:
    environment_dir = Path(__file__).resolve().parent / ".venv"
    relative_executable = (
        Path("Scripts") / "python.exe" if os.name == "nt" else Path("bin") / "python"
    )
    local_python = environment_dir / relative_executable
    return str(local_python) if local_python.is_file() else sys.executable


def pause_for_review(message: str, input_fn: Callable[[str], str]) -> None:
    try:
        input_fn(message)
    except EOFError:
        pass


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test and run the minrun3 GREEN simulator")
    parser.add_argument("--auto", action="store_true", help="run all events without prompting")
    parser.add_argument("--interval", type=float, help="automatic-mode delay in seconds")
    args = parser.parse_args(argv)
    if args.interval is not None and args.interval < 0:
        parser.error("--interval must be non-negative")

    print("WSL NETCONF not configured in minrun3 (Python/YANG adapter only).")
    project_dir = Path(__file__).resolve().parent
    python = project_python()
    tests = subprocess.run(
        [python, "-m", "pytest", "-v"],
        check=False,
        stdin=subprocess.DEVNULL,
        cwd=project_dir,
    )
    if tests.returncode != 0:
        pause_for_review("\nTests failed. Press ENTER to review the trace...", input)
        return tests.returncode

    print("\nAll tests passed. Starting the GREEN runtime...\n", flush=True)
    runtime_command = [python, "-m", "green"]
    if args.auto:
        runtime_command.append("--auto")
    if args.interval is not None:
        runtime_command.extend(("--interval", str(args.interval)))
    runtime = subprocess.run(runtime_command, check=False, cwd=project_dir)
    pause_for_review("\nGREEN runtime ended. Press ENTER to review the trace...", input)
    return runtime.returncode


if __name__ == "__main__":
    raise SystemExit(main())