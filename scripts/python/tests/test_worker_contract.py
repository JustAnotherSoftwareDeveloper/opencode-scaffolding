"""Regression tests for the worker planning and assignment contract."""

from pathlib import Path

ROOT = Path(__file__).parents[3]


def read(relative: str) -> str:
    return (ROOT / relative).read_text()


def test_worker_reports_planning_context_separately() -> None:
    content = read("agents/worker.md")
    assert (
        "load the uncapped set of\n   materially relevant planning-class profiles"
        in content
    )
    assert "passive planning loads" in content
    assert "Planning context loaded" in content
    assert "Skills loaded` is the executable capability set" in content


def test_worker_requires_bounded_assignments_and_two_pass_reconciliation() -> None:
    content = read("agents/worker.md")
    assert "one to three executable task assignments" in content
    assert "collector-winning\n   skill" in content
    assert "Reconcile in two passes" in content
    assert "stale or substituted paths block" in content


def test_delegation_rejects_stale_paths_and_dynamic_non_planning_loads() -> None:
    content = read("skills/task-delegation/SKILL.md")
    assert "stale paths" in content
    assert "dynamic planning context for any other workflow" in content
    assert "collector-winning paths" in content
    assert "two-pass reconciliation" in content


def test_inline_execution_does_not_turn_planning_into_authority() -> None:
    content = read("skills/task-executor/SKILL.md")
    assert "no passive planning-load exception" in content
    assert "Load exactly those declared skills" in content
    assert "stale, substituted, or non-winning paths block" in content
    assert "post-execution pass" in content
