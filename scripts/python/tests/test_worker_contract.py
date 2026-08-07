"""Regression tests for the worker planning and assignment contract."""

from pathlib import Path

ROOT = Path(__file__).parents[3]


def read(relative: str) -> str:
    return (ROOT / relative).read_text()


def test_worker_reports_planning_context_separately() -> None:
    worker = read("agents/worker.md")
    contract = read("output-contract-template.md")
    assert "load every materially relevant planning" in worker
    assert "separately" in worker
    assert "Planning context loaded" in contract
    assert "successfully loaded executable skill" in contract


def test_worker_requires_bounded_assignments_and_two_pass_reconciliation() -> None:
    content = read("agents/worker.md")
    assert "one to three executable assignments" in content
    assert "collector-winning existing `SKILL.md` path" in content
    assert "reconcile one to three executable assignments" in content
    assert "Any stale path" in content


def test_delegation_uses_flexible_resource_semantics_and_list_envelope() -> None:
    content = read("skills/task-delegation/SKILL.md")
    assert "Stale paths" in content
    assert "minimums" in content
    assert "strong suggestions" in content
    assert "output-contract-template.md" in content
    assert "sole authority" in content
    assert "do not maintain a second grammar" in content
    assert "malformed report" in content


def test_executor_preserves_approved_plan_without_status_only_routing() -> None:
    content = read("agents/executor.md")
    assert "approved `{summary, tasks}` plan" in content
    assert "complete report" in content
    assert "Status is a routing signal" in content
    assert "sole acceptance criterion" in content
    assert "Do not reorder, combine, or parallelize tasks" in content


def test_inline_execution_does_not_turn_planning_into_authority() -> None:
    content = read("skills/task-executor/SKILL.md")
    assert "no passive planning-load exception" in content
    assert "Load exactly those declared skills" in content
    assert "stale, substituted, or non-winning paths block" in content
    assert "post-execution pass" in content
