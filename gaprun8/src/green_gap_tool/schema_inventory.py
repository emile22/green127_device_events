from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

EXPECTED_REPOSITORY_MODULES = (
    "ietf-power-and-energy",
    "ietf-hardware",
    "iana-power-and-energy",
    "iana-hardware",
    "ietf-inet-types",
    "ietf-yang-types",
)
ADDITIONAL_MODULES_TO_CHECK = (
    "ietf-green-controller",
    "ietf-green-capability-discovery",
    "ietf-network",
    "ietf-network-topology",
    "ietf-ivys-network-inventory",
)


def repository_root(project_root: Path) -> Path:
    return project_root.resolve().parent


def active_sysrepo_features() -> dict[str, Any]:
    windir = os.environ.get("WINDIR")
    wsl = Path(windir) / "System32" / "wsl.exe" if windir else None
    if wsl is None or not wsl.is_file():
        return {"status": "unavailable", "reason": "wsl.exe not found"}
    result = subprocess.run(
        [str(wsl), "-d", "Ubuntu-22.04", "-u", "root", "--", "sysrepoctl", "-l"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        return {"status": "unavailable", "reason": result.stderr.strip() or f"exit {result.returncode}"}
    for line in result.stdout.splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if cells and cells[0] == "ietf-hardware":
            feature_column = cells[6] if len(cells) > 6 else ""
            features = sorted(feature.strip() for feature in re.split(r"[,\s]+", feature_column) if feature.strip())
            return {"status": "observed", "module": "ietf-hardware", "features": features, "source": "sysrepoctl -l"}
    return {"status": "unavailable", "reason": "ietf-hardware not listed by sysrepoctl"}


def _module_metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    module_match = re.search(r"\bmodule\s+([A-Za-z0-9_.-]+)\s*\{", text)
    revision_match = re.search(r"\brevision\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\s*\{", text)
    imports = sorted(set(re.findall(r"\bimport\s+([A-Za-z0-9_.-]+)\s*\{", text)))
    return {
        "module": module_match.group(1) if module_match else path.stem,
        "revision": revision_match.group(1) if revision_match else None,
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "imports": imports,
    }


def scan_repository_yang(project_root: Path) -> dict[str, Any]:
    repo = repository_root(project_root)
    generated_root = project_root.resolve()
    excluded = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "runtime"}
    modules: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
    for path in repo.rglob("*.yang"):
        resolved = path.resolve()
        if generated_root == resolved or generated_root in resolved.parents:
            continue
        if any(part in excluded for part in path.parts):
            continue
        info = _module_metadata(path)
        modules.setdefault((info["module"], info["revision"]), []).append(info)
    unique = []
    variants = []
    for (name, revision), copies in sorted(modules.items()):
        hashes = sorted({copy["sha256"] for copy in copies})
        record = {
            "module": name,
            "revision": revision,
            "copies": copies,
            "identical_copies": len(hashes) == 1,
            "sha256_variants": hashes,
        }
        unique.append(record)
        if len(hashes) > 1:
            variants.append(record)
    present_names = {record["module"] for record in unique}
    return {
        "unique_module_revisions": unique,
        "duplicate_revision_variants": variants,
        "expected_modules": {
            name: ("present" if name in present_names else "not found in repository YANG corpus")
            for name in (*EXPECTED_REPOSITORY_MODULES, *ADDITIONAL_MODULES_TO_CHECK)
        },
    }


def prepare_upstream(project_root: Path) -> list[Path]:
    repo = repository_root(project_root)
    source_dir = repo / "allrun5" / "yang"
    destination_dir = project_root / "yang" / "upstream"
    destination_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for source in sorted(source_dir.glob("*.yang")):
        destination = destination_dir / source.name
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if destination.exists():
            destination_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
            if destination_hash != source_hash:
                raise ValueError(f"refusing to overwrite modified upstream copy: {destination}")
        else:
            shutil.copy2(source, destination)
        copied.append(destination)
    missing = set(EXPECTED_REPOSITORY_MODULES) - { _module_metadata(path)["module"] for path in copied }
    if missing:
        raise FileNotFoundError(f"allrun5/yang is missing required modules: {sorted(missing)}")
    return copied


def pyang_tree(module_path: Path, search_path: Path) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pyang", "-p", str(search_path), "-f", "tree", str(module_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode:
        raise RuntimeError(f"pyang tree failed for {module_path.name}: {result.stderr.strip()}")
    return result.stdout


def generate_tree_reports(project_root: Path) -> tuple[str, str]:
    upstream_dir = project_root / "yang" / "upstream"
    experimental_dir = project_root / "yang" / "experimental"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    upstream_paths = sorted(upstream_dir.glob("*.yang"))
    before_parts = []
    for path in upstream_paths:
        before_parts.extend([f"## {path.name}", "", pyang_tree(path, upstream_dir).rstrip(), ""])
    before = "\n".join(before_parts).rstrip() + "\n"
    (docs_dir / "yang_tree_before.txt").write_text(before, encoding="utf-8")

    after_parts = list(before_parts)
    for path in sorted(experimental_dir.glob("*.yang")):
        after_parts.extend([f"## {path.name}", "", pyang_tree(path, upstream_dir).rstrip(), ""])
    after = "\n".join(after_parts).rstrip() + "\n"
    (docs_dir / "yang_tree_after.txt").write_text(after, encoding="utf-8")
    return before, after
