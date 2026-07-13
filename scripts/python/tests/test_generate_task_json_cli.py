"""CLI integration tests for generate-task-json."""

from __future__ import annotations

import json

from click.testing import CliRunner

from cli import generate_task_json
from lib.generate_task_json.core import GenerationValidationError


def _drafts() -> str:
    return json.dumps(
        {
            "summary": "CLI test.",
            "tasks": [
                {
                    "purpose": "Write tests.",
                    "context": "x" * 2000,
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
        lambda _data, slug: tmp_path / ".tasks" / f"{slug}.json",
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test"],
        input=_drafts(),
    )
    assert result.exit_code == 0
    assert result.output == ".tasks/cli-test.json\n"


def test_missing_summary_slug_fails() -> None:
    result = CliRunner().invoke(generate_task_json.main, [], input=_drafts())
    assert result.exit_code == 2


def test_invalid_summary_slug_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "Not a slug"],
        input=_drafts(),
    )
    assert result.exit_code == 1
    assert "kebab-case" in result.output


def test_malformed_json_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test"],
        input="not json",
    )
    assert result.exit_code == 2
    assert "Error:" in result.output


def test_array_json_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test"],
        input="[]",
    )
    assert result.exit_code == 2
    assert "object" in result.output


def test_validation_failure_has_no_stdout(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_: (_ for _ in ()).throw(GenerationValidationError("invalid draft")),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test"],
        input=_drafts(),
    )
    assert result.exit_code == 1
    assert result.output == "Error: invalid draft\n"


def test_runtime_failure_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_: (_ for _ in ()).throw(RuntimeError("no skills")),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test"],
        input=_drafts(),
    )
    assert result.exit_code == 1


def test_output_error_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_: (_ for _ in ()).throw(OSError("bad path")),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test"],
        input=_drafts(),
    )
    assert result.exit_code == 2
