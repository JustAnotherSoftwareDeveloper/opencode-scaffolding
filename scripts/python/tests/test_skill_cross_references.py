"""Check explicit skill loading and the skill-to-document reference contract."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"
CROSS_REFERENCE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*) -> ([^`\n]+)`")
CONSUMERS = (
    "skill-script-bash-writer",
    "skill-script-bash-test-writer",
    "skill-script-node-writer",
    "skill-script-node-test-writer",
    "skill-factory",
    "skill-reviewer",
    "generic-executor",
    "plan-writer",
    "breakdown-tasks",
    "plan-audit",
)


@pytest.mark.parametrize("consumer", CONSUMERS)
def test_cross_references_resolve_within_the_named_passive_skill(
    consumer: str,
) -> None:
    """Verify each skill reference resolves within its named workspace."""
    source = SKILLS / consumer / "SKILL.md"
    references = list(
        CROSS_REFERENCE.finditer(source.read_text(encoding="utf-8"))
    )
    assert references, (
        f"{source}: expected explicit skill-to-document references"
    )

    for match in references:
        name, destination = match.groups()
        workspace = SKILLS / name
        entry_point = workspace / "SKILL.md"
        assert entry_point.is_file(), (
            f"{source}: unknown referenced skill {name}"
        )
        entry_text = entry_point.read_text(encoding="utf-8")
        metadata = yaml.safe_load(entry_text.split("---", 2)[1])
        assert metadata["name"] == name
        assert metadata["class"] in {"planning", "documentation"}

        document, separator, fragment = destination.partition("#")
        if document:
            path = Path(document)
            assert not path.is_absolute() and ".." not in path.parts
            assert path.suffix == ".md"
            target = (workspace / path).resolve()
            assert target.is_relative_to(workspace.resolve())
            assert target.is_file(), (
                f"{source}: missing destination {destination}"
            )
            target_text = target.read_text(encoding="utf-8")
        else:
            assert separator and fragment
            target_text = entry_text

        if separator:
            headings = re.findall(r"^#{1,6}\s+(.+)$", target_text, re.MULTILINE)
            anchors = {
                re.sub(r"[^\w-]", "", heading.lower().replace(" ", "-"))
                for heading in headings
            }
            assert fragment in anchors, (
                f"{source}: missing heading {destination}"
            )


@pytest.mark.parametrize("workflow", ("plan-writer", "breakdown-tasks"))
def test_planning_and_documentation_require_actual_skill_tool_loads(
    workflow: str,
) -> None:
    """Verify planning workflows load selected skills through the skill tool."""
    text = (SKILLS / workflow / "SKILL.md").read_text(encoding="utf-8")
    planning = text.split("**Select and load planning skills.**", 1)[1].split(
        "**Collect operation and documentation skills.**", 1
    )[0]
    planning = " ".join(planning.split())
    assert "skill tool" in planning
    assert "load failure" in planning
    assert "substitute for loading" in planning

    verification = " ".join(
        text.split("**Verify selected contracts.**", 1)[1].split()
    )
    assert "Load each selected documentation skill" in verification
    assert "skill tool before relying on its guidance" in verification
    assert "reading its `SKILL.md` is not a load" in verification
    assert "Do not load planning skills" not in text


def test_cross_reference_policy_is_indexed_and_loads_before_resolution() -> (
    None
):
    """Verify cross-reference guidance is indexed and loaded before use."""
    policy = SKILLS / "skill-authoring-guide/reference/cross-references.md"
    text = policy.read_text(encoding="utf-8")
    index = (SKILLS / "skill-authoring-guide/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "./reference/cross-references.md" in index
    assert (
        "Load that skill through the skill tool before relying on its guidance"
        in text
    )
    assert "does not satisfy this step" in text
    assert "does not load transitively" in text
    assert "heading fragment" in text
    assert (
        "Do not use relative Markdown hyperlinks into sibling skill directories"
        in text
    )


def test_audit_loads_documentation_and_uses_a_dedicated_evidence_directory(  # noqa: E501
) -> None:
    """Verify audits load task-contract guidance and use dedicated evidence."""
    text = (SKILLS / "plan-audit/SKILL.md").read_text(encoding="utf-8")
    text = " ".join(text.split())
    assert "load the exact fresh `task-contract` documentation winner" in text
    assert "skill tool before semantic checks" in text
    assert "reading `SKILL.md` is not a substitute for a load" in text
    assert "dedicated evidence directory such as `.evidence/`" in text
    assert "not as loose files in the workspace root" in text


def test_offloading_audit_reports_live_in_evidence_not_the_repository_root(  # noqa: E501
) -> None:
    """Verify offloading audit reports stay under the evidence directory."""
    assert not list(ROOT.glob("static-operation-skill-offloading-*audit*.md"))
