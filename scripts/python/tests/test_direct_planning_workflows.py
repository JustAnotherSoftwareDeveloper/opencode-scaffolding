"""Contract checks for the shared procedural workflow semantics."""

from pathlib import Path

ROOT = Path(__file__).parents[3]
BREAKDOWN = ROOT / "skills/breakdown-tasks/SKILL.md"
PLAN = ROOT / "skills/plan-writer/SKILL.md"


def test_both_workflows_use_two_collector_calls_and_inline_assignment() -> None:
    breakdown = BREAKDOWN.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    for text in (breakdown, plan):
        lowered = text.lower()
        assert "collect-skills --class planning" in text
        assert "--class operation" in text
        assert "--class documentation" in text
        assert "one to three" in lowered
        assert "never score" in lowered or "do not score" in lowered
        assert "init-task-packet" in text
        assert "packet slug" in lowered
        assert "never derive" in lowered


def test_breakdown_prohibits_obsolete_selection_patterns() -> None:
    text = BREAKDOWN.read_text(encoding="utf-8").lower()
    assert "do not score" in text
    assert "do not recollect" in text
    assert "do not manually populate" in text


def test_plan_preserves_sources_and_fail_closed_publication() -> None:
    text = PLAN.read_text(encoding="utf-8").lower()
    assert "never modify source documents" in text
    assert "fail closed" in text
    assert "tasks.md" in text
    assert "validate-task-structure" in text


def test_dispatch_and_display_require_a_canonical_slug_without_derivation() -> None:
    dispatch = (ROOT / "skills/dispatch-decompose/SKILL.md").read_text(encoding="utf-8")
    display = (ROOT / "skills/display-tasks/SKILL.md").read_text(encoding="utf-8")

    assert "select a packet slug" in dispatch
    assert "preserve it unchanged" in dispatch
    assert "including its author-selected packet slug" in display
    assert "Do not restate or\nlocally validate slug grammar" in display
