import argparse
import os
import re
import shlex
import subprocess
import sys
import time
from collections import defaultdict
from collections.abc import Callable, Sequence
from pathlib import Path
from textwrap import wrap

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    _console = None
else:
    _console = Console()

_wsl_keepalive: subprocess.Popen | None = None

project_source = str(Path(__file__).resolve().parent / "src")
if project_source not in sys.path:
    sys.path.insert(0, project_source)

from green.cli import SUPPORTED_USE_CASE_IDS, parse_use_case
from green.topology import demo_energy_objects

_PYTEST_RESULT = re.compile(
    r"^(?P<test>.+?)\s+(?P<result>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b"
)
_PYTEST_DURATION = re.compile(
    r"^\s*(?P<seconds>\d+(?:\.\d+)?)s\s+(?:setup|call|teardown)\s+(?P<test>.+)$"
)


def _print_status(label: str, message: str) -> None:
    colors = {"INFO": "cyan", "OK": "green", "WARNING": "yellow", "ERROR": "red"}
    color = colors.get(label, "white")
    if _console is None:
        print(f"{label} {message}")
    else:
        _console.print(f"[{color}]{label}[/{color}] {message}")


def _parse_pytest_results(
    stdout: str,
    stderr: str,
    returncode: int,
    elapsed_seconds: float,
) -> tuple[list[tuple[str, str, float | None]], dict[str, int]]:
    output = f"{stdout}\n{stderr}"
    durations: dict[str, float] = {}
    for line in output.splitlines():
        match = _PYTEST_DURATION.match(line)
        if match:
            name = match.group("test")
            durations[name] = durations.get(name, 0.0) + float(match.group("seconds"))

    rows = []
    counts = {"passed": 0, "failed": 0, "skipped": 0}
    for line in output.splitlines():
        match = _PYTEST_RESULT.match(line.strip())
        if not match:
            continue
        name, result = match.group("test"), match.group("result")
        if result in {"PASSED", "XPASS"}:
            counts["passed"] += 1
        elif result in {"FAILED", "ERROR"}:
            counts["failed"] += 1
        else:
            counts["skipped"] += 1
        duration = durations.get(name)
        rows.append((name, result, duration * 1000 if duration is not None else None))

    if not rows:
        counts["failed" if returncode else "passed"] = 1
        rows.append(("pytest suite", "FAILED" if returncode else "PASSED", elapsed_seconds * 1000))
    return rows, counts


def _display_test_results(
    stdout: str,
    stderr: str,
    returncode: int,
    elapsed_seconds: float,
) -> None:
    rows, counts = _parse_pytest_results(stdout, stderr, returncode, elapsed_seconds)
    if _console is not None:
        table = Table(title="GREEN Test Suite")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Test", overflow="fold")
        table.add_column("Result")
        table.add_column("Time (ms)", justify="right")
        for index, (name, result, duration_ms) in enumerate(rows, 1):
            if result in {"PASSED", "XPASS"}:
                result_label = "[green]PASS[/green]"
            elif result in {"FAILED", "ERROR"}:
                result_label = "[red]FAIL[/red]"
            else:
                result_label = "[yellow]SKIP[/yellow]"
            time_label = f"{duration_ms:.0f}" if duration_ms is not None else "-"
            table.add_row(str(index), name, result_label, time_label)
        _console.print(table)
        panel_style = "green" if counts["failed"] == 0 else "red"
        summary = (
            f"Total tests : {len(rows)}\n"
            f"[green]Passed      : {counts['passed']}[/green]\n"
            f"[red]Failed      : {counts['failed']}[/red]\n"
            f"Duration    : {elapsed_seconds:.2f} s"
        )
        _console.print(Panel(summary, title="[green]SUMMARY[/green]", border_style=panel_style))
    else:
        print("GREEN Test Suite")
        for index, (name, result, duration_ms) in enumerate(rows, 1):
            time_label = f"{duration_ms:.0f}" if duration_ms is not None else "-"
            print(f"{index:>3}  {name}  {result}  {time_label} ms")
        print(
            f"Total tests: {len(rows)} | Passed: {counts['passed']} | "
            f"Failed: {counts['failed']} | Duration: {elapsed_seconds:.2f} s"
        )


def _run_pytest(python: str, project_dir: Path, environment: dict[str, str]):
    command = [python, "-m", "pytest", "-v", "--durations=0"]
    _print_status("INFO", "GREEN - Start NETCONF test suite")
    started = time.perf_counter()
    if _console is None:
        result = subprocess.run(
            command,
            check=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env=environment,
        )
    else:
        with _console.status("[cyan]Running test suite...", spinner="dots"):
            result = subprocess.run(
                command,
                check=False,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=environment,
            )
    elapsed = time.perf_counter() - started
    stdout = getattr(result, "stdout", "") or ""
    stderr = getattr(result, "stderr", "") or ""
    _display_test_results(stdout, stderr, result.returncode, elapsed)
    if result.returncode and (stdout or stderr):
        if _console is not None:
            _console.print("[red]pytest details[/red]")
        print(stdout, end="" if stdout.endswith("\n") else "\n")
        print(stderr, end="" if stderr.endswith("\n") else "\n")
    return result


def project_python() -> str:
    environment_dir = Path(__file__).resolve().parent / ".venv"
    relative_executable = (
        Path("Scripts") / "python.exe" if os.name == "nt" else Path("bin") / "python"
    )
    local_python = environment_dir / relative_executable
    if not local_python.is_file():
        return sys.executable
    dependencies = subprocess.run(
        [str(local_python), "-c", "import pytest, ncclient, pyang"],
        check=False,
        capture_output=True,
        text=True,
    )
    return str(local_python) if dependencies.returncode == 0 else sys.executable


def pause_for_review(message: str, input_fn: Callable[[str], str]) -> None:
    try:
        input_fn(message)
    except EOFError:
        pass


def _wsl_command(project_dir: Path, shell_command: str) -> list[str]:
    if os.name == "nt":
        project_path = _wsl_project_path(project_dir)
        command = f"cd {shlex.quote(project_path)} && {shell_command}"
        return ["wsl.exe", "-e", "bash", "-lc", command]
    return ["bash", "-lc", f"cd {shlex.quote(str(project_dir))} && {shell_command}"]


def _wsl_project_path(project_dir: Path) -> str:
    if os.name == "nt":
        drive = project_dir.drive[0].lower()
        return f"/mnt/{drive}{project_dir.as_posix()[2:]}"
    return str(project_dir)


def _start_wsl_keepalive() -> bool:
    global _wsl_keepalive
    if os.name != "nt":
        return True
    if _wsl_keepalive is not None:
        if _wsl_keepalive.poll() is None:
            return True
        _wsl_keepalive = None

    try:
        _wsl_keepalive = subprocess.Popen(
            ["wsl.exe", "--exec", "/bin/cat"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as error:
        _print_status("ERROR", f"Could not keep WSL session alive: {error}")
        return False

    if _wsl_keepalive.poll() is not None:
        _print_status("ERROR", "Could not keep WSL session alive: wsl.exe exited immediately.")
        _wsl_keepalive = None
        return False
    return True


def _stop_wsl_keepalive() -> None:
    global _wsl_keepalive
    process = _wsl_keepalive
    _wsl_keepalive = None
    if process is None:
        return

    try:
        if process.stdin is not None:
            process.stdin.close()
        process.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)


def _hardware_component_ties() -> list[str]:
    objects = demo_energy_objects()
    object_ids_by_name = {
        item.hardware_component_name: item.energy_object_id for item in objects
    }
    children_by_parent: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for item in objects:
        if item.hardware_parent_name and item.hardware_component_name:
            children_by_parent[item.hardware_parent_name].append(
                (item.hardware_component_name, item.energy_object_id)
            )

    lines = []
    for parent, children in sorted(children_by_parent.items()):
        child_names = ", ".join(f"{object_id}/{name}" for name, object_id in children)
        sibling_label = " [siblings]" if len(children) > 1 else ""
        parent_id = object_ids_by_name.get(parent, "unmapped")
        lines.append(f"{parent_id}/{parent} -> {child_names}{sibling_label}")
    return lines


def _print_netconf_ready(project_dir: Path) -> None:
    pid_command = (
        "printf '%s\\n' "
        "\"$(systemctl show sysrepo-plugind.service -p MainPID --value)\" "
        "\"$(systemctl show netopeer2.service -p MainPID --value)\""
    )
    try:
        result = subprocess.run(
            _wsl_command(project_dir, pid_command),
            check=False,
            capture_output=True,
            text=True,
        )
        pids = result.stdout.splitlines() if result.returncode == 0 else []
    except OSError:
        pids = []
    sysrepo_pid = pids[0].strip() if len(pids) > 0 else "unknown"
    netopeer_pid = pids[1].strip() if len(pids) > 1 else "unknown"
    _print_status("OK", "WSL NETCONF ready (Netopeer2 TCP/830).")
    _print_status("INFO", f"WSL service PIDs: sysrepo-plugind={sysrepo_pid}, netopeer2={netopeer_pid}.")
    ties = _hardware_component_ties()
    if ties:
        print("Hardware component ties (Energy Object ID/component; parent/siblings):")
        for tie in ties:
            for line in wrap(
                tie,
                width=88,
                subsequent_indent="    ",
                break_long_words=False,
                break_on_hyphens=False,
            ):
                print(line)


def ensure_netconf_services() -> bool:
    if not _start_wsl_keepalive():
        return False
    project_dir = Path(__file__).resolve().parent
    wsl_project = _wsl_project_path(project_dir)
    expected_environment = (
        f"SRPD_PLUGINS_PATH={wsl_project}/netconf/plugins",
        f"GREEN_NETCONF_STATE_FILE={wsl_project}/runtime/operational.json",
        f"GREEN_NETCONF_TRACE_FILE={wsl_project}/logs/netconf-trace.log",
    )
    environment_check = " && ".join(
        f"systemctl show-environment | grep -Fx {shlex.quote(value)}"
        for value in expected_environment
    )
    health_check = (
        "systemctl is-active --quiet sysrepo-plugind.service && "
        "systemctl is-active --quiet netopeer2.service && "
        "ss -ltn | awk '$4 ~ /:830$/ { found=1 } END { exit !found }' && "
        "sysrepoctl -l | awk -F'|' '$1 ~ /^ietf-power-and-energy[[:space:]]/ { found=1 } END { exit !found }' && "
        f"{environment_check}"
    )
    try:
        health = subprocess.run(
            _wsl_command(project_dir, health_check),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        _print_status("ERROR", f"NETCONF infrastructure health check failed: {error}")
        return False

    if health.returncode == 0:
        _print_netconf_ready(project_dir)
        return True

    try:
        startup = subprocess.run(
            _wsl_command(project_dir, "bash scripts/wsl-netconf-start.sh"),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        _print_status("ERROR", f"Could not start WSL NETCONF services: {error}")
        return False

    if startup.returncode != 0:
        _print_status("ERROR", f"WSL NETCONF startup failed with exit {startup.returncode}.")
        if startup.stdout.strip():
            print(startup.stdout.strip())
        if startup.stderr.strip():
            print(startup.stderr.strip())
        return False
    _print_netconf_ready(project_dir)
    return True


def stop_netconf_services() -> None:
    project_dir = Path(__file__).resolve().parent
    stop_script = project_dir / "scripts" / "wsl-netconf-stop.sh"
    if os.name == "nt":
        drive = project_dir.drive[0].lower()
        project_path = f"/mnt/{drive}{project_dir.as_posix()[2:]}"
        wsl_command = (
            f"cd {shlex.quote(project_path)} && bash scripts/wsl-netconf-stop.sh"
        )
        command = ["wsl.exe", "-e", "bash", "-lc", wsl_command]
    else:
        command = ["bash", str(stop_script)]

    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as error:
        _print_status("WARNING", f"Could not stop NETCONF services: {error}")
        _stop_wsl_keepalive()
        return

    output = result.stdout.strip()
    if result.returncode == 0:
        if output:
            print(output)
        _stop_wsl_keepalive()
        return
    detail = result.stderr.strip() or output
    _print_status("WARNING", f"Could not stop NETCONF services (exit {result.returncode}).")
    if detail:
        print(detail)
    _stop_wsl_keepalive()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test and run the GREEN allrun51 simulator")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--auto", dest="auto", action="store_true", help="run all events automatically without prompts")
    mode.add_argument("--interactive", dest="auto", action="store_false", help="prompt between events (default)")
    parser.set_defaults(auto=False)
    parser.add_argument("--interval", type=float, help="automatic-mode delay in seconds (default: 1)")
    parser.add_argument(
        "-u",
        "--uc",
        type=parse_use_case,
        metavar="UC",
        help=f"run only one implemented UC (available: {', '.join(SUPPORTED_USE_CASE_IDS)})",
    )
    args = parser.parse_args(argv)
    if args.interval is not None and args.interval < 0:
        parser.error("--interval must be non-negative")

    try:
        if not ensure_netconf_services():
            _print_status("ERROR", "Tests were not started because NETCONF infrastructure is unavailable.")
            return 1
        project_dir = Path(__file__).resolve().parent
        python = project_python()
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(
            path for path in (project_source, environment.get("PYTHONPATH", "")) if path
        )
        if args.uc is None:
            tests = _run_pytest(python, project_dir, environment)
            if tests.returncode != 0:
                _print_status("ERROR", "NETCONF test suite failed.")
                pause_for_review("\nTests failed. Press ENTER to review the trace...", input)
                return tests.returncode
        else:
            _print_status(
                "WARNING",
                f"Skipping full pytest suite for selected {args.uc.value}; "
                "run python -m pytest -v separately after code changes.",
            )

        if args.uc is None:
            _print_status("OK", "All tests passed. Starting the GREEN runtime...")
        else:
            _print_status("INFO", f"Starting selected {args.uc.value}...")
        runtime_command = [python, "-m", "green"]
        if args.auto:
            runtime_command.append("--auto")
        if args.interval is not None:
            runtime_command.extend(("--interval", str(args.interval)))
        if args.uc is not None:
            runtime_command.extend(("--uc", args.uc.value.removeprefix("UC ")))
        runtime = subprocess.run(runtime_command, check=False, cwd=project_dir, env=environment)
        pause_for_review("\nGREEN runtime ended. Press ENTER to review the trace...", input)
        return runtime.returncode
    finally:
        stop_netconf_services()


if __name__ == "__main__":
    raise SystemExit(main())