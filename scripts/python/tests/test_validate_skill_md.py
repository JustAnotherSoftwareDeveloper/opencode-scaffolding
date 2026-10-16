"""Unit tests for validating skill Markdown files."""

from pathlib import Path

import pytest
import yaml

from cli.validate_skill_md import validate_skill_file

pytestmark = pytest.mark.unit


def profile(name: str = "demo", **updates: object) -> dict[str, object]:
    """Build a default skill profile for validation fixtures."""
    value: dict[str, object] = {
        "name": name,
        "description": "Use when validating a demo skill",
        "class": "operation",
        "selection": {"role": "owner", "tags": {"actions": ["validate"]}},
    }
    value.update(updates)
    return value


def write_skill(
    tmp_path: Path,
    data: dict[str, object],
    body: str = "\n1. Validate the input.\n",
) -> Path:
    """Write a skill Markdown fixture and return its path."""
    directory = tmp_path / str(data["name"])
    directory.mkdir()
    path = directory / "SKILL.md"
    path.write_text(
        "---\n" + yaml.safe_dump(data, sort_keys=False) + "---" + body,
        encoding="utf-8",
    )
    return path


def test_valid_profile_and_body(tmp_path: Path) -> None:
    """Verify a valid skill profile and body pass validation."""
    assert validate_skill_file(write_skill(tmp_path, profile())) == {
        "valid": True,
        "errors": [],
    }


def test_obsolete_and_unknown_fields_are_rejected(tmp_path: Path) -> None:
    """Verify obsolete and unknown profile fields are rejected."""
    result = validate_skill_file(
        write_skill(tmp_path, profile(schema_version="1"))
    )
    assert not result["valid"]
    assert any("obsolete" in error for error in result["errors"])


def test_passive_class_requires_reference_and_no_steps(tmp_path: Path) -> None:
    """Verify passive skills require reference material and prohibit steps."""
    data = profile(
        **{
            "class": "planning",
            "selection": {"role": "owner", "tags": {"topics": ["plans"]}},
        }
    )
    result = validate_skill_file(
        write_skill(tmp_path, data, "\nReference material.\n1. no\n")
    )
    assert not result["valid"]
    assert any("reference" in error for error in result["errors"])
    assert any("must not" in error for error in result["errors"])


def test_name_and_path_are_checked(tmp_path: Path) -> None:
    """Verify a skill's filename and path must match the profile contract."""
    path = write_skill(tmp_path, profile())
    path.rename(path.parent / "README.md")
    assert any(
        "SKILL.md" in error
        for error in validate_skill_file(path.parent / "README.md")["errors"]
    )
