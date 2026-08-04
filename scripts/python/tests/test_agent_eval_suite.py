"""Tests for agent_eval_suite CLI and core functionality."""

from __future__ import annotations

from pathlib import Path

from lib.agent_eval_suite.core import (
    CASES,
    list_cases,
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


def test_worker_contract_cases_cover_required_categories() -> None:
    """Verify smart supervision and flexible worker cases remain covered."""
    case_ids = {case.case_id for case in CASES}
    assert {
        "delegator_semantic_review",
        "delegator_in_memory_correction",
        "delegator_feedback_redecomposition",
        "delegator_report_review",
        "delegator_non_convergence",
        "executor_plan_immutability",
        "worker_minimum_resources",
        "worker_flexible_resources",
        "worker_authoritative_fields",
        "worker_malformed_evidence",
        "worker_report_repair",
        "worker_continuation",
        "worker_list_envelope",
        "worker_no_op",
        "worker_unavailable_skill",
        "worker_blocked_input",
        "worker_decomposition_false_completion",
    } <= case_ids
