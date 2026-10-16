"""A skill's Markdown links must not cross into a sibling skill workspace."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

SKILLS = Path(__file__).resolve().parents[3] / "skills"
INLINE_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
REFERENCE_DEFINITION = re.compile(r"^\[[^\]\n]+\]:\s+(\S+)", re.MULTILINE)


def test_skill_workspace_links_do_not_target_other_skill_directories() -> None:
    """Verify skill Markdown links stay within their own workspace."""
    violations: list[str] = []
    for skill_dir in SKILLS.iterdir():
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
            continue
        for source in skill_dir.rglob("*.md"):
            if any(
                part.startswith(".")
                for part in source.relative_to(skill_dir).parts
            ):
                continue
            content = source.read_text(encoding="utf-8")
            for match in (
                *INLINE_LINK.finditer(content),
                *REFERENCE_DEFINITION.finditer(content),
            ):
                destination = match.group(1).split("#", 1)[0].strip("<>")
                if (
                    not destination
                    or ":" in destination
                    or destination.startswith("/")
                ):
                    continue
                target = (source.parent / destination).resolve()
                if target.is_relative_to(SKILLS) and not target.is_relative_to(
                    skill_dir
                ):
                    line = content.count("\n", 0, match.start()) + 1
                    violations.append(
                        f"{source.relative_to(SKILLS)}:{line} -> {destination}"
                    )
    assert not violations, "Cross-skill Markdown links: " + ", ".join(
        violations
    )
