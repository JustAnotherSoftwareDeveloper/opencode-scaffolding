"""Selecting one task must not abbreviate or mutate the source packet."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.get_task import main
from lib.get_task.core import select_task


@pytest.fixture
def packet() -> dict:
    """Build a canonical packet with short and large task objects."""
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
    """Write the task packet to a temporary JSON file."""
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("args", "expected_index"),
    [(["--id", "first"], 0), (["--index", "0"], 0), (["--index", "1"], 1)],
)
@pytest.mark.integration
def test_returns_exact_complete_object(
    task_file: Path, packet: dict, args: list[str], expected_index: int
) -> None:
    """Verify task selection returns the complete unchanged object."""
    before = task_file.read_bytes()
    result = CliRunner().invoke(main, [str(task_file), *args])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == packet["tasks"][expected_index]
    assert task_file.read_bytes() == before


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--id", "first", "--index", "0"],
        ["--id", "missing"],
        ["--index", "2"],
    ],
)
@pytest.mark.integration
def test_rejects_ambiguous_or_missing_selection(
    task_file: Path, args: list[str]
) -> None:
    """Verify ambiguous and missing task selections are rejected."""
    result = CliRunner().invoke(main, [str(task_file), *args])
    assert result.exit_code == 2
    assert "Error:" in result.output


@pytest.mark.integration
def test_rejects_malformed_and_rootless_json(task_file: Path) -> None:
    """Verify malformed and rootless task packets are rejected."""
    task_file.write_text("[{}]", encoding="utf-8")
    rootless = CliRunner().invoke(main, [str(task_file), "--index", "0"])
    assert rootless.exit_code == 2
    assert "canonical task-packet object" in rootless.output
    task_file.write_text("{", encoding="utf-8")
    malformed = CliRunner().invoke(main, [str(task_file), "--index", "0"])
    assert malformed.exit_code == 2
    assert "Error:" in malformed.output


@pytest.mark.unit
def test_domain_selects_by_id_and_index(packet: dict) -> None:
    """Select complete task objects directly through the domain API."""
    assert select_task(packet, "first", None) is packet["tasks"][0]
    assert select_task(packet, None, 1) is packet["tasks"][1]


@pytest.mark.parametrize("packet", [[], {"tasks": None}, {"items": []}])
@pytest.mark.unit
def test_domain_rejects_invalid_roots(packet: object) -> None:
    """Reject non-object roots and roots without a task array."""
    with pytest.raises(ValueError, match="canonical task-packet object"):
        select_task(packet, "first", None)


@pytest.mark.unit
def test_domain_rejects_out_of_range_index(packet: dict) -> None:
    """Reject an index outside the canonical task array."""
    with pytest.raises(ValueError, match="out of range"):
        select_task(packet, None, len(packet["tasks"]))


@pytest.mark.unit
def test_rejects_duplicate_task_id_and_non_object_task(packet: dict) -> None:
    """Verify duplicate IDs and non-object tasks are rejected."""
    packet["tasks"].append({"taskId": "first"})
    with pytest.raises(ValueError, match="exactly one task"):
        select_task(packet, "first", None)
    packet["tasks"][0] = "bad task"
    with pytest.raises(ValueError, match="not a JSON object"):
        select_task(packet, None, 0)


@pytest.mark.integration
def test_selects_late_task_from_a_plan_larger_than_read_tool_limit(
    task_file: Path, packet: dict
) -> None:
    """Verify a late task can be selected from a large plan."""
    packet["tasks"] = [deepcopy(packet["tasks"][0]) for _ in range(25)]
    for index, task in enumerate(packet["tasks"]):
        task["taskId"] = f"long-task-{index}"
    task_file.write_text(json.dumps(packet), encoding="utf-8")
    assert task_file.stat().st_size > 50_000
    result = CliRunner().invoke(main, [str(task_file), "--index", "24"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == packet["tasks"][24]
