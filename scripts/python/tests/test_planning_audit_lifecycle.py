"""Release gates for the passive proposal-derived audit lifecycle reference."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills" / "planning-pipeline-architecture"
SKILL = SKILL_ROOT / "SKILL.md"
REFERENCE_ROOT = SKILL_ROOT / "reference"
FIXTURE = (
    ROOT
    / "scripts"
    / "python"
    / "test-data"
    / "planning-audit-lifecycle-selection-cases.json"
)


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", " ".join(value.lower().split()))


def test_selection_fixture_uses_exact_current_owners_and_paths() -> None:
    """Verify the selection fixture names current owners and skill paths."""
    data = _fixture()
    inventory = {item["name"]: item for item in data["inventory"]}
    assert data["schema_version"] == 1
    assert set(inventory) == {
        "planning-pipeline-architecture",
        "proposal",
        "plan-writer",
        "plan-audit",
    }

    for item in data["inventory"]:
        path = ROOT / item["path"]
        assert path == ROOT / "skills" / item["name"] / "SKILL.md"
        assert path.is_file()
        frontmatter = yaml.safe_load(
            path.read_text(encoding="utf-8").split("---", 2)[1]
        )
        assert frontmatter["name"] == item["name"]
        assert frontmatter["class"] == item["class"]

    for case in data["cases"]:
        names = case["expected"]["names"]
        paths = case["expected"]["paths"]
        assert len(names) == len(paths)
        for name, path in zip(names, paths, strict=True):
            assert name in inventory, case["id"]
            assert inventory[name]["path"] == path, case["id"]


def test_proposal_derived_lifecycle_has_the_mandatory_reaudit_loop() -> None:
    """Verify planning preserves its mandatory re-audit loop."""
    text = _text(
        "skills/planning-pipeline-architecture/reference/proposal-derived-audit-lifecycle.md"
    )
    states = [
        "Proposal recorded",
        "Proposal authorization confirmed",
        "Plan authored",
        "Audit pending",
        "Audit passed",
        "Audit findings",
        "Bounded plan-owned correction",
        "Revised plan",
        "Mandatory re-audit",
    ]
    positions = [text.index(state) for state in states]
    assert positions == sorted(positions)
    assert "proposal" in text
    assert "plan-writer" in text
    assert "plan-audit" in text
    assert "mandatory re-audit" in text.lower()
    assert "review-ready" in text
    assert "do not cause this transition" in text
    assert "decision-ready" in text
    assert "recorded\n  `decision-owner`" in text
    collapsed = " ".join(text.split())
    assert (
        "The revised snapshot transitions to **Mandatory re-audit** rather than"
        " directly to a passed state."
    ) in collapsed
    assert "recorded accepted lifecycle state" in collapsed
    assert (
        "`decision-ready` plus explicit planning authorization"
        " from the recorded `decision-owner`."
    ) in collapsed
    assert (
        "Publication, validation, `review-ready`, baseline stability, recency,"
        " and invocation do not cause this transition."
    ) in collapsed


def test_audit_reports_are_external_read_only_and_root_routed() -> None:
    """Verify reports stay outside audited plans and under .audit/."""
    text = _text(
        "skills/planning-pipeline-architecture/reference/proposal-derived-audit-lifecycle.md"
    )
    collapsed = " ".join(text.split())

    assert (
        "`plan-audit` remains an independent, read-only report owner."
        in collapsed
    )
    assert (
        "Every audit report is external to the audited inputs and located under"
        " the repository-root `.audit/`."
    ) in collapsed
    assert "external UTF-8 Markdown audit report" in collapsed
    assert "external report under repository-root `.audit/`" in collapsed
    assert (
        "new external report against the revised immutable snapshot,"
        " stored under repository-root `.audit/`."
    ) in collapsed
    assert "the report does not change the audited plan." in collapsed
    assert (
        "`plan-audit` remains read-only and does not apply or self-certify the"
        " correction."
    ) in collapsed


def test_correction_is_bounded_in_the_same_workspace_before_reaudit() -> None:
    """Verify findings lead to an in-place fix and mandatory re-audit."""
    text = _text(
        "skills/planning-pipeline-architecture/reference/proposal-derived-audit-lifecycle.md"
    )
    collapsed = " ".join(text.split())

    assert (
        "`plan-writer` owns correction of the existing plan workspace's"
        " `tasks.json` and `tasks.md`"
    ) in collapsed
    assert (
        "bounded by the exact finding IDs, proposal decision, source evidence,"
        " and stated impact."
    ) in collapsed
    assert "copied sources and proposal context are preserved" in collapsed
    assert (
        "does not expand the proposal scope or "
        "replace its decision." in collapsed
    )
    assert (
        "`plan-writer` owns the revised snapshot in that same existing"
        " plan workspace"
        in collapsed
    )
    assert (
        "The revised snapshot transitions to **Mandatory re-audit** rather than"
        " directly to a passed state."
    ) in collapsed


def test_proposal_derived_workflows_keep_audits_and_fixes_in_scope() -> None:
    """Verify workflow summaries retain external audits and in-place fixes."""
    references = (
        "skills/planning-pipeline-architecture/reference/proposal-to-plan.md",
        "skills/planning-pipeline-architecture/reference/analysis-to-proposal-to-plan.md",
    )
    for relative in references:
        collapsed = " ".join(_text(relative).split())
        lowered = collapsed.lower()
        assert ".audit/" in collapsed
        assert "same existing plan workspace" in collapsed
        assert "mandatory" in lowered
        assert "re-audit" in lowered
        assert "read-only" in lowered


def test_blocked_handoffs_preserve_exact_needed_input_and_impact() -> None:
    """Verify blocked handoffs specify exact inputs and resulting impacts."""
    data = _fixture()
    text = _text(
        "skills/planning-pipeline-architecture/reference/proposal-derived-audit-lifecycle.md"
    )
    lowered = _normalized(text)
    assert "exact needed input" in lowered
    assert "impact" in lowered
    for handoff in data["blocked_handoffs"]:
        assert handoff["owner"] in text
        assert _normalized(handoff["needed_input"]) in lowered
        assert _normalized(handoff["impact"]) in lowered


def test_direct_plan_only_keeps_publication_without_an_automatic_audit() -> (
    None
):
    """Verify plan-only publication does not trigger an automatic audit."""
    text = _text("skills/planning-pipeline-architecture/reference/plan-only.md")
    lowered = text.lower()
    assert "plan-writer" in text
    assert "publication" in lowered
    assert "does not imply `audit pending`" in lowered
    assert "explicit audit request" in lowered
    assert "mandatory" not in lowered


def test_planning_reference_is_passive_and_non_transitive() -> None:
    """Verify planning references stay passive and non-transitive."""
    files = [SKILL, *sorted(REFERENCE_ROOT.glob("*.md"))]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    forbidden_operational_markers = (
        "collect-skills",
        "init-task-packet",
        "validate-task-structure",
        "render-task-markdown",
        "uv run",
        "```",
    )
    lowered = combined.lower()
    assert all(
        marker not in lowered for marker in forbidden_operational_markers
    )
    assert not re.search(
        r"(?im)^\s*(load|run|write|create|delegate)\s+the\s", combined
    )
    assert "passive" in lowered
    assert "non-transitive" in lowered
    assert "no execution" in lowered
    assert "no fallback assignment" in lowered


def test_planning_reference_links_resolve() -> None:
    """Verify all local links in planning lifecycle references resolve."""
    files = [SKILL, *sorted(REFERENCE_ROOT.glob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            assert (path.parent / target).is_file(), (path, target)
