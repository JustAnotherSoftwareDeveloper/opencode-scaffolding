"""CLI tests for render-task-markdown."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from cli.render_task_markdown import main

VALID_CONTEXT = "x" * 200


def _packet() -> dict:
    return {
        "summary": "Render a plan.",
        "tasks": [
            {
                "purpose": "Render Markdown.",
                "context": VALID_CONTEXT,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["documentation"],
                "executionInstructions": [{"step": 1, "action": "Render the task."}],
                "expectedOutput": "Markdown task plan.",
            }
        ],
    }


def test_cli_renders_markdown(tmp_path: Path) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        input_file = Path.cwd() / "tasks.json"
        output_file = Path.cwd() / "tasks.md"
        input_file.write_text(json.dumps(_packet()))
        result = runner.invoke(
            main,
            [
                "--input",
                str(input_file),
                "--output",
                str(output_file),
            ],
        )
    assert result.exit_code == 0, result.output
    assert output_file.is_file()


def test_cli_rejects_invalid_json(tmp_path: Path) -> None:
    input_file = tmp_path / "tasks.json"
    input_file.write_text("not json")
    result = CliRunner().invoke(
        main,
        [
            "--input",
            str(input_file),
            "--output",
            str(tmp_path / "tasks.md"),
        ],
    )
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_cli_rejects_output_outside_cwd(tmp_path: Path) -> None:
    input_file = tmp_path / "tasks.json"
    input_file.write_text(json.dumps(_packet()))
    result = CliRunner().invoke(
        main,
        [
            "--input",
            str(input_file),
            "--output",
            str(tmp_path / "tasks.md"),
        ],
    )
    assert result.exit_code == 1
    assert "within the current working directory" in result.output
