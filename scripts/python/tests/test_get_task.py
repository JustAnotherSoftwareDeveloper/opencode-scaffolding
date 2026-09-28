"""Selecting one complete task must not abbreviate or mutate the source packet."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.get_task import main, select_task


@pytest.fixture
def packet() -> dict:
    return {
        "summary": "Select one task.",
        "slug": "read-only-selection",
        "tasks": [
            {
                "taskId": "first",
                "purpose": "Keep content unchanged.",
                "context": "A" * 8000,
                "filesToRead": ["skills/example/SKILL.md"],
                "filesToWrite": ["skills/example/SKILL.md"],
                "skills": ["generic-executor"],
                "executionInstructions": [
                    {"step": 1, "action": "Preserve every field."}
                ],
                "verification": ["Check all fields."],
                "expectedOutput": "One unchanged task.",
                "verificationCoverage": {"observable": ["Task selected."]},
                "dependencies": [],
                "antiPatternSignals": ["none"],
                "purposeOutputAlignment": {
                    "status": "aligned",
                    "evidence": "Selection preserves the task.",
                },
            },
            {"taskId": "second", "purpose": "Return the second task."},
        ],
        "boundaryReview": {},
    }


@pytest.fixture
def task_file(tmp_path: Path, packet: dict) -> Path:
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("args", "expected_index"),
    [(["--id", "first"], 0), (["--index", "0"], 0), (["--index", "1"], 1)],
)
def test_returns_exact_complete_object(
    task_file: Path, packet: dict, args: list[str], expected_index: int
) -> None:
    before = task_file.read_bytes()
    result = CliRunner().invoke(main, [str(task_file), *args])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == packet["tasks"][expected_index]
    assert task_file.read_bytes() == before


@pytest.mark.parametrize(
    "args",
    [[], ["--id", "first", "--index", "0"], ["--id", "missing"], ["--index", "2"]],
)
def test_rejects_ambiguous_or_missing_selection(
    task_file: Path, args: list[str]
) -> None:
    result = CliRunner().invoke(main, [str(task_file), *args])
    assert result.exit_code == 2
    assert "Error:" in result.output


def test_rejects_malformed_and_rootless_json(task_file: Path) -> None:
    task_file.write_text("[{}]", encoding="utf-8")
    rootless = CliRunner().invoke(main, [str(task_file), "--index", "0"])
    assert rootless.exit_code == 2
    assert "canonical task-packet object" in rootless.output
    task_file.write_text("{", encoding="utf-8")
    malformed = CliRunner().invoke(main, [str(task_file), "--index", "0"])
    assert malformed.exit_code == 2
    assert "Error:" in malformed.output


def test_rejects_duplicate_task_id_and_non_object_task(packet: dict) -> None:
    packet["tasks"].append({"taskId": "first"})
    with pytest.raises(ValueError, match="exactly one task"):
        select_task(packet, "first", None)
    packet["tasks"][0] = "bad task"
    with pytest.raises(ValueError, match="not a JSON object"):
        select_task(packet, None, 0)


def test_selects_late_task_from_a_plan_larger_than_read_tool_limit(
    task_file: Path, packet: dict
) -> None:
    packet["tasks"] = [deepcopy(packet["tasks"][0]) for _ in range(25)]
    for index, task in enumerate(packet["tasks"]):
        task["taskId"] = f"long-task-{index}"
    task_file.write_text(json.dumps(packet), encoding="utf-8")
    assert task_file.stat().st_size > 50_000
    result = CliRunner().invoke(main, [str(task_file), "--index", "24"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == packet["tasks"][24]
