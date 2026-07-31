"""CLI tests for structured routing metadata validation."""

# ruff: noqa: E501, I001

from __future__ import annotations

import json
from pathlib import Path

from cli.validate_skill_meta import main

from click.testing import CliRunner


_VALID_SKILL = """---
name: valid-skill
description: Use when testing routing metadata
schema_version: '1.0'
cues:
  - facet: operation
    value: validate-routing
    primary: true
relationships:
  - role: owner
class: operation
---
Some content.
"""
_INVALID_SKILL = "---\nname: legacy\ndescription: Use when testing\ntags: [legacy]\nclass: operation\n---\n"


def test_help_and_missing_argument() -> None:
    runner = CliRunner()
    assert runner.invoke(main, ["--help"]).exit_code == 0
    assert runner.invoke(main, []).exit_code == 2


def test_valid_file_json_and_text() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_VALID_SKILL, encoding="utf-8")
        result = runner.invoke(main, ["SKILL.md"])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"valid": True, "errors": []}
        text = runner.invoke(main, ["SKILL.md", "--format", "text"])
        assert text.exit_code == 0
        assert text.output.startswith("VALID SKILL.md")


def test_invalid_legacy_tags_are_reported() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(_INVALID_SKILL, encoding="utf-8")
        result = runner.invoke(main, ["SKILL.md"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        assert any("structured cues" in error for error in data["errors"])


def test_cli_preserves_file_and_yaml_errors() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text("---\ninvalid: [\n---\n", encoding="utf-8")
        result = runner.invoke(main, ["SKILL.md", "--format", "json"])
        assert result.exit_code == 1
        assert "parse error" in json.loads(result.output)["errors"][0].lower()
