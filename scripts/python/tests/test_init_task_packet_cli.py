"""CLI tests for init-task-packet."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from cli.init_task_packet import main


def _packet(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "summary": "Test packet for init",
        "tasks": [
            {
                "purpose": "Init a packet.",
                "context": "x" * 200,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["demo"],
                "executionInstructions": [{"step": 1, "action": "Run it."}],
                "expectedOutput": "A packet file.",
            }
        ],
    }
    data.update(overrides)
    return data


def test_publishes_and_prints_path(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet()),
    )
    assert result.exit_code == 0, result.output
    path = Path(result.output.strip())
    assert path.is_file()
    assert path.suffix == ".json"
    assert path.parent == tmp_path


def test_rejects_invalid_json(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input="{not json",
    )
    assert result.exit_code == 1


def test_rejects_non_object(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input="[]",
    )
    assert result.exit_code == 1


def test_rejects_missing_summary(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps({"tasks": []}),
    )
    assert result.exit_code == 1
    assert "summary" in result.output


def test_rejects_empty_summary(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps({"summary": "   ", "tasks": []}),
    )
    assert result.exit_code == 1


def test_rejects_existing_destination(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("cli.init_task_packet.time.time_ns", lambda: 1_000_000_000)
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet()),
    )
    assert result.exit_code == 0
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet()),
    )
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_derives_readable_slug(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet(summary="Deploy the API Gateway")),
    )
    assert result.exit_code == 0
    path = Path(result.output.strip())
    assert "deploy-the-api-gateway" in path.name
    assert path.suffix == ".json"


def test_help_works() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "init-task-packet" in result.output