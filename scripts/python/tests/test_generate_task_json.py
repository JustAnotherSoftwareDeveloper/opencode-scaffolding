"""Tests for the generate-task-json library."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from lib.collect_skills.models import Skill
from lib.generate_task_json import core


def _drafts() -> dict:
    return {
        "summary": "Generate test task packets.",
        "tasks": [
            {
                "purpose": "Write Python tests.",
                "context": "x" * 2000,
                "filesToRead": ["scripts/python/src/cli/example.py"],
                "filesToWrite": ["scripts/python/tests/test_example.py"],
                "executionInstructions": [{"step": 1, "action": "Write tests."}],
                "expectedOutput": "Python tests.",
            }
        ],
    }


def _skill(name: str = "python-test", class_: str = "operation") -> Skill:
    return Skill(
        name=name,
        description="Write Python tests",
        tags=["python", "tests"],
        class_=class_,
    )


def test_generate_task_json_writes_assigned_output(tmp_path: Path) -> None:
    output = core.generate_task_json(
        _drafts(),
        "generate-tests",
        project_root=tmp_path,
        skills_index=[
            {
                "name": "python-test",
                "description": "Write Python tests",
                "tags": ["python", "tests"],
                "class": "operation",
            }
        ],
    )
    result = json.loads(output.read_text())
    assert output == tmp_path / ".tasks" / "generate-tests.json"
    assert result["tasks"][0]["skills"] == ["python-test"]


def test_generate_task_json_rejects_invalid_input_without_replacing_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / ".tasks" / "generate-tests.json"
    output.parent.mkdir()
    output.write_text('{"preserve": true}\n')
    with pytest.raises(core.GenerationValidationError, match="input failed"):
        core.generate_task_json(
            {"summary": "missing tasks"},
            "generate-tests",
            project_root=tmp_path,
        )
    assert output.read_text() == '{"preserve": true}\n'


def test_generate_task_json_rejects_draft_skills_before_creating_tasks_directory(
    tmp_path: Path,
) -> None:
    drafts = _drafts()
    drafts["tasks"][0]["skills"] = ["manual-skill"]
    with pytest.raises(core.GenerationValidationError, match="input failed"):
        core.generate_task_json(drafts, "generate-tests", project_root=tmp_path)
    assert not (tmp_path / ".tasks").exists()


def test_generate_task_json_rejects_missing_candidates(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="No skills found"):
        core.generate_task_json(
            _drafts(), "generate-tests", project_root=tmp_path, skills_index=[]
        )


def test_generate_task_json_rejects_invalid_final_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validations = iter([[], ["final output is invalid"]])
    monkeypatch.setattr(core, "validate_json_schema", lambda *_: next(validations))
    with pytest.raises(core.GenerationValidationError, match="output failed"):
        core.generate_task_json(
            _drafts(),
            "generate-tests",
            project_root=tmp_path,
            skills_index=[{"name": "test", "class": "operation"}],
        )


def test_candidate_skills_discovers_and_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        core,
        "_discover_skills",
        lambda: [_skill(), _skill("planner", "planning")],
    )
    assert [skill.name for skill in core._candidate_skills(None)] == ["python-test"]


def test_parse_skills_preserves_defaults() -> None:
    parsed = core._parse_skills([{"name": "minimal"}])
    assert parsed[0].name == "minimal"
    assert parsed[0].tags == []


def test_discover_skills_resolves_index() -> None:
    with patch("lib.generate_task_json.core.discover_all_skills") as discover:
        assert core._discover_skills() == []
    discover.assert_called_once()


def test_select_skills_uses_threshold_and_fallback() -> None:
    matching = _skill()
    weak = Skill(name="docs", description="", tags=[], class_="documentation")
    task = _drafts()["tasks"][0]
    assert core._select_skills(task, [weak, matching]) == ["python-test"]
    assert core._select_skills(task, [weak]) == ["docs"]


def test_select_skills_caps_matches_at_three() -> None:
    task = _drafts()["tasks"][0]
    candidates = [_skill(f"python-test-{index}") for index in range(4)]
    assert core._select_skills(task, candidates) == [
        "python-test-0",
        "python-test-1",
        "python-test-2",
    ]


def test_task_text_and_scoring_helpers() -> None:
    task = _drafts()["tasks"][0]
    text = core._task_text(task)
    assert "Write Python tests." in text
    assert core._score_skill(_skill(), text) > core._score_skill(
        Skill(name="docs", description="docs", tags=[], class_="documentation"), text
    )
    assert core._tokenize("Write WRITE tests!") == {"write", "tests"}
    assert core._infer_task_class({"document", "guide"}) == "documentation"
    assert core._infer_task_class({"write", "test"}) == "operation"


def test_output_path_rejects_invalid_slug(tmp_path: Path) -> None:
    with pytest.raises(core.SummarySlugError, match="kebab-case"):
        core._output_path("not/a-slug", tmp_path)


def test_write_json_new_cleans_up_after_link_failure(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output.json"
    with (
        patch("lib.generate_task_json.core.os.link", side_effect=OSError("boom")),
        pytest.raises(OSError, match="boom"),
    ):
        core._write_json_new(output, {"key": "value"})
    assert list(tmp_path.glob(".output.json.tmp_*")) == []
