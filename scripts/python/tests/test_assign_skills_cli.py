"""CLI integration tests for assign-skills."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from cli.assign_skills import main


def _make_state_with_tasks(tmp_path: Path) -> str:
    """Create a valid TaskDraft state file and return its path."""
    state = {
        "summary": "test",
        "tasks": [
            {
                "purpose": "Write tests.",
                "context": "Write tests for CLI.",
                "filesToRead": [],
                "filesToWrite": [],
                "executionInstructions": [{"step": 1, "action": "Do it"}],
                "expectedOutput": "Tests.",
            },
        ],
    }
    path = tmp_path / "state.json"
    path.write_text(json.dumps(state), encoding="utf-8")
    return str(path)


def _make_schema(tmp_path: Path) -> str:
    """Create a minimal TaskDraft schema file and return its path."""
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        '{"type":"object","required":["summary","tasks"],'
        '"properties":{"summary":{"type":"string"},'
        '"tasks":{"type":"array","minItems":1,"items":{"type":"object"}}}}'
    )
    return str(schema_path)


def test_help() -> None:
    """--help produces usage and exits 0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Populate skills on each task draft" in result.output


def test_missing_required_options() -> None:
    """Missing --state-file and --schema exits 2."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 2


def test_missing_schema(tmp_path: Path) -> None:
    """Missing --schema exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--state-file", state_path])
    assert result.exit_code == 2


def test_invalid_skill_classes(tmp_path: Path) -> None:
    """Invalid --skill-classes value exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--skill-classes",
            "operation,nonexistent",
        ],
    )
    assert result.exit_code == 2
    assert "invalid class names" in result.output


def test_invalid_floor(tmp_path: Path) -> None:
    """Negative legacy --floor exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--floor",
            "-1.0",
        ],
    )
    assert result.exit_code == 2
    assert "floor" in result.output.lower()


def test_invalid_threshold(tmp_path: Path) -> None:
    """Negative --threshold exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--threshold",
            "-1.0",
        ],
    )
    assert result.exit_code == 2
    assert "threshold" in result.output.lower()


def test_invalid_weight_sum(tmp_path: Path) -> None:
    """Weights must sum to 1.0."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--weight-keyword-overlap",
            "1.0",
        ],
    )
    assert result.exit_code == 2
    assert "weights must sum" in result.output.lower()


def test_invalid_min_skills(tmp_path: Path) -> None:
    """--min-skills < 1 exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--min-skills",
            "0",
        ],
    )
    assert result.exit_code == 2
    assert "min-skills" in result.output.lower()


def test_invalid_skills_json(tmp_path: Path) -> None:
    """Invalid --skills-json JSON exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--skills-json",
            "not valid json",
        ],
    )
    assert result.exit_code == 2


def test_skills_json_not_array(tmp_path: Path) -> None:
    """--skills-json that is not an array exits 2."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--state-file",
            state_path,
            "--schema",
            schema_path,
            "--skills-json",
            '{"not": "array"}',
        ],
    )
    assert result.exit_code == 2


def test_success_with_mocked_ranker(tmp_path: Path) -> None:
    """Normal invocation succeeds with mocked assignment function."""
    state_path = _make_state_with_tasks(tmp_path)
    schema_path = _make_schema(tmp_path)

    with patch(
        "cli.assign_skills.assign_skills",
        return_value=state_path,
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--state-file",
                state_path,
                "--schema",
                schema_path,
            ],
        )
        assert result.exit_code == 0
