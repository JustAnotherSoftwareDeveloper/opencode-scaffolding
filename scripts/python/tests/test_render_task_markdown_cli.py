"""CLI tests for render-task-markdown."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.render_task_markdown import main

pytestmark = pytest.mark.integration

VALID_CONTEXT = "x" * 200


def _packet() -> dict:
    return {
        "summary": "Render a plan.",
        "slug": "render-a-plan",
        "boundaryReview": {
            "requestResultInventory": {
                "render": {
                    "result": "Markdown task plan.",
                    "kind": "immediate",
                    "disposition": "represented-by-task",
                }
            },
            "taskReviews": {
                "render": {
                    "immediateResult": "Markdown task plan.",
                    "predecessorOutputs": [],
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
            },
            "warningDispositions": {},
        },
        "tasks": [
            {
                "taskId": "render",
                "purpose": "Render Markdown.",
                "context": VALID_CONTEXT,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["documentation"],
                "executionInstructions": [
                    {"step": 1, "action": "Render the task."}
                ],
                "expectedOutput": "Markdown task plan.",
                "verificationCoverage": {
                    "observable": ["Markdown output exists."]
                },
                "dependencies": [],
                "antiPatternSignals": ["none"],
                "purposeOutputAlignment": {
                    "status": "aligned",
                    "evidence": "Rendering produces the Markdown task plan.",
                },
            }
        ],
    }


def test_cli_renders_markdown(tmp_path: Path) -> None:
    """Verify the CLI writes a rendered Markdown task plan."""
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
    content = output_file.read_text()
    assert "## Task 1\n\nPurpose: Render Markdown." in content
    assert "### Task 1 Context" in content


def test_cli_overwrites_only_with_explicit_flag(tmp_path: Path) -> None:
    """Verify the CLI overwrites existing Markdown only with the flag."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        input_file = Path.cwd() / "tasks.json"
        output_file = Path.cwd() / "tasks.md"
        input_file.write_text(json.dumps(_packet()))
        output_file.write_text("stale\n")

        result = runner.invoke(
            main,
            [
                "--input",
                str(input_file),
                "--output",
                str(output_file),
                "--overwrite",
            ],
        )

    assert result.exit_code == 0, result.output
    assert output_file.read_text().startswith("# Task Plan\n")


def test_cli_rejects_invalid_json(tmp_path: Path) -> None:
    """Verify the CLI reports invalid task JSON."""
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
    assert result.exit_code == 2
    assert "Error:" in result.stderr
    assert "Traceback" not in result.output


def test_cli_rejects_output_outside_cwd(tmp_path: Path) -> None:
    """Verify the CLI rejects output paths outside its working directory."""
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
    assert result.exit_code == 2
    assert "within the current working directory" in result.stderr
    assert "Traceback" not in result.output


def test_cli_reports_output_filesystem_failure_with_environment_status(
    tmp_path: Path,
) -> None:
    """Distinguish output I/O errors from invalid packet or path input."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        input_file = Path.cwd() / "tasks.json"
        input_file.write_text(json.dumps(_packet()), encoding="utf-8")
        blocked_parent = Path.cwd() / "blocked-parent"
        blocked_parent.write_text("not a directory", encoding="utf-8")
        output_file = blocked_parent / "tasks.md"

        result = runner.invoke(
            main,
            ["--input", str(input_file), "--output", str(output_file)],
        )

        assert result.exit_code == 3
        assert "Error:" in result.stderr
        assert "Traceback" not in result.output
        assert not output_file.exists()
        assert blocked_parent.read_text(encoding="utf-8") == "not a directory"
