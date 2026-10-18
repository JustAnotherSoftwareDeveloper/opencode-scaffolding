"""Regression tests for the worker planning and assignment contract."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).parents[3]


def read(relative: str) -> str:
    """Read a repository file as text."""
    return (ROOT / relative).read_text()


def normalized(relative: str) -> str:
    """Read repository prose with case and whitespace normalized."""
    return " ".join(read(relative).split()).casefold()


def test_worker_reports_planning_context_separately() -> None:
    """Verify worker separates planning context from executable skills."""
    worker = normalized("agents/worker.md")
    contract = normalized("output-contract-template.md")
    assert "load every materially relevant planning" in worker
    assert "separately" in worker
    assert "planning context loaded" in contract
    assert "successfully loaded executable skill" in contract


def test_worker_requires_bounded_assignments_and_two_pass_reconciliation() -> (
    None
):
    """Verify workers enforce bounded assignments and reconciliation passes."""
    content = normalized("agents/worker.md")
    assert "one operation owner and zero to two documentation skills" in content
    assert "collector-winning existing `skill.md` path" in content
    assert (
        "reconcile each generated task to exactly one `class: operation` owner"
        in content
    )
    assert "any stale path" in content


def test_delegation_uses_flexible_resource_semantics_and_list_envelope() -> (
    None
):
    """Verify delegation uses flexible resources and the list-based envelope."""
    content = normalized("skills/task-delegation/SKILL.md")
    assert "block on stale or substituted paths" in content
    assert "reads as minimum starting context" in content
    assert "writes as strong suggestions" in content
    assert "output-contract-template.md" in content
    assert "sole authority for the envelope grammar" in content
    assert "do not maintain a second grammar" in content
    assert "malformed report is not a deliverable" in content


def test_executor_preserves_approved_plan_without_status_only_routing() -> None:
    """Verify the executor preserves the plan rather than routing by status."""
    content = normalized("agents/executor.md")
    assert "preserve the approved canonical packet root, packet slug" in content
    assert "preserve the complete validated envelope unchanged" in content
    assert (
        "predecessor `partial` satisfies the edge only when the report clearly "
        "establishes" in content
    )
    assert (
        "dispatch a task only when all of its dependency edges are satisfied"
        in content
    )
    assert (
        "process the approved task graph in packet order, one worker at a time"
        in content
    )


def test_executor_contract_requires_and_preserves_the_supplied_slug() -> None:
    """Verify executor contracts require and preserve the supplied slug."""
    for relative in (
        "agents/executor.md",
        "agents/executor-simple.md",
        "agents/delegator.md",
    ):
        content = normalized(relative)
        assert "slug" in content
        assert "preserve" in content


def test_inline_execution_does_not_turn_planning_into_authority() -> None:
    """Verify inline execution leaves planning context non-authoritative."""
    content = normalized("skills/task-executor/SKILL.md")
    assert "exactly one `class: operation` owner" in content
    assert "zero to two `class: documentation` skills" in content
    assert (
        "no planning, delegated, or inline skill as a task assignment"
        in content
    )
    assert (
        "must not reconstruct collector metadata that is absent from the task "
        "packet" in content
    )
    assert "do not load skills outside the declared `skills` array" in content
