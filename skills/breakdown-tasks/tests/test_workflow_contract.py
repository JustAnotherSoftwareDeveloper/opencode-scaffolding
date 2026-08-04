"""Regression checks for workflow authority and procedural commands."""

from pathlib import Path  # noqa: I001


WORKFLOW = Path(__file__).parents[1] / "SKILL.md"


def test_planning_uses_class_planning_filter() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "collect-skills --class planning" in text


def test_operation_uses_class_operation_and_documentation_filters() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "--class operation" in text
    assert "--class documentation" in text


def test_publish_uses_init_task_packet() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "init-task-packet" in text
    assert "--output-dir .tasks" in text


def test_validate_step_uses_auto_fix_loop() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "validate-task-structure" in text
    assert "--auto-fix" in text
    assert "--state-file" in text
    assert "retry" in text


def test_guardrails_prohibit_swap_and_recollection() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "Do not swap" in text
    assert "Do not recollect" in text
    assert "Do not manually populate" in text
