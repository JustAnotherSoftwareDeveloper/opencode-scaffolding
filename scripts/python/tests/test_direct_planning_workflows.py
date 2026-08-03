"""Contract checks for the shared direct-selection workflow semantics."""

from pathlib import Path

ROOT = Path(__file__).parents[3]
BREAKDOWN = ROOT / "skills/breakdown-tasks/SKILL.md"
PLAN = ROOT / "skills/plan/SKILL.md"


def test_both_workflows_share_direct_selection_contract() -> None:
    breakdown = BREAKDOWN.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    for text in (breakdown, plan):
        lowered = text.lower()
        assert (
            "one frozen inventory" in lowered
            or "one full inventory snapshot" in lowered
        )
        assert "one to three" in lowered
        assert "no numeric cap" in lowered or "without a numeric cap" in lowered
        assert "no score" in lowered or "never score" in lowered
        assert "atomic" in lowered
    assert "same direct-selection contract" in plan


def test_breakdown_prohibits_obsolete_selection_execution() -> None:
    text = BREAKDOWN.read_text(encoding="utf-8").lower()
    assert "never score" in text
    assert "fallback selector" in text
    assert "collect-skills again" not in text


def test_plan_preserves_sources_and_fail_closed_publication() -> None:
    text = PLAN.read_text(encoding="utf-8").lower()
    assert "never modify source documents" in text
    assert "fail closed" in text
    assert "tasks.md" in text
