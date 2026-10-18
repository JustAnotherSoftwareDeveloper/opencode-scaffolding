"""Integration tests for Click parsing on ``validate-skill-md``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from cli.validate_skill_md import main

pytestmark = pytest.mark.integration


def _write_skill(path: Path, *, body: str) -> Path:
    """Write a complete skill Markdown input under a matching directory."""
    path.parent.mkdir(parents=True)
    metadata = {
        "name": path.parent.name,
        "description": "Use when checking a CLI skill",
        "class": "operation",
        "selection": {"role": "owner", "tags": {"actions": ["validate"]}},
    }
    path.write_text(
        "---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n" + body,
        encoding="utf-8",
    )
    return path


def test_cli_validates_valid_skill_and_emits_result_json(
    tmp_path: Path,
) -> None:
    """Parse a path argument and return the valid result object as JSON."""
    skill = _write_skill(
        tmp_path / "valid-skill" / "SKILL.md", body="1. Run.\n"
    )

    result = CliRunner().invoke(main, [str(skill)])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"valid": True, "errors": []}


def test_cli_invalid_skill_returns_failure_status_and_diagnostics(
    tmp_path: Path,
) -> None:
    """Return a structured diagnostic and nonzero status for an invalid file."""
    skill = _write_skill(
        tmp_path / "invalid-skill" / "SKILL.md", body="No steps.\n"
    )

    result = CliRunner().invoke(main, [str(skill)])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["valid"] is False
    assert payload["errors"] == [
        "active classes must define numbered execution steps"
    ]


def test_cli_requires_at_least_one_skill_path() -> None:
    """Keep Click's required-argument usage handling observable."""
    result = CliRunner().invoke(main, [])

    assert result.exit_code == 2
    assert "Missing argument" in result.output
    assert "Usage:" in result.output
