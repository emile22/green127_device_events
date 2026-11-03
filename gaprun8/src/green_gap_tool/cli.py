from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from green_gap_tool.analyze import analyze
from green_gap_tool.schema_inventory import repository_root
from green_gap_tool.validate import validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-based GREEN YANG gap analysis and validation")
    commands = parser.add_subparsers(dest="command", required=False)
    commands.add_parser("analyze", help="inspect green7 candidates against actual YANG schemas")
    commands.add_parser("validate", help="validate copied upstream and experimental YANG/data")
    commands.add_parser("report", help="summarize the latest machine-readable analysis")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "analyze"
    project_root = Path(__file__).resolve().parents[2]
    try:
        if command == "analyze":
            print(
                "Analyzing ctrlrun7/docs/green8_input.json against the current repository YANG schema corpus.",
                flush=True,
            )
            result = analyze(project_root)
            print(f"Analyzed {len(result['decisions'])} green7 candidates against {len(result['schema_corpus']['unique_module_revisions'])} unique module revisions.")
            print(f"Confirmed gaps: {result['confirmed_gap_count']}; rejected candidates: {result['rejected_candidate_count']}; Group B reviews: {len(result['group_b_review'])}.")
            print("Reports: docs/confirmed_gaps.md, docs/rejected_gap_candidates.md, docs/yang_gap_matrix.md")
            return 0
        if command == "validate":
            print(
                "Validating copied upstream and experimental YANG modules plus representative data.",
                flush=True,
            )
            result = validate(project_root)
            failed = [item for item in result["pyang"] if item["status"] != "passed"]
            yanglint_status = result["yanglint"]["status"]
            print(f"pyang: {len(result['pyang']) - len(failed)}/{len(result['pyang'])} modules passed")
            print(f"upstream hashes: {sum(item['matches_allrun5'] for item in result['upstream_hashes'])}/{len(result['upstream_hashes'])} unchanged")
            print(f"yanglint representative data: {yanglint_status}")
            if failed or yanglint_status == "failed":
                return 1
            return 0
        analysis_path = project_root / "docs" / "analysis.json"
        if not analysis_path.is_file():
            print("Run `python -m green_gap_tool analyze` first.", file=sys.stderr)
            return 2
        result = json.loads(analysis_path.read_text(encoding="utf-8"))
        print(f"Confirmed gaps: {result['confirmed_gap_count']}")
        for item in result["decisions"]:
            gap_id = item.get("gap", {}).get("gap_id", "-")
            decision = item["decision"]
            rationale = item["rationale"]
            repeated_prefix = f"{decision}: "
            if rationale.startswith(repeated_prefix):
                rationale = rationale[len(repeated_prefix) :]
            print(f"{gap_id} {item['candidate']['uc']}: {decision} - {rationale}")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
