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


def test_commands_select_project_without_changing_working_directory() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("uv run --project ~/.config/opencode/scripts/python") == 4


def test_validate_step_uses_auto_fix_loop() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "validate-task-structure" in text
    assert "--auto-fix" in text
    assert '--state-file "$PUBLISHED_PATH"' in text
    assert "retry" in text


def test_guardrails_prohibit_swap_and_recollection() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "Do not swap" in text
    assert "Do not recollect" in text
    assert "Do not manually populate" in text


def test_candidate_boundaries_precede_skill_assignment() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    draft = text.index("Establish candidate boundaries")
    assignment = text.index("Assign skills to each task")
    assert draft < assignment
    assert "without changing the established boundaries" in text
    assert "Give each task a unique `taskId`" in text
    assert "populate `verificationCoverage`" in text


def test_task_count_is_uncapped_and_skill_count_is_separate() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "regardless of task count" in text
    assert "Do not cap, target, or pad the number of tasks" in text
    assert "one-to-three limit applies to `skills` within each task" in text


def test_split_or_migration_is_revalidated_before_publication() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "after any split or migration" in text
    assert "revalidate boundaries, mappings, dependencies, and skills" in text
    assert text.index("Validate and fix") < text.index("Output Contract")


def test_staged_diagnostics_are_actionable() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "warnings before hard failure" in text
    assert "Exit 0 with diagnostics" in text
    assert "Exit 1" in text and "fix the JSON, retry" in text
