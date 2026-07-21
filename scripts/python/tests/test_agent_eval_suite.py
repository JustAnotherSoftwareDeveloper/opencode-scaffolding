"""Tests for agent_eval_suite CLI and core functionality."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.agent_eval_suite import main
from lib.agent_eval_suite.core import (
    CASES,
    EvalCase,
    FrameworkStatus,
    list_cases,
    preflight_frameworks,
    run_inspect_eval,
    run_terminal_bench,
    write_inspect_task,
)


def test_eval_case_structure() -> None:
    """Verify EvalCase dataclass has expected fields."""
    case = CASES[0]
    assert isinstance(case.case_id, str)
    assert isinstance(case.category, str)
    assert isinstance(case.prompt, str)
    assert isinstance(case.required_terms, tuple)
    assert isinstance(case.forbidden_terms, tuple)


def test_list_cases_returns_serializable() -> None:
    """Verify list_cases returns a list of dictionaries."""
    cases = list_cases()
    assert isinstance(cases, list)
    assert len(cases) > 0
    for case in cases:
        assert isinstance(case, dict)
        assert "case_id" in case
        assert "category" in case


def test_write_inspect_task(tmp_path: Path) -> None:
    """Verify write_inspect_task creates a valid Python file."""
    output_path = tmp_path / "eval_task.py"
    result_path = write_inspect_task(output_path)
    assert result_path.exists()
    assert result_path.is_file()
    content = result_path.read_text()
    assert "from inspect_ai" in content
    assert "@task" in content


def test_cases_have_required_fields() -> None:
    """Verify all cases have all required fields populated."""
    for case in CASES:
        assert len(case.case_id) > 0
        assert len(case.category) > 0
        assert len(case.prompt) > 0
        assert len(case.required_terms) > 0
