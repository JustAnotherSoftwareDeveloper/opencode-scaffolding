"""Unit tests for validating skill Markdown files."""

from pathlib import Path

import pytest
import yaml

from lib.skill_validator import validate_skill_file

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


def test_domain_validator_handles_missing_unreadable_and_malformed_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return fail-closed diagnostics for absent, unreadable, and bad YAML."""
    missing = validate_skill_file(tmp_path / "missing" / "SKILL.md")
    assert missing == {
        "valid": False,
        "errors": [f"File not found: {tmp_path / 'missing' / 'SKILL.md'}"],
    }

    malformed = tmp_path / "malformed" / "SKILL.md"
    malformed.parent.mkdir()
    malformed.write_text("---\nname: [broken\n---\n", encoding="utf-8")
    malformed_result = validate_skill_file(malformed)
    assert malformed_result["valid"] is False
    assert "Frontmatter YAML parse error" in malformed_result["errors"][0]

    unreadable = write_skill(tmp_path, profile(name="unreadable"))
    original_read_text = Path.read_text

    def reject_selected_path(
        path: Path,
        encoding: str | None = None,
        *,
        errors: str | None = None,
    ) -> str:
        if path == unreadable:
            raise OSError("read denied")
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", reject_selected_path)
    unreadable_result = validate_skill_file(unreadable)
    assert unreadable_result == {
        "valid": False,
        "errors": ["Unable to read file: read denied"],
    }


def test_domain_validator_checks_name_and_active_passive_body_contracts(
    tmp_path: Path,
) -> None:
    """Validate directory identity and class-specific Markdown requirements."""
    wrong_name = write_skill(tmp_path, profile(name="directory-name"))
    text = wrong_name.read_text(encoding="utf-8").replace(
        "name: directory-name", "name: different-name"
    )
    wrong_name.write_text(text, encoding="utf-8")
    wrong_name_result = validate_skill_file(wrong_name)
    assert wrong_name_result["valid"] is False
    assert any(
        "does not match directory" in error
        for error in wrong_name_result["errors"]
    )

    active = write_skill(
        tmp_path,
        profile(name="active-without-steps"),
        body="Reference material only.\n",
    )
    active_result = validate_skill_file(active)
    assert active_result["valid"] is False
    assert (
        "active classes must define numbered execution steps"
        in (active_result["errors"])
    )

    passive = write_skill(
        tmp_path,
        profile(
            name="passive-with-steps",
            **{
                "class": "documentation",
                "selection": {
                    "role": "reference",
                    "tags": {"actions": ["validate"]},
                },
            },
        ),
        body="1. This step is not allowed.\n",
    )
    passive_result = validate_skill_file(passive)
    assert passive_result["valid"] is False
    assert any(
        "must not define execution steps" in error
        for error in passive_result["errors"]
    )


def test_domain_validator_requires_reference_role_for_passive_skill(
    tmp_path: Path,
) -> None:
    """Reject passive profile metadata that claims an execution-owner role."""
    path = write_skill(
        tmp_path,
        profile(
            name="passive-owner",
            **{
                "class": "planning",
                "selection": {
                    "role": "owner",
                    "tags": {"topics": ["plans"]},
                },
            },
        ),
        body="Planning reference only.\n",
    )

    result = validate_skill_file(path)

    assert result["valid"] is False
    assert any(
        "selection.role reference" in error for error in result["errors"]
    )
