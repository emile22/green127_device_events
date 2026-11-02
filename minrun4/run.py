import argparse
import json
import os
import shlex
import subprocess
import sys
from collections import defaultdict
from collections.abc import Callable, Sequence
from pathlib import Path
from textwrap import wrap


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


def _wsl_command(project_dir: Path, shell_command: str) -> list[str]:
    if os.name == "nt":
        project_path = _wsl_project_path(project_dir)
        return [
            "wsl.exe",
            "-e",
            "bash",
            "-lc",
            f"cd {shlex.quote(project_path)} && {shell_command}",
        ]
    return ["bash", "-lc", f"cd {shlex.quote(str(project_dir))} && {shell_command}"]


def _wsl_project_path(project_dir: Path) -> str:
    if os.name == "nt":
        drive = project_dir.drive[0].lower()
        return f"/mnt/{drive}{project_dir.as_posix()[2:]}"
    return str(project_dir)


def _hardware_hierarchy_lines(project_dir: Path) -> list[str]:
    hardware_path = project_dir / "examples" / "hardware-instance.json"
    energy_path = project_dir / "examples" / "pdu-instance.json"
    try:
        hardware = json.loads(hardware_path.read_text(encoding="utf-8"))
        energy = json.loads(energy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    object_ids_by_component = {
        item.get("source-component-id"): item.get("id")
        for item in energy.get("ietf-power-and-energy:energy-objects", {}).get("energy-object", [])
        if item.get("source-component-id") and item.get("id")
    }
    children_by_parent: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for component in hardware.get("ietf-hardware:hardware", {}).get("component", []):
        parent = component.get("parent")
        if not parent:
            continue
        name = component.get("name", "unknown")
        object_id = object_ids_by_component.get(name, "unmapped")
        position = component.get("parent-rel-pos", 0)
        children_by_parent[parent].append((name, object_id, position))

    lines: list[str] = []
    for parent, children in sorted(children_by_parent.items()):
        parent_id = object_ids_by_component.get(parent, "unmapped")
        child_labels = ", ".join(
            f"{object_id}/{name} (pos {position})"
            for name, object_id, position in sorted(children, key=lambda child: child[2])
        )
        sibling_label = " [siblings]" if len(children) > 1 else ""
        lines.append(f"  {parent_id}/{parent} -> {child_labels}{sibling_label}")
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
    print("WSL NETCONF ready (Netopeer2 TCP/830).")
    print(f"WSL service PIDs: sysrepo-plugind={sysrepo_pid}, netopeer2={netopeer_pid}.")
    hierarchy = _hardware_hierarchy_lines(project_dir)
    if hierarchy:
        print("Hardware component ties (Energy Object ID/component; parent-relative position):")
        for line in hierarchy:
            for wrapped_line in wrap(
                line,
                width=88,
                subsequent_indent="    ",
                break_long_words=False,
                break_on_hyphens=False,
            ):
                print(wrapped_line)


def ensure_netconf_services() -> bool:
    project_dir = Path(__file__).resolve().parent
    wsl_project = _wsl_project_path(project_dir)
    expected_environment = (
        f"SRPD_PLUGINS_PATH={wsl_project}/netconf/plugins",
        f"GREEN_NETCONF_STATE_FILE={wsl_project}/state/netconf/operational.json",
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
        print(f"NETCONF infrastructure health check failed: {error}")
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
        print(f"Could not start WSL NETCONF services: {error}")
        return False
    if startup.returncode != 0:
        print(f"WSL NETCONF startup failed with exit {startup.returncode}.")
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
        project_path = _wsl_project_path(project_dir)
        wsl_command = (
            f"cd {shlex.quote(project_path)} && bash scripts/wsl-netconf-stop.sh"
        )
        command = ["wsl.exe", "-e", "bash", "-lc", wsl_command]
    else:
        command = ["bash", str(stop_script)]

    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as error:
        print(f"Warning: could not stop NETCONF services: {error}")
        return

    output = result.stdout.strip()
    if result.returncode == 0:
        if output:
            print(output)
        return
    detail = result.stderr.strip() or output
    print(f"Warning: could not stop NETCONF services (exit {result.returncode}).")
    if detail:
        print(detail)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test and run the minrun4 GREEN simulator")
    parser.add_argument("--auto", action="store_true", help="run all events without prompting")
    parser.add_argument("--interval", type=float, help="automatic-mode delay in seconds")
    args = parser.parse_args(argv)
    if args.interval is not None and args.interval < 0:
        parser.error("--interval must be non-negative")

    try:
        if not ensure_netconf_services():
            print("Tests were not started because NETCONF infrastructure is unavailable.")
            return 1
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
    finally:
        stop_netconf_services()


if __name__ == "__main__":
    raise SystemExit(main())