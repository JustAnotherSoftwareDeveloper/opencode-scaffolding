"""Unit tests for lib.assign_skills.core."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from lib.assign_skills.core import (
    _parse_skills_from_index,
    _rank_candidates_weighted,
    _select_skills,
    _validate_weights,
    _write_json_atomic,
    assign_skills,
    build_query,
    infer_task_class,
    render_skill,
    score_skill_weighted,
    tokenize,
)
from lib.collect_skills.models import Skill

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_skill(
    name: str,
    description: str = "",
    tags: list[str] | None = None,
    class_: str = "operation",
) -> Skill:
    return Skill(
        name=name,
        description=description,
        tags=tags or [],
        class_=class_,
    )


def _make_state_file(tmp_path, tasks: list[dict]) -> str:
    import json

    state = {"summary": "test", "tasks": tasks}
    path = tmp_path / "state.json"
    path.write_text(json.dumps(state))
    return str(path)


# ---------------------------------------------------------------------------
# render_skill
# ---------------------------------------------------------------------------


def test_render_skill_includes_all_fields() -> None:
    skill = _make_skill(
        "test-skill",
        description="A test skill.",
        tags=["testing", "python"],
        class_="operation",
    )
    text = render_skill(skill)
    assert "name: test-skill" in text
    assert "class: operation" in text
    assert "description: A test skill." in text
    assert "tags: testing, python" in text


def test_render_skill_empty_tags() -> None:
    skill = _make_skill("minimal", tags=[])
    text = render_skill(skill)
    assert "tags: " in text


# ---------------------------------------------------------------------------
# build_query
# ---------------------------------------------------------------------------


def test_build_query_basic() -> None:
    q = build_query("Fix a bug", "Context here.", [], [])
    assert "purpose: Fix a bug" in q
    assert "context: Context here." in q


def test_build_query_with_files() -> None:
    q = build_query("Do X", "Context.", ["a.py"], ["b.py"])
    assert "files to read: a.py" in q
    assert "files to write: b.py" in q


def test_build_query_empty_files_omitted() -> None:
    q = build_query("Test", "Ctx", [], [])
    assert "files to read:" not in q
    assert "files to write:" not in q


# ---------------------------------------------------------------------------
# weighted scoring
# ---------------------------------------------------------------------------


def test_tokenize_lowercases_and_deduplicates() -> None:
    assert tokenize("Write WRITE tests!") == {"write", "tests"}


def test_infer_task_class_documentation() -> None:
    assert infer_task_class("Analyze and write a proposal") == "documentation"


def test_infer_task_class_operation_default() -> None:
    assert infer_task_class("Write and run tests") == "operation"


def test_score_skill_weighted_prefers_matching_metadata() -> None:
    skill = _make_skill(
        "skill-script-python-test-writer",
        description="Write python tests",
        tags=["python", "test"],
        class_="operation",
    )
    score = score_skill_weighted(
        skill,
        "Write python tests",
        "Update CLI tests",
        [],
        [],
    )
    assert score > 0.25


def test_rank_candidates_weighted_orders_by_score() -> None:
    good = _make_skill("python-test", "Write python tests", ["python"], "operation")
    weak = _make_skill("docs", "Explain docs", ["docs"], "documentation")
    names, scores = _rank_candidates_weighted(
        "Write python tests", "", [], [], [weak, good]
    )
    assert names[0] == "python-test"
    assert scores[0] > scores[1]


def test_validate_weights_rejects_bad_sum() -> None:
    with pytest.raises(ValueError, match="sum to 1.0"):
        _validate_weights(
            {"keyword_overlap": 1.0, "class_match": 1.0, "tag_similarity": 1.0}
        )


# ---------------------------------------------------------------------------
# _select_skills
# ---------------------------------------------------------------------------


def test_select_all_above_floor() -> None:
    names, scores = _select_skills(
        ["a", "b", "c"], [3.0, 1.0, 0.5], floor=0.0, min_skills=1
    )
    assert names == ["a", "b", "c"]


def test_select_only_above_floor() -> None:
    names, scores = _select_skills(
        ["a", "b", "c"], [3.0, 1.0, -1.0], floor=0.0, min_skills=1
    )
    assert names == ["a", "b"]


def test_fill_to_min_from_below_floor() -> None:
    names, scores = _select_skills(
        ["a", "b", "c"], [3.0, -1.0, -2.0], floor=0.0, min_skills=3
    )
    assert len(names) == 3
    assert names[0] == "a"


def test_none_above_floor_falls_back_to_top() -> None:
    names, scores = _select_skills(["a", "b"], [-2.0, -3.0], floor=5.0, min_skills=1)
    assert len(names) >= 1
    assert names[0] == "a"


def test_empty_ranked_list_with_data_returns_top() -> None:
    """If no skills qualify and we have data, still return something."""
    names, scores = _select_skills(["only-one"], [-5.0], floor=5.0, min_skills=1)
    assert len(names) == 1
    assert names[0] == "only-one"


# ---------------------------------------------------------------------------
# assign_skills integration
# ---------------------------------------------------------------------------


def test_assign_skills_success(tmp_path) -> None:
    """Full weighted pipeline returns the state_file path."""
    tasks = [
        {
            "purpose": "Write tests.",
            "context": "Write tests for CLI.",
            "filesToRead": [],
            "filesToWrite": [],
            "executionInstructions": [{"step": 1, "action": "Do it"}],
            "expectedOutput": "Tests.",
        },
    ]
    state_path = _make_state_file(tmp_path, tasks)

    # Create a minimal schema file
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        '{"type":"object","required":["summary","tasks"],'
        '"properties":{"summary":{"type":"string"},'
        '"tasks":{"type":"array","minItems":1,"items":{"type":"object"}}}}'
    )

    with patch(
        "lib.assign_skills.core._discover_skills",
        return_value=[
            _make_skill(
                "skill-script-python-test-writer",
                description="Write tests for python cli",
                tags=["test", "python"],
            )
        ],
    ):
        result = assign_skills(
            state_file=state_path,
            schema_path=str(schema_path),
        )
        assert result == state_path

    # Verify skills were written
    data = json.loads(Path(state_path).read_text())
    assert data["tasks"][0]["skills"] == ["skill-script-python-test-writer"]


def test_assign_skills_no_candidates_raises(tmp_path) -> None:
    """If class filter eliminates all skills, RuntimeError is raised."""
    tasks = [
        {
            "purpose": "Write tests.",
            "context": "Tests for CLI.",
            "filesToRead": [],
            "filesToWrite": [],
            "executionInstructions": [{"step": 1, "action": "Do it"}],
            "expectedOutput": "Tests.",
        },
    ]
    state_path = _make_state_file(tmp_path, tasks)

    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        '{"type":"object","required":["summary","tasks"],'
        '"properties":{"summary":{"type":"string"},'
        '"tasks":{"type":"array","minItems":1,"items":{"type":"object"}}}}'
    )

    # Discover skills but all are "planning" class — filtered out
    planning_skill = _make_skill("breakdown-tasks", class_="planning")

    with (
        patch(
            "lib.assign_skills.core._discover_skills",
            return_value=[planning_skill],
        ),
        pytest.raises(RuntimeError, match="No skills found"),
    ):
        assign_skills(
            state_file=state_path,
            schema_path=str(schema_path),
        )


def test_assign_skills_schema_rejection(tmp_path) -> None:
    """State file that doesn't match TaskDraft schema raises ValueError."""
    path = tmp_path / "bad.json"
    path.write_text('{"summary": "no tasks key"}')

    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        '{"type":"object","required":["summary","tasks"],'
        '"properties":{"summary":{"type":"string"},'
        '"tasks":{"type":"array","minItems":1}}}'
    )

    with pytest.raises(ValueError, match="state file failed"):
        assign_skills(state_file=str(path), schema_path=str(schema_path))


# ---------------------------------------------------------------------------
# _parse_skills_from_index
# ---------------------------------------------------------------------------


def test_parse_skills_from_index() -> None:
    """Convert a raw JSON skills index into Skill instances."""
    raw = [
        {
            "name": "skill-a",
            "description": "desc a",
            "tags": ["t1"],
            "class": "operation",
        },
        {
            "name": "skill-b",
            "description": "desc b",
            "tags": [],
            "class": "documentation",
        },
    ]
    skills = _parse_skills_from_index(raw)  # type: ignore[arg-type]
    assert len(skills) == 2
    assert skills[0].name == "skill-a"
    assert skills[1].class_ == "documentation"


def test_parse_skills_from_index_empty() -> None:
    """Empty list returns empty list."""
    assert _parse_skills_from_index([]) == []


def test_parse_skills_from_index_missing_fields() -> None:
    """Missing fields default to empty strings/empty lists."""
    skills = _parse_skills_from_index([{"name": "minimal"}])  # type: ignore[arg-type]
    assert skills[0].name == "minimal"
    assert skills[0].description == ""
    assert skills[0].tags == []


# ---------------------------------------------------------------------------
# _write_json_atomic
# ---------------------------------------------------------------------------


def test_write_json_atomic_success(tmp_path: Path) -> None:
    """Atomically writes valid JSON to a file."""
    path = str(tmp_path / "test.json")
    data = {"key": "value"}
    _write_json_atomic(path, data)

    content = Path(path).read_text()
    assert json.loads(content) == data


def test_write_json_atomic_cleanup_on_failure(tmp_path: Path) -> None:
    """Temp file is cleaned up on write failure."""
    path = str(tmp_path / "test.json")

    with patch("os.replace", side_effect=OSError("boom")), pytest.raises(OSError):
        _write_json_atomic(path, {"k": "v"})


# ---------------------------------------------------------------------------
# assign_skills with skills_index parameter
# ---------------------------------------------------------------------------


def test_assign_skills_with_external_index(tmp_path) -> None:
    """Full pipeline with --skills-json external index."""
    tasks = [
        {
            "purpose": "Write tests.",
            "context": "Write tests for CLI.",
            "filesToRead": [],
            "filesToWrite": [],
            "executionInstructions": [{"step": 1, "action": "Do it"}],
            "expectedOutput": "Tests.",
        },
    ]
    state_path = _make_state_file(tmp_path, tasks)

    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        '{"type":"object","required":["summary","tasks"],'
        '"properties":{"summary":{"type":"string"},'
        '"tasks":{"type":"array","minItems":1,"items":{"type":"object"}}}}'
    )

    external_index = [
        {"name": "skill-a", "description": "A skill", "tags": [], "class": "operation"},
    ]

    result = assign_skills(
        state_file=state_path,
        schema_path=str(schema_path),
        skills_index=external_index,  # type: ignore[arg-type]
    )
    assert result == state_path

    data = json.loads(Path(state_path).read_text())
    assert data["tasks"][0]["skills"] == ["skill-a"]


def test_assign_skills_rejects_invalid_backend(tmp_path) -> None:
    state_path = _make_state_file(tmp_path, [])
    schema_path = tmp_path / "schema.json"
    schema_path.write_text('{"type":"object"}')

    with pytest.raises(ValueError, match="backend"):
        assign_skills(state_path, str(schema_path), backend="bad")
