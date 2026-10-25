"""Check explicit skill loading and the skill-to-document reference contract."""

from __future__ import annotations

import re
import subprocess
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
    planning_start = text.split("**Select and load planning skills.**", 1)[1]
    planning_sections = re.split(
        r"\*\*Collect operation skills(?: once per request)?\.\*\*",
        planning_start,
        maxsplit=1,
    )
    assert len(planning_sections) == 2
    planning = planning_sections[0]
    planning = " ".join(planning.split())
    assert "skill tool" in planning
    assert "load failure" in planning
    assert "substitute for loading" in planning

    assert text.index("**Collect documentation skills") < text.index(
        "**Load the shared task contract before authoring"
    )

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


def test_plan_audit_routes_to_audit_directory() -> None:
    """Verify audits load task-contract guidance and use the audit directory."""
    text = (SKILLS / "plan-audit/SKILL.md").read_text(encoding="utf-8")
    text = " ".join(text.split())
    assert "load the exact fresh `task-contract` documentation winner" in text
    assert "skill tool before semantic checks" in text
    assert "reading `SKILL.md` is not a substitute for a load" in text
    assert (
        "`auditOutput` resolves beneath the repository-root `.audit/` directory"
        in text
    )
    assert (
        "Keep the report external to all audited trees and beneath the "
        "repository-root "
        "`.audit/` directory"
    ) in text
    assert "Do not create the parent, overwrite an existing report" in text
    assert ".analysis/" not in text


def test_skill_review_reports_use_the_audit_directory() -> None:
    """Verify skill reviews publish reports under repository-root .audit/."""
    text = " ".join(
        (SKILLS / "skill-reviewer/SKILL.md").read_text(encoding="utf-8").split()
    )
    report_route = text.split("Publish one conformance report", 1)[1].split(
        "## Self-Validation", 1
    )[0]
    assert "repository-root `.audit/<epoch-ms>-<slug>.md`" in text
    assert "The conformance report is under repository-root `.audit/`" in text
    assert "Do not use this destination for ordinary analyses" in text
    assert ".analysis/" not in report_route


def test_generic_analysis_audit_and_analysis_routes() -> None:
    """Verify only explicit generic audits use .audit, not ordinary analysis."""
    text = (SKILLS / "generic-analysis/SKILL.md").read_text(encoding="utf-8")
    output = text.split("## Output", 1)[1].split("## Analysis Types", 1)[0]
    ordinary_route, audit_route = output.split("- **Audit/review report:**", 1)
    audit_route = audit_route.split("\nDerive `<summary-slug>`", 1)[0]

    assert "Ordinary analysis (default)" in ordinary_route
    assert (
        "$CWD/.analysis/<unix-epoch-milliseconds>-<summary-slug>.md"
        in ordinary_route
    )
    assert (
        "only when the user explicitly requests a final audit or review report"
        in audit_route
    )
    assert (
        "directly under repository-root "
        "`.audit/<unix-epoch-milliseconds>-<summary-slug>.md`"
    ) in audit_route
    assert ".analysis/" not in audit_route


def test_audit_directory_is_ignored() -> None:
    """Verify the repository ignore rule excludes audit reports."""
    ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    ignore_rules = ignore_text.splitlines()
    assert ".audit/" in ignore_rules
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "--verbose",
            "--no-index",
            ".audit/audit-routing-regression.md",
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert ".gitignore" in result.stdout
    assert ".audit/" in result.stdout


def test_offloading_audit_reports_do_not_live_in_the_repository_root() -> None:
    """Verify offloading audit reports are not loose root files."""
    assert not list(ROOT.glob("static-operation-skill-offloading-*audit*.md"))
