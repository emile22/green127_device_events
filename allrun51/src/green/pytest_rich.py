from collections import Counter
import time

from rich.console import Console
from rich.table import Table


_collected = 0
_results: dict[str, str] = {}
_started_at = 0.0


def pytest_configure(config) -> None:
    global _collected, _started_at
    _collected = 0
    _results.clear()
    _started_at = time.perf_counter()
    config.option.verbose = -1


def pytest_collection_finish(session) -> None:
    global _collected
    _collected = len(session.items)


def _outcome(report) -> str:
    if hasattr(report, "wasxfail"):
        return "xfailed" if report.skipped else "xpassed"
    return report.outcome


def pytest_report_teststatus(report, config):
    if report.when == "call" or report.failed or report.skipped:
        return _outcome(report), "", ""
    return "", "", ""


def pytest_runtest_logreport(report) -> None:
    if report.when == "call" or report.failed or report.skipped:
        _results[report.nodeid] = _outcome(report)


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    counts = Counter(_results.values())
    table = Table(title=f"Test results ({time.perf_counter() - _started_at:.2f}s)")
    table.add_column("Outcome")
    table.add_column("Tests", justify="right")
    for outcome in ("passed", "failed", "error", "skipped", "xfailed", "xpassed"):
        if counts[outcome]:
            table.add_row(outcome.capitalize(), str(counts[outcome]))
    table.add_section()
    table.add_row("Total", f"{_collected}", style="bold")
    Console().print(table)