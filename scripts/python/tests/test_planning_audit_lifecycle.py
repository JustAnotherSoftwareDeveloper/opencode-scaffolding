"""Release gates for the passive proposal-derived audit lifecycle reference."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

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
    text = _text(
        "skills/planning-pipeline-architecture/reference/proposal-derived-audit-lifecycle.md"
    )
    states = [
        "Proposal recorded",
        "Plan authored",
        "Audit pending",
        "Audit passed",
        "Audit findings",
        "Bounded plan-owned fix",
        "Revised plan",
        "Mandatory re-audit",
    ]
    positions = [text.index(state) for state in states]
    assert positions == sorted(positions)
    assert "proposal" in text
    assert "plan-writer" in text
    assert "plan-audit" in text
    assert "mandatory re-audit" in text.lower()
    assert "revised plan transitions to **Mandatory\n  re-audit**" in text


def test_blocked_handoffs_preserve_exact_needed_input_and_impact() -> None:
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


def test_direct_plan_only_keeps_publication_without_an_automatic_audit() -> None:
    text = _text("skills/planning-pipeline-architecture/reference/plan-only.md")
    lowered = text.lower()
    assert "plan-writer" in text
    assert "publication" in lowered
    assert "does not imply `audit pending`" in lowered
    assert "explicit audit request" in lowered
    assert "mandatory" not in lowered


def test_planning_reference_is_passive_and_non_transitive() -> None:
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
    assert all(marker not in lowered for marker in forbidden_operational_markers)
    assert not re.search(r"(?im)^\s*(load|run|write|create|delegate)\s+the\s", combined)
    assert "passive" in lowered
    assert "non-transitive" in lowered
    assert "no execution" in lowered
    assert "no fallback assignment" in lowered


def test_planning_reference_links_resolve() -> None:
    files = [SKILL, *sorted(REFERENCE_ROOT.glob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            assert (path.parent / target).is_file(), (path, target)
