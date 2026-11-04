from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from green_gap_tool.analyze import analyze
from green_gap_tool import cli
from green_gap_tool.schema_inventory import scan_repository_yang


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent


@pytest.fixture(scope="module")
def analysis_result():
    return analyze(PROJECT_ROOT)


def test_actual_schema_inventory_finds_expected_modules_and_absent_controller_models() -> None:
    inventory = scan_repository_yang(PROJECT_ROOT)
    modules = {item["module"] for item in inventory["unique_module_revisions"]}
    assert {"ietf-power-and-energy", "ietf-hardware", "iana-power-and-energy", "iana-hardware"} <= modules
    assert inventory["expected_modules"]["ietf-green-controller"] == "not found in repository YANG corpus"
    assert inventory["expected_modules"]["ietf-network-topology"] == "not found in repository YANG corpus"


def test_cli_without_subcommand_defaults_to_analyze_and_identifies_inputs(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        cli,
        "analyze",
        lambda project_root: {
            "decisions": [],
            "confirmed_gap_count": 0,
            "rejected_candidate_count": 0,
            "group_b_review": [],
            "schema_corpus": {"unique_module_revisions": []},
        },
    )

    assert cli.main([]) == 0
    output = capsys.readouterr().out
    assert "Analyzing ctrlrun7/docs/green8_input.json" in output
    assert "repository YANG schema corpus" in output


def test_report_does_not_repeat_decision_prefix_in_rationale(tmp_path, monkeypatch, capsys) -> None:
    project_root = tmp_path / "gaprun8"
    cli_path = project_root / "src" / "green_gap_tool" / "cli.py"
    cli_path.parent.mkdir(parents=True)
    cli_path.touch()
    docs = project_root / "docs"
    docs.mkdir()
    (docs / "analysis.json").write_text(
        json.dumps(
            {
                "confirmed_gap_count": 0,
                "decisions": [
                    {
                        "gap": {},
                        "candidate": {"uc": "UC 2.1"},
                        "decision": "NOT A GAP",
                        "rationale": "NOT A GAP: Existing YANG covers this requirement.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "__file__", str(cli_path))

    assert cli.main(["report"]) == 0
    output = capsys.readouterr().out
    assert output.count("NOT A GAP") == 1
    assert "Existing YANG covers this requirement." in output


def test_analysis_checks_every_green7_candidate_and_confirms_only_battery_soc(analysis_result) -> None:
    decisions = analysis_result["decisions"]
    assert len(decisions) == 14
    confirmed = [item for item in decisions if item["decision"] == "CONFIRMED GAP"]
    assert len(confirmed) == 1
    assert confirmed[0]["gap"]["gap_id"] == "GAP-001"
    assert confirmed[0]["candidate"]["uc"] == "UC 2.14"
    assert confirmed[0]["gap"]["category"] == "STATE-GAP"
    assert all(item["decision"] == "NOT A GAP" for item in decisions if item is not confirmed[0])
    assert len(analysis_result["group_b_review"]) == 2


def test_upstream_copies_are_byte_identical_and_experimental_node_has_traceability(analysis_result) -> None:
    upstream = PROJECT_ROOT / "yang" / "upstream"
    sources = REPOSITORY_ROOT / "allrun5" / "yang"
    copied = sorted(upstream.glob("*.yang"))
    assert len(copied) == 6
    for path in copied:
        assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256((sources / path.name).read_bytes()).digest()
    experimental = list((PROJECT_ROOT / "yang" / "experimental").glob("*.yang"))
    assert [path.name for path in experimental] == ["example-green-power-energy-gaps.yang"]
    text = experimental[0].read_text(encoding="utf-8")
    assert "GAP-001" in text
    assert "config false;" in text
    container_section = text.split("container battery-state-of-charge", 1)[1].split("leaf status", 1)[0]
    status_section = text.split("leaf status", 1)[1].split("leaf state-of-charge-percent", 1)[0]
    percent_section = text.split("leaf state-of-charge-percent", 1)[1]
    assert "GAP-001" in container_section
    assert "GAP-001" in status_section
    assert "GAP-001" in percent_section
    assert 'range "0..100"' in percent_section
    assert 'units "percent"' in percent_section
    assert not re.search(r"GAP-00[2-9]", text)


def test_representative_state_distinguishes_zero_unknown_and_unavailable() -> None:
    state = json.loads((PROJECT_ROOT / "examples" / "representative-state.json").read_text(encoding="utf-8"))
    items = state["ietf-power-and-energy:energy-objects"]["energy-object"]
    states = [item["example-green-power-energy-gaps:battery-state-of-charge"] for item in items]
    assert states[0]["state-of-charge-percent"] == 15.0
    assert states[1]["state-of-charge-percent"] == 0.0
    assert states[2]["status"] == "unknown" and "state-of-charge-percent" not in states[2]
    assert states[3]["status"] == "unavailable" and "state-of-charge-percent" not in states[3]


def test_analysis_reports_include_candidate_decisions_and_tree_artifacts(analysis_result) -> None:
    docs = PROJECT_ROOT / "docs"
    assert (docs / "analysis.json").is_file()
    assert (docs / "yang_tree_before.txt").is_file()
    for name in (
        "confirmed_gaps.md",
        "rejected_gap_candidates.md",
        "yang_gap_matrix.md",
        "modeling_decisions.md",
        "upstream_change_proposals.md",
    ):
        assert (docs / name).is_file()
    rejected = (docs / "rejected_gap_candidates.md").read_text(encoding="utf-8")
    assert "UC 2.3" in rejected and "UC 2.4" in rejected
    assert "GAP-" not in rejected
    assert "Decision: NOT A GAP. NOT A GAP:" not in rejected
    matrix = (docs / "yang_gap_matrix.md").read_text(encoding="utf-8")
    table_rows = [line for line in matrix.splitlines() if line.startswith("|")]
    assert all(len(line) <= 240 for line in table_rows)
    assert matrix.index("## Use Case Names") < matrix.index("## Summary")
    summary = matrix.split("## Summary", 1)[1].split("## Candidate Details", 1)[0]
    summary_table_lines = [line for line in summary.splitlines() if line.startswith("|")]
    summary_headers = [cell.strip() for cell in summary_table_lines[0].split("|")[1:-1]]
    assert summary_headers[2] == "Gap?"
    first_candidate_cells = [cell.strip() for cell in summary_table_lines[2].split("|")[1:-1]]
    assert first_candidate_cells[:3] == [
        "UC 2.1",
        "U1-0, U1-1, U1-2, U1-3, U1-4, U1-5, U1-6, U1-7",
        "No",
    ]
    assert "UC 2.1: Incremental Application of the GREEN Framework" not in summary
    summary_cells = [
        [cell.strip() for cell in line.split("|")[1:-1]]
        for line in summary_table_lines[2:]
    ]
    summary_uc_ids = [cells[0] for cells in summary_cells]
    assert "UC 2.3" in summary_uc_ids and "UC 2.4" in summary_uc_ids
    group_b_rows = [cells for cells in summary_cells if cells[0] in {"UC 2.3", "UC 2.4"}]
    confirmed_row = next(cells for cells in summary_cells if cells[0] == "UC 2.14")
    assert all(cells[2] == "Deferred" and cells[4] == "underspecified" for cells in group_b_rows)
    assert confirmed_row[2] == "Yes" and confirmed_row[5] == "GAP-001"
    assert all(cells[2] == "No" for cells in summary_cells if cells[0] not in {"UC 2.3", "UC 2.4", "UC 2.14"})
    assert "NOT A GAP" not in summary
    assert "insufficient operational detail" not in summary
    pipe_positions = [
        tuple(index for index, character in enumerate(line) if character == "|")
        for line in summary_table_lines
    ]
    assert len(set(pipe_positions)) == 1
    assert "- Requirement:" in matrix and "- Existing module/path:" in matrix
    assert "- Rationale:" in matrix and "- Test:" in matrix


def test_experimental_module_passes_pyang() -> None:
    module = PROJECT_ROOT / "yang" / "experimental" / "example-green-power-energy-gaps.yang"
    result = subprocess.run(
        [sys.executable, "-m", "pyang", "-p", str(PROJECT_ROOT / "yang" / "upstream"), str(module)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
