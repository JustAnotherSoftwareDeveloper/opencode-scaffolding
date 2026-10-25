"""Direct unit contracts for skill validation checks and result aggregation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from lib.skill_validator import checks, helpers, registry
from lib.validate_skill_meta import core as meta_core

pytestmark = pytest.mark.unit


def _profile(name: str = "demo-skill", skill_class: str = "operation") -> dict:
    return {
        "name": name,
        "description": "Use when checking a skill profile",
        "class": skill_class,
        "selection": {
            "role": "reference" if skill_class == "documentation" else "owner",
            "tags": {"actions": ["validate"]},
        },
    }


def _write_skill(
    root: Path,
    *,
    name: str = "demo-skill",
    skill_class: str = "operation",
    body: str = "## Docs\nDocumentation.\n",
) -> Path:
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "SKILL.md"
    path.write_text(
        "---\n"
        + yaml.safe_dump(_profile(name, skill_class), sort_keys=False)
        + "---\n"
        + body,
        encoding="utf-8",
    )
    return path


def test_skill_validator_helpers_fail_closed_on_missing_and_invalid_frontmatter(
    tmp_path: Path,
) -> None:
    """Parse frontmatter safely and identify skip directories by path."""
    skill_dir = tmp_path / "missing"
    assert helpers._read_skill_md(skill_dir) is None
    assert helpers._parse_frontmatter("body only") is None
    assert helpers._parse_frontmatter("---\nname: [bad\n---") is None
    assert helpers._parse_frontmatter("---\nname: good\n---") == {
        "name": "good"
    }
    assert helpers._is_in_skip_directory(
        tmp_path / "skill" / "reference" / "guide.md",
        tmp_path / "skill",
        frozenset({"reference"}),
    )
    assert not helpers._is_in_skip_directory(
        tmp_path / "outside.md", tmp_path / "skill", frozenset({"reference"})
    )


def test_frontmatter_check_surfaces_normalization_diagnostics(
    tmp_path: Path,
) -> None:
    """Report invalid metadata without accepting the profile."""
    skill_dir = tmp_path / "invalid-selection"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: invalid-selection\n"
        "description: Use when checking metadata\n"
        "class: operation\nselection: {role: owner, tags: {unknown: [value]}}\n"
        "---\n",
        encoding="utf-8",
    )
    result = checks.check_frontmatter_valid(skill_dir)
    assert result.passed is False
    assert "Selection metadata is invalid" in result.detail


def test_frontmatter_name_description_and_class_checks_report_contracts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Validate required metadata and the class-dependent description prefix."""
    missing = tmp_path / "missing"
    missing.mkdir()
    assert not checks.check_frontmatter_valid(missing).passed
    assert not checks.check_name_matches_dir(missing).passed
    assert not checks.check_description_prefix(missing).passed
    assert not checks.check_class_valid(missing).passed

    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "SKILL.md").write_text("---\nname: [bad\n---\n", encoding="utf-8")
    assert "invalid" in checks.check_frontmatter_valid(bad).detail.lower()
    assert "frontmatter invalid" in checks.check_name_matches_dir(bad).detail
    assert "frontmatter invalid" in checks.check_description_prefix(bad).detail
    assert "frontmatter invalid" in checks.check_class_valid(bad).detail

    missing_scalar = tmp_path / "missing-scalar"
    missing_scalar.mkdir()
    (missing_scalar / "SKILL.md").write_text(
        "---\nname: ''\ndescription: Valid description\n"
        "class: operation\n---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(checks, "normalize_skill_metadata", lambda _: None)
    assert (
        "missing or empty"
        in checks.check_frontmatter_valid(missing_scalar).detail
    )

    bad_syntax = tmp_path / "bad-syntax"
    bad_syntax.mkdir()
    (bad_syntax / "SKILL.md").write_text(
        "---\nname: 'not canonical'\ndescription: Use when checking\n"
        "class: operation\n---\n",
        encoding="utf-8",
    )
    assert "invalid syntax" in checks.check_frontmatter_valid(bad_syntax).detail

    wrong = tmp_path / "actual-dir"
    wrong.mkdir()
    (wrong / "SKILL.md").write_text(
        "---\nname: invalid name\ndescription: bad\nclass: other\n---\n",
        encoding="utf-8",
    )
    assert not checks.check_frontmatter_valid(wrong).passed
    assert not checks.check_name_matches_dir(wrong).passed
    assert not checks.check_description_prefix(wrong).passed
    assert not checks.check_class_valid(wrong).passed

    planning = _write_skill(
        tmp_path,
        name="planning-guide",
        skill_class="planning",
        body="Reference only.\n",
    )
    planning_profile = _profile("planning-guide", "planning")
    planning_profile["description"] = "Use as planning reference for tests"
    planning.write_text(
        "---\n" + yaml.safe_dump(planning_profile, sort_keys=False) + "---\n",
        encoding="utf-8",
    )
    assert checks.check_description_prefix(planning.parent).passed
    assert checks.check_class_valid(planning.parent).passed

    bad_planning = _write_skill(
        tmp_path,
        name="bad-planning",
        skill_class="planning",
        body="Reference only.\n",
    )
    assert not checks.check_description_prefix(bad_planning.parent).passed


def test_docs_examples_and_reference_index_checks_cover_empty_and_present_cases(
    tmp_path: Path,
) -> None:
    """Check final Docs sections, forbidden Examples, and reference indexes."""
    skill = _write_skill(tmp_path)
    assert checks.check_docs_last_section(skill.parent).passed
    assert checks.check_no_examples_section(skill.parent).passed
    assert checks.check_reference_readme_exists(skill.parent).passed

    skill.write_text(
        skill.read_text(encoding="utf-8") + "## Examples\nExample.\n## Later\n",
        encoding="utf-8",
    )
    assert not checks.check_docs_last_section(skill.parent).passed
    assert not checks.check_no_examples_section(skill.parent).passed

    references = skill.parent / "reference"
    references.mkdir()
    assert checks.check_reference_readme_exists(skill.parent).passed
    (references / "guide.md").write_text("# Guide\n", encoding="utf-8")
    missing_index = checks.check_reference_readme_exists(skill.parent)
    assert not missing_index.passed
    assert "README.md" in missing_index.detail
    (references / "README.md").write_text("# Index\n", encoding="utf-8")
    assert checks.check_reference_readme_exists(skill.parent).passed

    empty = tmp_path / "empty"
    empty.mkdir()
    assert not checks.check_docs_last_section(empty).passed
    assert not checks.check_no_examples_section(empty).passed

    no_headings = tmp_path / "no-headings"
    no_headings.mkdir()
    (no_headings / "SKILL.md").write_text("Plain content.\n", encoding="utf-8")
    assert "No H2" in checks.check_docs_last_section(no_headings).detail


def test_voice_and_placeholder_checks_honor_prose_and_skip_rules(
    tmp_path: Path,
) -> None:
    """Report prose defects while ignoring supported skip regions."""
    skill = _write_skill(tmp_path, body="## Docs\nClean prose.\n")
    assert checks.check_description_prefix(skill.parent).passed
    (skill.parent / "reference").mkdir()
    (skill.parent / "reference" / "reference.md").write_text(
        "Reference prose.\nThis is used.\n<<kept>>\n", encoding="utf-8"
    )
    (skill.parent / "templates").mkdir()
    (skill.parent / "templates" / "template.md").write_text(
        "<<intentional>>\n", encoding="utf-8"
    )
    assert checks.check_no_declarative_voice(skill.parent).passed
    assert checks.check_no_placeholders(skill.parent).passed

    (skill.parent / "guide.md").write_text(
        "This is used.\n" * 7
        + "<<missing>>\n" * 7
        + "1. One sentence.\n2. Another sentence.\n"
        + "* A bullet.\n> A quotation.\n"
        + "```text\ncode content\n```\n"
        + "3. It is used.\n",
        encoding="utf-8",
    )
    voice = checks.check_no_declarative_voice(skill.parent)
    placeholders = checks.check_no_placeholders(skill.parent)
    assert not voice.passed and "and 2 more" in voice.detail
    assert not placeholders.passed and "and 2 more" in placeholders.detail

    no_markdown = tmp_path / "no-markdown"
    no_markdown.mkdir()
    assert not checks.check_no_declarative_voice(no_markdown).passed
    assert not checks.check_no_placeholders(no_markdown).passed


def test_registry_omits_physical_line_rule_and_keeps_other_checks(
    tmp_path: Path,
) -> None:
    """Omit physical-line policy and retain all other aggregate checks."""
    skill = _write_skill(tmp_path)

    checks_result = registry.run_all(skill.parent)["checks"]
    check_names = [result["name"] for result in checks_result]

    assert "one-sentence-per-line" not in check_names
    assert check_names == [
        "frontmatter-valid",
        "name-matches-dir",
        "description-prefix",
        "class-valid",
        "docs-last-section",
        "reference-readme-exists",
        "no-examples-section",
        "no-declarative-voice",
        "no-placeholders",
        "cross-references-exist",
    ]
    assert all(result["passed"] for result in checks_result)


def test_cross_reference_check_resolves_root_and_file_relative_links(
    tmp_path: Path,
) -> None:
    """Resolve skill-root anchors and paths relative to the link source."""
    skill = _write_skill(tmp_path)
    (skill.parent / "root-guide.md").write_text("# Root\n", encoding="utf-8")
    nested = skill.parent / "nested"
    nested.mkdir()
    (nested / "guide.md").write_text("# Nested\n", encoding="utf-8")
    (nested / "index.md").write_text(
        "[root](./root-guide.md#section)\n[nested](./guide.md)\n",
        encoding="utf-8",
    )
    assert checks.check_cross_references_exist(skill.parent).passed

    (nested / "broken.md").write_text(
        "[broken](./missing.md)\n" * 7, encoding="utf-8"
    )
    result = checks.check_cross_references_exist(skill.parent)
    assert not result.passed
    assert "and 2 more" in result.detail

    empty = tmp_path / "no-markdown"
    empty.mkdir()
    assert checks.check_cross_references_exist(empty).passed


def test_skill_validator_registry_reports_missing_directory_and_check_exception(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return structured failures for absent roots and check errors."""
    missing = registry.run_all(tmp_path / "absent")
    assert missing["file_count"] == 0
    assert missing["checks"][0]["name"] == "skill-dir-exists"

    def fail(_: Path):
        raise OSError("read failed")

    monkeypatch.setattr(registry, "ALL_CHECKS", [("custom-check", fail)])
    result = registry.run_all(tmp_path)
    assert result["checks"] == [
        {
            "name": "custom-check",
            "passed": False,
            "detail": "Exception: read failed",
        }
    ]


def test_validate_skill_meta_extracts_and_validates_frontmatter(
    tmp_path: Path,
) -> None:
    """Validate frontmatter boundaries and report normalization failures."""
    valid = _write_skill(tmp_path, name="meta-profile")
    text = valid.read_text(encoding="utf-8")
    frontmatter = meta_core._extract_frontmatter(text)
    assert frontmatter is not None
    assert meta_core._extract_frontmatter("body") is None
    assert meta_core._extract_frontmatter("---\nname: x\n") is None
    parsed = yaml.safe_load(frontmatter)
    assert meta_core.validate_frontmatter(parsed) == []
    assert meta_core.validate_frontmatter(None)
    assert meta_core.validate_skill_file(valid) == {"valid": True, "errors": []}

    no_front = tmp_path / "no-front.md"
    no_front.write_text("body", encoding="utf-8")
    assert "must start" in meta_core.validate_skill_file(no_front)["errors"][0]
    invalid_yaml = tmp_path / "invalid-yaml.md"
    invalid_yaml.write_text("---\nname: [bad\n---\n", encoding="utf-8")
    yaml_result = meta_core.validate_skill_file(invalid_yaml)
    assert "YAML parse error" in yaml_result["errors"][0]


def test_validate_skill_meta_returns_file_read_and_validator_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return consistent results for missing, undecodable, and failed reads."""
    absent = meta_core.validate_skill_file(tmp_path / "missing.md")
    assert not absent["valid"] and "File not found" in absent["errors"][0]

    invalid_bytes = tmp_path / "undecodable.md"
    invalid_bytes.write_bytes(b"\xff")
    undecodable = meta_core.validate_skill_file(invalid_bytes)
    assert not undecodable["valid"]
    assert "Cannot read file" in undecodable["errors"][0]

    valid = _write_skill(tmp_path, name="raised-validator")
    monkeypatch.setattr(
        meta_core,
        "validate_frontmatter",
        lambda _: (_ for _ in ()).throw(ValueError("invalid selection")),
    )
    result = meta_core.validate_skill_file(valid)
    assert result == {
        "valid": False,
        "errors": ["Selection metadata is invalid: invalid selection"],
    }
