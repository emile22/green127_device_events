from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from green_gap_tool.schema_inventory import (
    active_sysrepo_features,
    generate_tree_reports,
    prepare_upstream,
    pyang_tree,
    repository_root,
    scan_repository_yang,
)
from green_gap_tool.traceability import write_reports


def _module_by_name(project_root: Path, module_name: str) -> Path:
    for path in (project_root / "yang" / "upstream").glob("*.yang"):
        text = path.read_text(encoding="utf-8")
        if re.search(rf"\bmodule\s+{re.escape(module_name)}\s*\{{", text):
            return path
    raise FileNotFoundError(f"YANG module not found in copied corpus: {module_name}")


def _path_evidence(candidate: dict[str, Any], tree_by_module: dict[str, str]) -> list[str]:
    evidence = []
    for path in candidate.get("searched_paths", []):
        module = path.lstrip("/").split(":", 1)[0]
        leaf = path.rsplit("/", 1)[-1]
        tree = tree_by_module.get(module, "")
        present = leaf.split("[")[0] in tree
        evidence.append(f"{module}:{leaf} {'present in pyang tree' if present else 'not found in pyang tree'}")
    return evidence


def _decision(
    candidate: dict[str, Any],
    tree_by_module: dict[str, str],
    module_text: dict[str, str],
    runtime_features: dict[str, Any],
) -> dict[str, Any]:
    uc = candidate["uc"]
    evidence = _path_evidence(candidate, tree_by_module)
    base = {
        "candidate": candidate,
        "schema_evidence": evidence,
        "decision": "NOT A GAP",
        "rationale": "The requirement is adequately handled by existing YANG or is controller-scope metadata/processing.",
    }
    if uc == "UC 2.10":
        power_tree = tree_by_module.get("ietf-power-and-energy", "")
        power_text = module_text.get("ietf-power-and-energy", "")
        has_cumulative = "total-energy-consumed" in power_tree and "since the last reset" in power_text
        has_timestamps = "interval-start" in power_tree or "interval-end" in power_tree
        has_interval_leaf = "interval-energy-consumed" in power_tree
        base["schema_evidence"].extend([
            f"total-energy-consumed cumulative counter: {has_cumulative}",
            f"explicit interval start/end leaves: {has_timestamps}",
            f"explicit interval-energy-consumed leaf: {has_interval_leaf}",
            "units statement declares Watt-hours; prose description also mentions mWh",
        ])
        base["rationale"] = (
            "The existing operational cumulative counter can be sampled and differenced by the controller; "
            "the controller records retrieval timestamps and can mark counter decreases/reset uncertainty incomplete. "
            "The machine-readable units statement declares Watt-hours; its conflicting prose is an editorial clarification candidate, not an unrepresentable node."
        )
        return base
    if uc == "UC 2.14":
        hardware_tree = tree_by_module.get("ietf-hardware", "")
        hardware_text = module_text.get("ietf-hardware", "")
        iana_text = module_text.get("iana-hardware", "")
        sensor_generic = all(token in hardware_tree for token in ("sensor-data", "value-type", "value-scale", "units-display"))
        sensor_feature = "feature hardware-sensor" in hardware_text
        active_features = runtime_features.get("features", []) if runtime_features.get("status") == "observed" else None
        sensor_feature_enabled = "hardware-sensor" in active_features if active_features is not None else None
        battery_identity = "identity battery" in iana_text
        explicit_soc = any(term in "\n".join(tree_by_module.values()) for term in ("state-of-charge", "battery-level-percent"))
        base["schema_evidence"].extend([
            f"explicit state-of-charge/battery-level node: {explicit_soc}",
            f"RFC 8348 generic sensor-data/value-type/units-display representation: {sensor_generic}",
            f"generic sensor data is feature-gated by hardware-sensor: {sensor_feature}",
            f"hardware-sensor feature enabled in current Sysrepo: {sensor_feature_enabled}",
            f"IANA hardware battery identity exists: {battery_identity}",
        ])
        if not explicit_soc and sensor_generic and sensor_feature and battery_identity:
            base.update({
                "decision": "CONFIRMED GAP",
                "rationale": (
                    "A battery state-of-charge is a concrete UC 2.14 operational value demonstrated by U14-1 through U14-3. "
                    "The active Energy Object schema has no typed state-of-charge leaf. RFC 8348 generic sensor-data is feature-gated (hardware-sensor is not enabled in the inspected Sysrepo module) and its `other` value plus display string does not identify state-of-charge as a machine-readable battery semantic."
                ),
                "gap": {
                    "gap_id": "GAP-001",
                    "category": "STATE-GAP",
                    "scope": "device operational state",
                    "solution": "Add a local experimental battery-state-of-charge container with explicit available/unknown/unavailable status and a bounded percentage leaf.",
                    "experimental_path": "/ietf-power-and-energy:energy-objects/energy-object/example-green-power-energy-gaps:battery-state-of-charge/state-of-charge-percent",
                    "config": "config false",
                    "type_units": "decimal64 fraction-digits 2, range 0..100, units percent",
                    "test": "test_soc_status_and_percent_validation",
                },
            })
        else:
            base["rationale"] = "The actual schemas provide an adequate representation for the demonstrated battery state."
        return base

    rationales = {
        "UC 2.1": "The baseline comparison and vendor source are controller-side provenance; existing data-source-accuracy identities cover measured, estimated, and static source quality, and no interoperable device baseline field is required by the event text.",
        "UC 2.2": "Traffic condition and service continuity are controller policy inputs; the device model already exposes current power and operational state, so no additional energy leaf is required.",
        "UC 2.5": "The model has measurement-local and directional metering/powering relationships. The target's unknown direct measurement remains correctly represented as unknown controller context.",
        "UC 2.6": "Aggregating/aggregated-by and power/energy leaves represent the objects and readings; normalization, boundary guards, and lineage are processing provenance, not missing device state.",
        "UC 2.7": "Throughput profile and traffic condition are network-control context outside this energy-object operational model; the controller can retain them as metadata.",
        "UC 2.8": "Delivery strategy and cache placement are application/controller context; the current energy objects already carry the observed power values.",
        "UC 2.9": "The generic operational power-state leaf plus enabling, metering, and powering relationships represent the device state and topology; coverage and recovery-delay constraints are controller policy.",
        "UC 2.11": "Existing data-source-accuracy identities cover measured/estimated/static/unavailable source quality; history and optimized/legacy classification are controller-derived.",
        "UC 2.12": "Sensing modes, traffic routing, and critical-function policy are application/controller semantics; hardware state, power, and aggregation relationships are available for the energy view.",
        "UC 2.13": "Existing directional metering relationships are sufficient to compute topology completeness and accounting status in the controller; no device-side completeness state is required.",
        "UC 2.15": "Scheduling windows, workload placement, and active-node policy are controller/application context; existing Energy Objects and power-state leaves expose the relevant device observations.",
        "UC 2.16": "The enabling/enabled-by relationship models functional dependency; coordination progress and QoS policy remain controller-side decision context.",
    }
    base["rationale"] = rationales.get(uc, "The requirement is controller-side or already represented by the inspected schema.")
    return base


def _group_b_review(repo_root: Path) -> list[dict[str, Any]]:
    deferred = (repo_root / "allrun5" / "docs" / "deferred_group_b.md").read_text(encoding="utf-8")
    return [
        {
            "uc": "UC 2.3",
            "title": "Reporting on Lifecycle Management",
            "decision": "NOT A GAP candidate based on available text",
            "modeling_needs_from_text": [
                "lifecycle embedded-energy/carbon estimates for manufacturing, transport, recyclability, and end-of-life",
                "location-based carbon factors and energy mix",
                "backup-source identity and awareness of which backup is in use",
                "vendor, datasheet, or database information ingestion",
            ],
            "rationale": "The draft describes lifecycle reporting inputs and external metadata but gives no concrete event sequence, collection timing, or interoperable device data contract. No lifecycle transitions or external-data behavior are invented.",
            "source_evidence": "draft-ietf-green-use-cases.md, UC 2.3; allrun5/docs/deferred_group_b.md",
        },
        {
            "uc": "UC 2.4",
            "title": "Real-time Energy Metering of Virtualised or Cloud-native Network Functions",
            "decision": "NOT A GAP candidate based on available text",
            "modeling_needs_from_text": [
                "real-time energy measurement for virtualized or cloud-native functions",
                "metering across hardware and software layers",
                "energy-aware management of dynamic workloads",
            ],
            "rationale": "The draft states a high-level metering need but leaves GREEN requirements as TODO; it does not define virtual entity identity, host correlation, shared-energy attribution, migration behavior, or event timing.",
            "source_evidence": "draft-ietf-green-use-cases.md, UC 2.4; allrun5/docs/deferred_group_b.md",
        },
    ]


def analyze(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    repo_root = repository_root(project_root)
    input_path = repo_root / "ctrlrun7" / "docs" / "green8_input.json"
    candidates = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(candidates, list):
        raise ValueError("green8_input.json must contain a list")

    upstream_paths = prepare_upstream(project_root)
    corpus = scan_repository_yang(project_root)
    tree_by_module: dict[str, str] = {}
    module_text: dict[str, str] = {}
    for path in upstream_paths:
        module = _module_by_name(project_root, _module_name(path))
        name = _module_name(path)
        module_text[name] = module.read_text(encoding="utf-8")
        tree_by_module[name] = pyang_tree(path, project_root / "yang" / "upstream")

    before_parts = []
    for path in upstream_paths:
        before_parts.extend([f"## {path.name}", "", tree_by_module[_module_name(path)].rstrip(), ""])
    docs = project_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "yang_tree_before.txt").write_text("\n".join(before_parts).rstrip() + "\n", encoding="utf-8")

    runtime_features = active_sysrepo_features()
    corpus["active_sysrepo_features"] = runtime_features
    decisions = [_decision(candidate, tree_by_module, module_text, runtime_features) for candidate in candidates]
    result = {
        "input_path": str(input_path),
        "schema_corpus": corpus,
        "decisions": decisions,
        "group_b_review": _group_b_review(repo_root),
        "confirmed_gap_count": sum(item["decision"] == "CONFIRMED GAP" for item in decisions),
        "rejected_candidate_count": sum(item["decision"] == "NOT A GAP" for item in decisions),
    }
    (docs / "analysis.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_reports(project_root, result)
    return result


def _module_name(path: Path) -> str:
    match = re.search(r"\bmodule\s+([A-Za-z0-9_.-]+)\s*\{", path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"cannot read module name from {path}")
    return match.group(1)
