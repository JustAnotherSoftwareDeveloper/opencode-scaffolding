"""Unit tests for lib.validate_skill_meta.core.

Tests _extract_frontmatter, validate_frontmatter, and validate_skill_file.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from lib.validate_skill_meta.core import validate_frontmatter, validate_skill_file

VALID_TAGS = ["test-capability", "metadata-validation", "yaml-frontmatter", "python"]

# ---------------------------------------------------------------------------
# validate_frontmatter — parametrized
# ---------------------------------------------------------------------------


def test_validate_frontmatter_valid() -> None:
    """All required fields present and valid."""
    data = {
        "name": "my-skill",
        "description": "Use when doing something useful",
        "tags": VALID_TAGS,
        "class": "operation",
    }
    assert validate_frontmatter(data) == []


@pytest.mark.parametrize(
    ("tags", "error"),
    [
        (None, "Missing required frontmatter field: 'tags'"),
        ("testing", "Field 'tags' must be a list"),
        (["testing"], "Field 'tags' must contain 4–7 values"),
        (
            ["testing", "validation", "yaml-frontmatter", "Bad Tag"],
            "Field 'tags' values must be lowercase kebab-case",
        ),
        (
            ["testing", "validation", "yaml-frontmatter", "helper"],
            "Field 'tags' values must not be filler terms",
        ),
        (
            ["testing", "validation", "yaml-frontmatter", "testing"],
            "Field 'tags' values must be unique",
        ),
        (
            ["my-skill", "validation", "yaml-frontmatter", "python"],
            "Field 'tags' must not repeat the skill name",
        ),
    ],
)
def test_validate_frontmatter_tags(tags: object, error: str) -> None:
    """Required tag metadata rejects invalid tag lists."""
    data = {
        "name": "my-skill",
        "description": "Use when doing something useful",
        "tags": tags,
        "class": "operation",
    }
    assert error in validate_frontmatter(data)


@pytest.mark.parametrize(
    ("data", "expected_errors"),
    [
        pytest.param(
            None,
            ["Frontmatter is not a valid YAML mapping"],
            id="not-a-dict",
        ),
        pytest.param(
            {},
            [
                "Missing required frontmatter field: 'name'",
                "Missing required frontmatter field: 'description'",
                "Missing required frontmatter field: 'tags'",
                "Missing required frontmatter field: 'class'",
            ],
            id="all-missing",
        ),
        pytest.param(
            {"name": None, "description": "Use when test", "class": "operation"},
            ["Missing required frontmatter field: 'name'"],
            id="name-is-none",
        ),
        pytest.param(
            {"name": "", "description": "Use when test", "class": "operation"},
            ["Field 'name' must be a non-empty string"],
            id="name-empty-string",
        ),
        pytest.param(
            {"name": "   ", "description": "Use when test", "class": "operation"},
            ["Field 'name' must be a non-empty string"],
            id="name-whitespace-only",
        ),
        pytest.param(
            {"name": 42, "description": "Use when test", "class": "operation"},
            ["Field 'name' must be a non-empty string"],
            id="name-not-string",
        ),
        pytest.param(
            {"name": "valid", "class": "operation"},
            ["Missing required frontmatter field: 'description'"],
            id="description-missing",
        ),
        pytest.param(
            {"name": "valid", "description": 42, "class": "operation"},
            ["Field 'description' must be a string"],
            id="description-not-string",
        ),
        pytest.param(
            {"name": "valid", "description": "Nope", "class": "operation"},
            ["Field 'description' must start with 'Use when'"],
            id="description-wrong-prefix",
        ),
        pytest.param(
            {"name": "valid", "description": "Use when test"},
            ["Missing required frontmatter field: 'class'"],
            id="class-missing",
        ),
        pytest.param(
            {"name": "valid", "description": "Use when test", "class": 42},
            ["Field 'class' must be a string"],
            id="class-not-string",
        ),
        pytest.param(
            {
                "name": "valid",
                "description": "Use when test",
                "class": "unknown-class",
            },
            [
                "Field 'class' must be one of: "
                "delegated, documentation, inline, "
                "operation, orchestrated, planning"
            ],
            id="class-invalid-value",
        ),
        pytest.param(
            ["not", "a", "dict"],
            ["Frontmatter is not a valid YAML mapping"],
            id="list-instead-of-dict",
        ),
    ],
)
def test_validate_frontmatter_errors(
    data: object,
    expected_errors: list[str],
) -> None:
    """Each parametrized case produces the expected error messages."""
    if isinstance(data, dict) and data:
        data = {**data, "tags": VALID_TAGS}
    assert validate_frontmatter(data) == expected_errors


# ---------------------------------------------------------------------------
# validate_skill_file — file-level integration
# ---------------------------------------------------------------------------


def _write_skill(tmp_path: Path, content: str, filename: str = "SKILL.md") -> Path:
    """Helper: write *content* to *filename* under *tmp_path* and return full path."""
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    return path


def test_validate_skill_file_valid(tmp_path: Path) -> None:
    """A correct SKILL.md passes validation."""
    skill = (
        "---\n"
        "name: valid-skill\n"
        "description: Use when doing the thing\n"
        "tags: [test-capability, metadata-validation, yaml-frontmatter, python]\n"
        "class: operation\n"
        "---\n"
        "\n"
        "## Body\n"
    )
    path = _write_skill(tmp_path, skill)
    result = validate_skill_file(path)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_skill_file_checks_cross_skill_tag_rules(tmp_path: Path) -> None:
    """Cross-skill checks reject an overused tag when frequencies are supplied."""
    path = _write_skill(
        tmp_path,
        "---\n"
        "name: valid-skill\n"
        "description: Use when doing the thing\n"
        "tags: [test-capability, metadata-validation, yaml-frontmatter, python]\n"
        "class: operation\n"
        "---\n",
    )

    result = validate_skill_file(path, {"test-capability": 6})

    assert result["valid"] is False
    assert any("Tag 'test-capability' appears in 6 skills" in error for error in result["errors"])


def test_validate_skill_file_accepts_analysis_as_deliverable(tmp_path: Path) -> None:
    """Analysis artifacts satisfy the tool-or-deliverable tag requirement."""
    path = _write_skill(
        tmp_path,
        "---\n"
        "name: analysis-skill\n"
        "description: Use when analysing an artifact\n"
        "tags: [evidence-analysis, problem-framing, decision-assessment, root-cause-analysis]\n"
        "class: planning\n"
        "---\n",
    )

    result = validate_skill_file(path, {})

    assert result["valid"] is True


def test_validate_skill_file_nonexistent(tmp_path: Path) -> None:
    """Nonexistent file produces a file-not-found error."""
    path = tmp_path / "does_not_exist.md"
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert result["errors"] == [f"File not found: {path}"]


def test_validate_skill_file_missing_frontmatter(tmp_path: Path) -> None:
    """File without leading --- delimiters yields frontmatter error."""
    path = _write_skill(tmp_path, "no frontmatter here\n")
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert any("must start with '---'" in e for e in result["errors"])


def test_validate_skill_file_missing_closing_delimiter(tmp_path: Path) -> None:
    """File that starts with --- but never closes also yields frontmatter error."""
    path = _write_skill(tmp_path, "---\nname: foo\n")
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert any("must start with '---'" in e for e in result["errors"])


def test_validate_skill_file_malformed_yaml(tmp_path: Path) -> None:
    """Unparseable YAML content yields a YAML parse error."""
    path = _write_skill(
        tmp_path,
        "---\n  invalid_yaml: : :\n---\nstuff",
    )
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert result["errors"][0].startswith("Frontmatter YAML parse error")


def test_validate_skill_file_yields_validation_errors(tmp_path: Path) -> None:
    """Valid YAML frontmatter with invalid fields reports those errors."""
    path = _write_skill(
        tmp_path,
        "---\nname: ''\ndescription: Use when ok\nclass: bogus\n---\n",
    )
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert "Field 'name' must be a non-empty string" in result["errors"]
    assert any("one of" in e for e in result["errors"])


def test_validate_skill_file_unreadable(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    """When the file cannot be read, a read-error is returned."""
    path = _write_skill(tmp_path, "---\nname: x\n---\n")

    def broken_read(*_: object, **__: object) -> str:
        raise OSError("Permission denied")

    # PosixPath.read_text is a method on the class, not an instance attribute
    monkeypatch.setattr("pathlib.Path.read_text", broken_read)
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert "Cannot read file" in result["errors"][0]

    # Undo the class-level patch so other tests are unaffected
    monkeypatch.undo()


def test_validate_skill_file_yaml_exception_on_none(tmp_path: Path) -> None:
    """YAML content that evaluates to *None* is handled by validate_frontmatter."""
    path = _write_skill(
        tmp_path,
        "---\n---\nbody\n",
    )
    result = validate_skill_file(path)
    assert result["valid"] is False
    # yaml.safe_load("") returns None, which triggers "not a valid YAML mapping"
    assert any("Frontmatter is not a valid YAML mapping" in e for e in result["errors"])


# Convenience import check — make sure yaml is used (avoids unused-import lint)
def test_yaml_available() -> None:
    """Sanity check that PyYAML is importable."""
    assert yaml is not None  # pragma: no cover — just a smoke test
