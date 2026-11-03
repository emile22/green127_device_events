from __future__ import annotations

import json
from typing import Any


def render_processing(result: dict[str, Any], *, details: bool = False) -> str:
    lines = [
        "GREEN Controller Processing Summary",
        "",
        "COLLECTED OBSERVATIONS",
        json.dumps(result["collected_observations"], ensure_ascii=False),
        "",
        "NORMALIZED ENERGY OBJECTS",
        f"{len(result['filtered_energy_objects'])} objects retained; missing leaves remain absent.",
        "",
        "RELATIONSHIP-DERIVED CONTEXT",
        json.dumps(result["relationship_context"]["relationships_by_type"], ensure_ascii=False),
        f"Explicit metering roots traversed: {len(result['relationship_context']['metering_paths'])}.",
        "",
        "DERIVED / AGGREGATED VALUES",
        json.dumps(result["derived_values"], indent=2, ensure_ascii=False),
        "",
        "PROVENANCE SUMMARY",
        f"{len(result['provenance'])} derived/incomplete records; each includes source paths, inputs, transformations, and relationship edges.",
        "",
        "UC-SPECIFIC RECOMMENDATIONS",
        *[f"- {item['uc']}: {item['recommendation']} [{item['execution_status']}]" for item in result["recommendations"]],
        "",
        "REPRESENTATION COVERAGE",
        json.dumps(result["coverage"], ensure_ascii=False),
        "Coverage classifications are evidence only; no YANG gaps or GAP IDs are assigned.",
    ]
    if details:
        lines.extend(["", "FULL PROCESSING RECORD", json.dumps(result, indent=2, ensure_ascii=False)])
    return "\n".join(lines)
