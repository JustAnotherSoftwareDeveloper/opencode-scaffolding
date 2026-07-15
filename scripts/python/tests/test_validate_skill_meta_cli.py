"""CLI integration tests for validate-skill-meta.

Uses CliRunner and isolated_filesystem to test the full CLI pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.validate_skill_meta import main

_VALID_SKILL = (
    "---\n"
    "name: valid-skill\n"
    "description: Use when testing\n"
    "tags: [test-capability, metadata-validation, yaml-frontmatter, python]\n"
    "class: operation\n"
    "---\n"
    "\n"
    "Some content.\n"
)

_INVALID_SKILL = "---\nname: ''\ndescription: bad prefix\nclass: unknown-class\n---\n"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CliRunner instance."""
    return CliRunner()


# ---------------------------------------------------------------------------
# --help
# ---------------------------------------------------------------------------


def test_help(runner: CliRunner) -> None:
    """--help exits 0 and prints usage."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


# ---------------------------------------------------------------------------
# Missing required argument
# ---------------------------------------------------------------------------


def test_missing_argument(runner: CliRunner) -> None:
    """No SKILL_PATH argument exits 2 with error message."""
    result = runner.invoke(main, [])
    assert result.exit_code == 2
    assert "Missing argument" in result.output


# ---------------------------------------------------------------------------
# Nonexistent file
# ---------------------------------------------------------------------------


def test_nonexistent_file(runner: CliRunner) -> None:
    """A file path that does not exist exits 2 (Click Path(exists=True) check)."""
    result = runner.invoke(main, ["/tmp/opencode/no_such_file.md"])
    assert result.exit_code == 2
    assert "does not exist" in result.output


# ---------------------------------------------------------------------------
# Valid file — JSON output (default)
# ---------------------------------------------------------------------------


def test_valid_file_json_default(runner: CliRunner) -> None:
    """Valid SKILL.md produces valid:true in JSON stdout and exits 0."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_VALID_SKILL)
        result = runner.invoke(main, ["SKILL.md"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is True
        assert data["errors"] == []


# ---------------------------------------------------------------------------
# Valid file — explicit --format json
# ---------------------------------------------------------------------------


def test_valid_file_format_json(runner: CliRunner) -> None:
    """--format json explicitly produces valid:true."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_VALID_SKILL)
        result = runner.invoke(main, ["SKILL.md", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is True


# ---------------------------------------------------------------------------
# Valid file — --format text
# ---------------------------------------------------------------------------


def test_valid_file_format_text(runner: CliRunner) -> None:
    """--format text prints 'VALID' and exits 0."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_VALID_SKILL)
        result = runner.invoke(main, ["SKILL.md", "--format", "text"])
        assert result.exit_code == 0
        assert result.output.startswith("VALID SKILL.md")


def test_multiple_valid_files_json(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    """Multiple files produce a JSON array after one frequency calculation."""
    monkeypatch.setattr("cli.validate_skill_meta.compute_tag_frequencies", lambda: {})
    with runner.isolated_filesystem():
        Path("one.md").write_text(_VALID_SKILL)
        Path("two.md").write_text(_VALID_SKILL.replace("valid-skill", "other-skill"))

        result = runner.invoke(main, ["one.md", "two.md"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert [entry["valid"] for entry in data] == [True, True]


# ---------------------------------------------------------------------------
# Valid file — invalid --format value
# ---------------------------------------------------------------------------


def test_invalid_format_option(runner: CliRunner) -> None:
    """--format with an invalid choice exits 2."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_VALID_SKILL)
        result = runner.invoke(main, ["SKILL.md", "--format", "xml"])
        assert result.exit_code == 2
        assert "is not one of" in result.output


# ---------------------------------------------------------------------------
# Invalid frontmatter — JSON output
# ---------------------------------------------------------------------------


def test_invalid_frontmatter_json(runner: CliRunner) -> None:
    """Invalid frontmatter yields valid:false with error list in JSON."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_INVALID_SKILL)
        result = runner.invoke(main, ["SKILL.md"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        assert len(data["errors"]) > 0


# ---------------------------------------------------------------------------
# Invalid frontmatter — text output
# ---------------------------------------------------------------------------


def test_invalid_frontmatter_text(runner: CliRunner) -> None:
    """Invalid frontmatter prints INVALID and error bullets with --format text."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_INVALID_SKILL)
        result = runner.invoke(main, ["SKILL.md", "--format", "text"])
        assert result.exit_code == 1
        assert "INVALID" in result.output
        assert "- Field" in result.output or "- " in result.output


# ---------------------------------------------------------------------------
# Missing frontmatter delimiters
# ---------------------------------------------------------------------------


def test_no_frontmatter_delimiters(runner: CliRunner) -> None:
    """File without --- delimiters exits 1 with appropriate error."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text("just plain text\n")
        result = runner.invoke(main, ["SKILL.md"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        assert any("must start with '---'" in e for e in data["errors"])


# ---------------------------------------------------------------------------
# --verbose flag
# ---------------------------------------------------------------------------


def test_verbose_flag(runner: CliRunner) -> None:
    """--verbose prints diagnostics to stderr and JSON to stdout."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_VALID_SKILL)
        result = runner.invoke(main, ["SKILL.md", "--verbose"])
        assert result.exit_code == 0
        # stderr has the verbose message
        if hasattr(result, "stderr"):
            assert "Validating:" in result.stderr
        # stdout has JSON; output may include combined streams, so parse last line
        data = json.loads(result.stdout.strip())
        assert data["valid"] is True


# ---------------------------------------------------------------------------
# Malformed YAML frontmatter
# ---------------------------------------------------------------------------


def test_malformed_yaml(runner: CliRunner) -> None:
    """Unparseable YAML content exits 1 with parse error."""
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text("---\ninvalid_yaml: : :\n---\nstuff\n")
        result = runner.invoke(main, ["SKILL.md"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        assert any("parse error" in e.lower() for e in data["errors"])


# ---------------------------------------------------------------------------
# Parameterized error scenarios for CLI
# ---------------------------------------------------------------------------


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


@pytest.mark.parametrize(
    ("content", "expected_valid", "expected_substrings"),
    [
        pytest.param(
            "",
            False,
            ["must start with '---'"],
            id="empty-file",
        ),
        pytest.param(
            "---\n---\n",
            False,
            ["YAML mapping"],
            id="empty-frontmatter-yields-none",
        ),
        pytest.param(
            "---\nname: x\n---\n",
            False,
            ["Missing required frontmatter field: 'description'"],
            id="missing-description-field",
        ),
    ],
)
def test_various_invalid_inputs(
    runner: CliRunner,
    content: str,
    expected_valid: bool,
    expected_substrings: list[str],
) -> None:
    """Various invalid skill files produce the expected errors."""
    with runner.isolated_filesystem():
        _write_file(Path("SKILL.md"), content)
        result = runner.invoke(main, ["SKILL.md", "--format", "json"])
        if expected_valid:
            assert result.exit_code == 0
        else:
            assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is expected_valid
        for substring in expected_substrings:
            assert any(substring in e for e in data["errors"])
