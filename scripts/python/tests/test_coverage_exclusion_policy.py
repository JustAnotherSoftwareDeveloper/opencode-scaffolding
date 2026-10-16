"""Probe built-in coverage exclusions with executable test fixtures."""

from __future__ import annotations

import io
import re
from pathlib import Path

import coverage
import pytest
from coverage.results import should_fail_under

_PROBE_SOURCE = """\
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    TYPE_ONLY_VALUE = "not executed"

def deferred_body() -> None:
    ...
"""


@pytest.mark.unit
def test_builtin_exclusion_forms_remain_reportable(tmp_path: Path) -> None:
    """Require TYPE_CHECKING and ellipsis statements to remain measurable."""
    assert coverage.__version__ == "7.14.3"

    probe_path = tmp_path / "coverage_exclusion_probe.py"
    probe_path.write_text(_PROBE_SOURCE, encoding="utf-8")
    source_lines = _PROBE_SOURCE.splitlines()
    type_guard_line = source_lines.index("if TYPE_CHECKING:") + 1
    type_body_source = '    TYPE_ONLY_VALUE = "not executed"'
    type_body_line = source_lines.index(type_body_source) + 1
    function_line = source_lines.index("def deferred_body() -> None:") + 1
    ellipsis_line = source_lines.index("    ...") + 1

    namespace: dict[str, object] = {"__name__": "coverage_exclusion_probe"}
    exec(compile(_PROBE_SOURCE, str(probe_path), "exec"), namespace)
    assert "TYPE_ONLY_VALUE" not in namespace
    assert callable(namespace["deferred_body"])

    reporter = coverage.Coverage(
        config_file=str(Path(__file__).resolve().parents[1] / "pyproject.toml"),
        data_file=str(tmp_path / ".coverage.probe"),
        source=[str(tmp_path)],
    )
    exclusions = reporter.get_exclude_list()
    for line_number in (type_guard_line, type_body_line, ellipsis_line):
        line = source_lines[line_number - 1]
        assert not any(re.search(pattern, line) for pattern in exclusions)

    # Only module-level lines are recorded; the TYPE_CHECKING body and uncalled
    # function body are deliberately absent from execution data.
    reporter.get_data().add_lines(
        {str(probe_path): {1, type_guard_line, function_line}}
    )
    _, statements, excluded, missing, missing_formatted = reporter.analysis2(
        str(probe_path)
    )
    unexecuted_lines = {type_body_line, ellipsis_line}
    assert unexecuted_lines <= set(statements)
    assert unexecuted_lines.isdisjoint(excluded)
    assert unexecuted_lines <= set(missing)
    assert all(str(line) in missing_formatted for line in unexecuted_lines)

    report = io.StringIO()
    reporter.config.fail_under = 100
    percentage = reporter.report(
        [str(probe_path)],
        show_missing=True,
        file=report,
    )
    assert percentage < 100
    assert should_fail_under(
        percentage,
        reporter.config.fail_under,
        reporter.config.precision,
    )
    for line_number in unexecuted_lines:
        assert str(line_number) in report.getvalue()
