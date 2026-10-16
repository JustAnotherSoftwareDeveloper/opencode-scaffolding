"""Contract checks for the shared procedural workflow semantics."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).parents[3]
BREAKDOWN = ROOT / "skills/breakdown-tasks/SKILL.md"
PLAN = ROOT / "skills/plan-writer/SKILL.md"


def test_both_workflows_use_two_collector_calls_and_inline_assignment() -> None:
    """Verify both planning workflows collect and assign skills inline."""
    breakdown = BREAKDOWN.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    for text in (breakdown, plan):
        lowered = text.lower()
        assert "collect-skills --class planning" in text
        assert "--class operation" in text
        assert "--class documentation" in text
        assert "exactly one `class: operation` execution owner" in lowered
        assert (
            "zero to two materially relevant "
            "`class: documentation` skills" in lowered
        )
        assert "never score" in lowered or "do not score" in lowered
        assert "init-task-packet" in text
        assert "packet slug" in lowered
        assert "never derive" in lowered


def test_breakdown_prohibits_obsolete_selection_patterns() -> None:
    """Verify breakdown-tasks prohibits obsolete selection patterns."""
    text = BREAKDOWN.read_text(encoding="utf-8").lower()
    assert "do not score" in text
    assert "do not recollect" in text
    assert "do not manually populate" in text


def test_plan_preserves_sources_and_fail_closed_publication() -> None:
    """Verify plan-writer preserves sources and fails closed on publication."""
    text = PLAN.read_text(encoding="utf-8").lower()
    assert "never modify source documents" in text
    assert "fail closed" in text
    assert "tasks.md" in text
    assert "validate-task-structure" in text


def test_dispatch_and_display_require_a_canonical_slug_without_derivation() -> (
    None
):
    """Verify dispatch and display preserve the selected slug unchanged."""
    dispatch = (ROOT / "skills/dispatch-decompose/SKILL.md").read_text(
        encoding="utf-8"
    )
    display = (ROOT / "skills/display-tasks/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "select a packet slug" in dispatch
    assert "preserve it unchanged" in dispatch
    assert "including its author-selected packet slug" in display
    assert "Do not restate or\nlocally validate slug grammar" in display


def test_display_tasks_preserves_required_table_exception_contract() -> None:
    """Verify display-tasks retains the required Markdown table contract."""
    display = (ROOT / "skills/display-tasks/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "A single Markdown table with no surrounding commentary." in display
    assert (
        "```markdown\n"
        "| Purpose | Starting files | Suggested outputs | Skills |\n"
        "| ------- | -------------- | ----------------- | ------ |\n"
        "```"
    ) in display
