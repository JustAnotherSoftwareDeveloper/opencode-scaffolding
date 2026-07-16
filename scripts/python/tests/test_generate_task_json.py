"""Tests for the generate-task-json library."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from lib.collect_skills.models import Skill
from lib.generate_task_json import core

VALID_CONTEXT = (
    "Add focused Python tests for the example CLI behavior and preserve the existing "
    "test layout. Cover the supported input path, error handling, and output contract "
    "without changing unrelated production code or adding dependencies."
)


def _drafts() -> dict:
    return {
        "summary": "Generate test task packets.",
        "tasks": [
            {
                "purpose": "Write Python tests.",
                "context": VALID_CONTEXT,
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


def test_generate_task_json_writes_assigned_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
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
    assert output == tmp_path / ".tasks" / "1700000000123-generate-tests.json"
    assert result["tasks"][0]["skills"] == ["python-test"]


def test_generate_task_json_writes_to_explicit_output_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
    output_dir = tmp_path / "state"
    output = core.generate_task_json(
        _drafts(),
        "generate-tests",
        output_dir=output_dir,
        skills_index=[{"name": "python-test", "class": "operation"}],
    )
    assert output == output_dir / "1700000000123-generate-tests.json"


def test_generate_task_json_writes_to_explicit_output_file(tmp_path: Path) -> None:
    output = core.generate_task_json(
        _drafts(),
        output_file=tmp_path / "plan" / "tasks.json",
        skills_index=[{"name": "python-test", "class": "operation"}],
    )
    assert output == tmp_path / "plan" / "tasks.json"


def test_generate_task_json_rejects_mixed_destination_modes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        core.generate_task_json(
            _drafts(),
            "generate-tests",
            output_file=tmp_path / "tasks.json",
            skills_index=[{"name": "python-test", "class": "operation"}],
        )


def test_generate_task_json_rejects_non_json_explicit_output(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=".json suffix"):
        core.generate_task_json(
            _drafts(),
            output_file=tmp_path / "tasks.txt",
            skills_index=[{"name": "python-test", "class": "operation"}],
        )


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


def test_generate_task_json_rejects_context_below_minimum(tmp_path: Path) -> None:
    drafts = _drafts()
    drafts["tasks"][0]["context"] = "x" * 199
    with pytest.raises(core.GenerationValidationError, match="input failed"):
        core.generate_task_json(
            drafts,
            "generate-tests",
            project_root=tmp_path,
            skills_index=[{"name": "python-test", "class": "operation"}],
        )
    assert not (tmp_path / ".tasks").exists()


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


def test_select_skills_does_not_select_a_class_only_match() -> None:
    """Do not assign unrelated skills solely because their class matches."""
    task = {
        "purpose": "Update the planning architecture reference.",
        "context": (
            "Revise the planning lifecycle reference skill frontmatter and required "
            "sections. Preserve passive reference content and validate the updated "
            "skill against authoring requirements without generating scripts or tests."
        ),
        "filesToRead": ["skills/planning-pipeline-architecture/SKILL.md"],
        "filesToWrite": ["skills/planning-pipeline-architecture/SKILL.md"],
        "executionInstructions": [{"step": 1, "action": "Update the reference."}],
        "expectedOutput": "A validated planning reference skill.",
    }
    factory = Skill(
        name="skill-factory",
        description="Create and update OpenCode skill files",
        tags=["skill-authoring", "frontmatter-validation"],
        class_="operation",
    )
    bash_tests = Skill(
        name="skill-script-bash-test-writer",
        description="Generate bats tests for bash scripts",
        tags=["bash-testing", "bats", "test-generation"],
        class_="operation",
    )

    assert core._select_skills(task, [factory, bash_tests]) == ["skill-factory"]


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
    assert "Python tests." in text
    assert "scripts/python/src/cli/example.py" not in text
    assert "scripts/python/tests/test_example.py" not in text
    assert core._score_skill(_skill(), text) > core._score_skill(
        Skill(name="docs", description="docs", tags=[], class_="documentation"), text
    )
    assert core._tokenize("Write WRITE tests!") == {"write", "tests"}
    assert core._infer_task_class({"document", "guide"}) == "documentation"
    assert core._infer_task_class({"write", "test"}) == "operation"


def test_task_text_excludes_file_paths() -> None:
    """File paths in filesToRead and filesToWrite are absent from scoring text."""
    task = _drafts()["tasks"][0]
    text = core._task_text(task)
    assert "scripts/python/src/cli/example.py" not in text
    assert "scripts/python/tests/test_example.py" not in text


def test_task_text_includes_expected_output() -> None:
    """expectedOutput content is present in the task scoring text."""
    task = _drafts()["tasks"][0]
    text = core._task_text(task)
    assert "Python tests." in text


def test_skill_assignment_ignores_misleading_file_paths() -> None:
    """A task touching skill-factory's SKILL.md must not assign skill-factory
    based on file-path tokens alone when purpose/context are unrelated."""
    task = {
        "purpose": "Fix a typo in the README",
        "context": (
            "Correct a typographical error in the project's main README file. "
            "This documentation guide contains a misspelled word that could "
            "confuse new users. The fix involves locating the exact line with "
            "the error, replacing the incorrect spelling, and verifying the "
            "change renders properly in the rendered output. No functional "
            "code changes are required. This is a straightforward documentation "
            "correction that improves the quality of the project's primary "
            "entry point for new contributors and serves as a reference for "
            "the entire project."
        ),
        "filesToRead": ["README.md"],
        "filesToWrite": ["skills/skill-factory/SKILL.md"],
        "executionInstructions": [{"step": 1, "action": "Fix the typo."}],
        "expectedOutput": "The README with the typo corrected.",
    }
    skill_factory = Skill(
        name="skill-factory",
        description="Create and manage OpenCode skills",
        tags=["skill", "factory", "create", "manage"],
        class_="operation",
    )
    readme_editor = Skill(
        name="readme-editor",
        description="Fix typo and formatting error in documentation and README file",
        tags=["readme", "documentation", "fix", "typo", "docs"],
        class_="documentation",
    )
    selected = core._select_skills(task, [skill_factory, readme_editor])
    assert "skill-factory" not in selected
    assert "readme-editor" in selected


def test_score_skill_tokenizes_compound_tags() -> None:
    """Hyphenated tags contribute their individual terms to tag similarity."""
    matching = Skill(
        name="workspace",
        description="",
        tags=[
            "plan-workspace",
            "task-json",
            "source-documents",
            "workspace-generation",
        ],
        class_="operation",
    )
    unrelated = Skill(
        name="proposal",
        description="",
        tags=[
            "decision-record",
            "evidence-linking",
            "proposal-authoring",
            "workspace-creation",
        ],
        class_="operation",
    )

    assert core._score_skill(matching, "create a plan workspace") > core._score_skill(
        unrelated,
        "create a plan workspace",
    )


def test_output_path_prefixes_slug_with_epoch_milliseconds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
    assert core._output_path("generate-tests", tmp_path / ".tasks") == (
        tmp_path / ".tasks" / "1700000000123-generate-tests.json"
    )


def test_output_path_rejects_invalid_slug(tmp_path: Path) -> None:
    with pytest.raises(core.SummarySlugError, match="kebab-case"):
        core._output_path("not/a-slug", tmp_path / ".tasks")


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
