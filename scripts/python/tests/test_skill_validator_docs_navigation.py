"""Regression coverage for final skill documentation navigation sections."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.skill_validator.checks import check_docs_last_section

pytestmark = pytest.mark.unit


def _write_skill(skill_dir: Path, body: str) -> Path:
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(body, encoding="utf-8")
    return skill_file


def test_docs_is_accepted_as_the_final_section(tmp_path: Path) -> None:
    """Keep the existing Docs navigation heading accepted."""
    skill_file = _write_skill(
        tmp_path / "docs-skill",
        "# Example Skill\n\n## Docs\n\n- [Guide](guide.md)\n",
    )

    result = check_docs_last_section(skill_file.parent)

    assert result.passed
    assert result.detail == "Last H2 section is '## Docs'"


def test_references_link_to_local_index_is_accepted_as_the_final_section(
    tmp_path: Path,
) -> None:
    """Accept References navigation linking to the local reference index."""
    skill_dir = tmp_path / "references-skill"
    reference_dir = skill_dir / "reference"
    reference_dir.mkdir(parents=True)
    (reference_dir / "README.md").write_text(
        "# Reference Index\n", encoding="utf-8"
    )
    skill_file = _write_skill(
        skill_dir,
        "# Example Skill\n\n## References\n\n"
        "- [Reference index](reference/README.md)\n",
    )

    result = check_docs_last_section(skill_file.parent)

    assert (reference_dir / "README.md").is_file()
    assert result.passed
    assert result.detail == "Last H2 section is '## References'"


def test_unrelated_final_heading_is_rejected(tmp_path: Path) -> None:
    """Reject a final H2 heading that is not a navigation section."""
    skill_file = _write_skill(
        tmp_path / "unrelated-skill",
        "# Example Skill\n\n## Docs\n\n- [Guide](guide.md)\n\n"
        "## Overview\n\nOther content.\n",
    )

    result = check_docs_last_section(skill_file.parent)

    assert not result.passed
    assert result.detail == (
        "Last H2 section is '## Overview', expected '## Docs' or "
        "'## References'"
    )


def test_missing_final_section_is_rejected(tmp_path: Path) -> None:
    """Reject a skill document with no H2 navigation section."""
    skill_file = _write_skill(
        tmp_path / "missing-section-skill", "# Example Skill\n\nBody only.\n"
    )

    result = check_docs_last_section(skill_file.parent)

    assert not result.passed
    assert result.detail == "No H2 sections found in SKILL.md"
