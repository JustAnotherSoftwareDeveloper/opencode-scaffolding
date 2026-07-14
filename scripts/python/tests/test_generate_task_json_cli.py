"""CLI integration tests for generate-task-json."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from cli import generate_task_json
from lib.generate_task_json.core import GenerationValidationError

VALID_CONTEXT = (
    "Exercise the CLI task generator with a complete draft that identifies the test "
    "scope, target behavior, expected output, and relevant constraints while avoiding "
    "unrelated code changes or unsupported execution paths."
)


def _drafts() -> str:
    return json.dumps(
        {
            "summary": "CLI test.",
            "tasks": [
                {
                    "purpose": "Write tests.",
                    "context": VALID_CONTEXT,
                    "filesToRead": [],
                    "filesToWrite": [],
                    "executionInstructions": [{"step": 1, "action": "Write tests."}],
                    "expectedOutput": "Tests.",
                }
            ],
        }
    )


def test_help() -> None:
    result = CliRunner().invoke(generate_task_json.main, ["--help"])
    assert result.exit_code == 0
    assert "Assign skills" in result.output


def test_success_prints_relative_output_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda _data, slug, *, output_dir, output_file: (
            output_file,
            output_dir / f"{slug}.json",
        )[1],
    )
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            generate_task_json.main,
            [
                "--summary-slug",
                "cli-test",
                "--output-dir",
                str(Path.cwd() / ".tasks"),
            ],
            input=_drafts(),
        )
    assert result.exit_code == 0
    assert result.output == ".tasks/cli-test.json\n"


def test_missing_summary_slug_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main, ["--output-dir", ".tasks"], input=_drafts()
    )
    assert result.exit_code == 2


def test_missing_output_dir_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main, ["--summary-slug", "cli-test"], input=_drafts()
    )
    assert result.exit_code == 2


def test_explicit_output_file_succeeds(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda _data, _slug, *, output_dir, output_file: (output_dir, output_file)[1],
    )
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        output_file = Path.cwd() / "tasks.json"
        result = runner.invoke(
            generate_task_json.main,
            ["--output-file", str(output_file)],
            input=_drafts(),
        )
    assert result.exit_code == 0
    assert result.output == "tasks.json\n"


def test_explicit_output_file_outside_cwd_fails(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--output-file", str(tmp_path / "tasks.json")],
        input=_drafts(),
    )
    assert result.exit_code == 2
    assert "within the current working directory" in result.output


def test_partial_or_mixed_destination_options_fail() -> None:
    runner = CliRunner()
    for arguments in (
        [],
        ["--summary-slug", "cli-test"],
        ["--output-dir", ".tasks"],
        [
            "--summary-slug",
            "cli-test",
            "--output-dir",
            ".tasks",
            "--output-file",
            "tasks.json",
        ],
    ):
        result = runner.invoke(generate_task_json.main, arguments, input=_drafts())
        assert result.exit_code == 2


def test_invalid_summary_slug_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "Not a slug", "--output-dir", ".tasks"],
        input=_drafts(),
    )
    assert result.exit_code == 1
    assert "kebab-case" in result.output


def test_malformed_json_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test", "--output-dir", ".tasks"],
        input="not json",
    )
    assert result.exit_code == 2
    assert "Error:" in result.output


def test_array_json_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test", "--output-dir", ".tasks"],
        input="[]",
    )
    assert result.exit_code == 2
    assert "object" in result.output


def test_validation_failure_has_no_stdout(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_, **__: (_ for _ in ()).throw(
            GenerationValidationError("invalid draft")
        ),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test", "--output-dir", ".tasks"],
        input=_drafts(),
    )
    assert result.exit_code == 1
    assert result.output == "Error: invalid draft\n"


def test_runtime_failure_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_, **__: (_ for _ in ()).throw(RuntimeError("no skills")),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test", "--output-dir", ".tasks"],
        input=_drafts(),
    )
    assert result.exit_code == 1


def test_output_error_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_, **__: (_ for _ in ()).throw(OSError("bad path")),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test", "--output-dir", ".tasks"],
        input=_drafts(),
    )
    assert result.exit_code == 2
