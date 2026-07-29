"""Regression checks for workflow authority and immutable audit phases."""

from pathlib import Path  # noqa: I001


WORKFLOW = Path(__file__).parents[1] / "SKILL.md"


def test_phase_c_is_read_only_and_reuses_frozen_inventory() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    phase_c = text[text.index("## Phase C"):text.index("## Phase D")]
    compact = " ".join(phase_c.split())
    assert "`collect-skills` again" in phase_c
    assert "without mutating any skill array" in compact
    assert "Do not replace or remove assignments" in phase_c


def test_phase_d_blocks_without_auto_fix() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    phase_d = text[text.index("## Phase D"):text.index("## Output Contract")]
    assert "Do not pass `--auto-fix`" in phase_d
    assert "Treat every validation error as blocking" in phase_d
    assert "Do not trim, deduplicate" in phase_d


def test_phase_b_uses_one_caller_root_inventory_and_real_diagnostics() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    phase_b = text[text.index("## Phase B"):text.index("## Phase C")]
    assert phase_b.count("collect-skills") == 1
    assert '--project-root "$CALLER_ROOT"' in phase_b
    assert '--skills-file "$SKILL_INVENTORY"' in phase_b
    assert '--diagnostics-file "$RANKING_DIAGNOSTICS"' in phase_b
    assert "mktemp -d" in phase_b
