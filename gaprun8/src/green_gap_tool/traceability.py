from __future__ import annotations

from pathlib import Path
from typing import Any


def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    column_widths = [
        max([len(header), *(len(row[column_index]) for row in rows)])
        for column_index, header in enumerate(headers)
    ]

    def format_row(values: list[str]) -> str:
        cells = [value.ljust(column_widths[index]) for index, value in enumerate(values)]
        return "| " + " | ".join(cells) + " |"

    return [
        format_row(headers),
        format_row(["-" * width for width in column_widths]),
        *(format_row(row) for row in rows),
    ]


def write_reports(project_root: Path, analysis: dict[str, Any]) -> None:
    docs = project_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    confirmed = [item for item in analysis["decisions"] if item["decision"] == "CONFIRMED GAP"]
    rejected = [item for item in analysis["decisions"] if item["decision"] == "NOT A GAP"]

    confirmed_lines = ["# Confirmed YANG Gaps", ""]
    if not confirmed:
        confirmed_lines.append("No confirmed YANG gaps were found after schema inspection.")
    for item in confirmed:
        gap = item["gap"]
        confirmed_lines.extend([
            f"## {gap['gap_id']} - {item['candidate']['uc']} {item['candidate']['uc_full_name']}",
            "",
            f"- Events: {', '.join(item['candidate']['event_ids'])}",
            f"- Requirement: {item['candidate']['requirement']}",
            f"- Category: {gap['category']}",
            f"- Scope: {gap['scope']}",
            f"- Confirmed because: {item['rationale']}",
            f"- Local experimental path: `{gap['experimental_path']}`",
            f"- Config: `{gap['config']}`; type/units: `{gap['type_units']}`",
            f"- Test: `{gap['test']}`",
            "",
        ])
    (docs / "confirmed_gaps.md").write_text("\n".join(confirmed_lines).rstrip() + "\n", encoding="utf-8")

    rejected_lines = [
        "# Rejected Gap Candidates",
        "",
        "Each item was checked against the actual repository YANG trees. Rejection means the candidate is represented adequately, is controller-scope, or lacks enough grounded semantic detail; it does not dismiss the use-case requirement.",
        "",
    ]
    for item in rejected:
        candidate = item["candidate"]
        evidence = "; ".join(item["schema_evidence"][:4])
        rejected_lines.extend([
            f"## {candidate['uc']} {candidate['uc_full_name']} ({', '.join(candidate['event_ids'])})",
            f"- Candidate: {candidate['requirement']}",
            f"- Decision: NOT A GAP. {item['rationale']}",
            f"- Schema evidence: {evidence or 'no applicable existing device path required for this controller-side function.'}",
            "",
        ])
    for item in analysis["group_b_review"]:
        rejected_lines.extend([
            f"## {item['uc']} {item['title']} (Group B)",
            f"- Decision: NOT A GAP candidate for this run. {item['rationale']}",
            f"- Modeling topics stated in the draft: {'; '.join(item['modeling_needs_from_text'])}",
            f"- Evidence: {item['source_evidence']}",
            "",
        ])
    (docs / "rejected_gap_candidates.md").write_text("\n".join(rejected_lines).rstrip() + "\n", encoding="utf-8")

    uc_names = [
        (item["candidate"]["uc"], item["candidate"]["uc_full_name"])
        for item in analysis["decisions"]
    ]
    uc_names.extend((item["uc"], item["title"]) for item in analysis["group_b_review"])
    uc_names.sort(key=lambda entry: tuple(int(part) for part in entry[0].removeprefix("UC ").split(".")))

    matrix = [
        "# YANG Gap Matrix",
        "",
        "## Use Case Names",
        "",
    ]
    matrix.extend(_markdown_table(["UC", "Use case name"], [list(item) for item in uc_names]))
    matrix.extend([
        "",
        "## Summary",
        "",
    ])
    summary_rows = []
    for item in analysis["decisions"]:
        candidate = item["candidate"]
        gap = item.get("gap", {})
        summary_rows.append([
            candidate["uc"],
            ", ".join(candidate["event_ids"]),
            "Yes" if item["decision"] == "CONFIRMED GAP" else "No",
            gap.get("scope", candidate["scope"]),
            candidate["coverage"],
            gap.get("gap_id", "-"),
        ])
    for item in analysis["group_b_review"]:
        summary_rows.append([
            item["uc"],
            "-",
            "Deferred",
            "controller/device reporting",
            "underspecified",
            "-",
        ])
    matrix.extend(_markdown_table(
        ["UC", "Events", "Gap?", "Scope", "Coverage before", "GAP ID"],
        summary_rows,
    ))
    matrix.extend(["", "## Candidate Details", ""])
    for item in analysis["decisions"]:
        candidate = item["candidate"]
        gap = item.get("gap", {})
        matrix.extend([
            f"### {candidate['uc']} {candidate['uc_full_name']}",
            "",
            f"- Events: {', '.join(candidate['event_ids'])}",
            f"- Requirement: {candidate['requirement']}",
            f"- Scope: {gap.get('scope', candidate['scope'])}",
            f"- Coverage before: {candidate['coverage']}",
            f"- Confirmed gap?: {'yes' if gap else 'no'}",
            f"- Category: {gap.get('category', '-')}",
            f"- Proposed solution: {gap.get('solution', '-')}",
            f"- Experimental module/path: {gap.get('experimental_path', '-')}",
            f"- Config true/false: {gap.get('config', '-')}",
            f"- Units/type: {gap.get('type_units', '-')}",
            "- Existing module/path:",
        ])
        paths = candidate.get("searched_paths", [])
        matrix.extend([f"  - `{path}`" for path in paths] or ["  - None identified."])
        matrix.extend([
            f"- Rationale: {item.get('rationale', gap.get('rationale', '-'))}",
            f"- Test: {gap.get('test', '-')}",
            "",
        ])
    for item in analysis["group_b_review"]:
        matrix.extend([
            f"### {item['uc']} {item['title']} (Group B)",
            "",
            "- Decision: NOT A GAP candidate for this run.",
            f"- Modeling topics stated in the draft: {'; '.join(item['modeling_needs_from_text'])}",
            f"- Evidence: {item['source_evidence']}",
            "",
        ])
    (docs / "yang_gap_matrix.md").write_text("\n".join(matrix) + "\n", encoding="utf-8")

    decisions = [
        "# Modeling Decisions",
        "",
        f"Confirmed gaps: {len(confirmed)}. Rejected green7 candidates: {len(rejected)}.",
        "",
        "## Local Experimental Augmentation",
        "",
    ]
    if confirmed:
        decisions.extend(f"- {item['gap']['gap_id']}: {item['gap']['solution']}" for item in confirmed)
    else:
        decisions.append("None. No experimental nodes are added unless a candidate passes all gap-rule checks.")
    decisions.extend([
        "",
        "## Possible Future IETF Work",
        "",
        "The existing total-energy-consumed leaf declares units as Watt-hours while its description says mWh. YANG's units statement is machine-readable and is retained as authoritative here; an editorial clarification may be considered separately. This ambiguity was not assigned a GAP ID and was not changed locally.",
        "",
        "All source schemas remain unchanged. The experimental module is local-only and is not an IETF standard.",
    ])
    (docs / "modeling_decisions.md").write_text("\n".join(decisions), encoding="utf-8")

    proposals = [
        "# Upstream Change Proposals",
        "",
        "No confirmed upstream YANG change proposal is produced by this run.",
        "",
        "The `total-energy-consumed` leaf declares `Watt-hours` in its `units` statement but its description says milliwatt-hours. The units statement is the machine-readable contract; the prose inconsistency is recorded as a possible editorial clarification only, not a local module change or confirmed gap.",
        "",
        "Any future IETF proposal must be reviewed separately from the local experimental augmentation and must not be presented as an accepted standard.",
    ]
    (docs / "upstream_change_proposals.md").write_text("\n".join(proposals), encoding="utf-8")
