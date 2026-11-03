from __future__ import annotations

import difflib
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

from green_gap_tool.schema_inventory import generate_tree_reports, prepare_upstream, repository_root


def _wsl_executable() -> Path | None:
    windir = os.environ.get("WINDIR")
    if not windir:
        return None
    path = Path(windir) / "System32" / "wsl.exe"
    return path if path.is_file() else None


def _wsl_path(path: Path) -> str:
    drive = path.drive.rstrip(":\\/").lower()
    parts = path.parts[1:]
    return "/mnt/" + drive + "/" + "/".join(parts)


def _yanglint(project_root: Path, schemas: list[Path], instance: Path) -> dict[str, Any]:
    wsl = _wsl_executable()
    if wsl is None:
        return {"status": "unavailable", "detail": "wsl.exe not found; yanglint validation skipped"}
    repo_root = repository_root(project_root)
    posix_repo = _wsl_path(repo_root)
    schema_args = " ".join(
        shlex.quote((Path("gaprun8") / "yang" / schema.relative_to(project_root / "yang")).as_posix())
        for schema in schemas
    )
    search = "-p gaprun8/yang/upstream -p gaprun8/yang/experimental"
    command = (
        f"cd {shlex.quote(posix_repo)} && yanglint {search} "
        f"{schema_args} {shlex.quote('gaprun8/examples/representative-state.json')}"
    )
    result = subprocess.run(
        [str(wsl), "-d", "Ubuntu-22.04", "--", "bash", "-lc", command],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "command": "yanglint with copied upstream/experimental modules and representative-state.json",
    }


def validate(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    repo_root = repository_root(project_root)
    upstream = prepare_upstream(project_root)
    experimental_dir = project_root / "yang" / "experimental"
    experimental = sorted(experimental_dir.glob("*.yang"))
    search_path = project_root / "yang" / "upstream"
    pyang_results = []
    for module in (*upstream, *experimental):
        result = subprocess.run(
            [sys.executable, "-m", "pyang", "-p", str(search_path), str(module)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        pyang_results.append(
            {
                "module": module.name,
                "status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )
        if result.returncode:
            raise RuntimeError(f"pyang failed for {module.name}: {result.stderr.strip()}")

    upstream_checks = []
    for copied in upstream:
        source = repo_root / "allrun5" / "yang" / copied.name
        copied_hash = hashlib.sha256(copied.read_bytes()).hexdigest()
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        upstream_checks.append({"module": copied.name, "sha256": copied_hash, "matches_allrun5": copied_hash == source_hash})
        if copied_hash != source_hash:
            raise RuntimeError(f"upstream copy differs from allrun5: {copied.name}")

    before, after = generate_tree_reports(project_root)
    diff = "\n".join(
        difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            fromfile="yang_tree_before.txt", tofile="yang_tree_after.txt", lineterm="",
        )
    )
    if not diff:
        diff = "No experimental nodes were added.\n"
    (project_root / "docs" / "yang_tree_diff.md").write_text(
        "# YANG Tree Diff\n\n```diff\n" + diff + "\n```\n",
        encoding="utf-8",
    )

    schemas = [*upstream, *experimental]
    yanglint_result = _yanglint(
        project_root,
        schemas,
        project_root / "examples" / "representative-state.json",
    )
    result = {
        "pyang": pyang_results,
        "upstream_hashes": upstream_checks,
        "yanglint": yanglint_result,
        "experimental_modules": [path.name for path in experimental],
        "tree_diff": "gaprun8/docs/yang_tree_diff.md",
    }
    (project_root / "docs" / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result
