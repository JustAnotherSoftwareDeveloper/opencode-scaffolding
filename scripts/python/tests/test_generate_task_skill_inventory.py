"""Focused tests for the generator's frozen collector boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.generate_task_json.skill_inventory import (
    FrozenSkillInventory,
    SkillInventoryError,
    validate_skill_inventory,
)


def record(tmp_path: Path, **changes: object) -> dict:
    path = tmp_path / "python-test" / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# skill\n", encoding="utf-8")
    value: dict = {
        "name": "python-test",
        "description": "Write Python tests",
        "selection": {"role": "owner", "tags": {"actions": ["write-tests"]}},
        "class": "operation",
        "path": str(path),
        "source": "project",
    }
    value.update(changes)
    return value


def test_valid_record_is_normalized_and_immutable(tmp_path: Path) -> None:
    result = validate_skill_inventory(
        [record(tmp_path, version="1", metadata={"team": "tools"})],
        project_root=tmp_path,
    )
    assert isinstance(result, FrozenSkillInventory)
    assert result.names == ("python-test",)
    assert result[0].path == (tmp_path / "python-test" / "SKILL.md").resolve()
    with pytest.raises(TypeError):
        result[0].optional["version"] = "2"  # type: ignore[index]


@pytest.mark.parametrize(
    ("inventory", "message"),
    [
        ([], "non-empty"),
        ([{"name": "x"}], "missing"),
        (None, "non-empty"),
    ],
)
def test_shape_is_fail_closed(tmp_path: Path, inventory: object, message: str) -> None:
    with pytest.raises(SkillInventoryError, match=message):
        validate_skill_inventory(inventory, project_root=tmp_path)


@pytest.mark.parametrize(
    "field", ["name", "description", "selection", "class", "path", "source"]
)
def test_required_fields_are_exact(tmp_path: Path, field: str) -> None:
    value = record(tmp_path)
    del value[field]
    with pytest.raises(SkillInventoryError):
        validate_skill_inventory([value], project_root=tmp_path)


@pytest.mark.parametrize(
    "changes",
    [
        {"extra": True},
        {"name": "not canonical"},
        {"class": "planning"},
        {"source": "archive"},
        {"selection": {"role": "owner", "tags": {}, "supports": ["bad name"]}},
    ],
)
def test_invalid_record_fields_fail_closed(tmp_path: Path, changes: dict) -> None:
    with pytest.raises(SkillInventoryError):
        validate_skill_inventory([record(tmp_path, **changes)], project_root=tmp_path)


def test_duplicates_and_external_paths_fail_closed(tmp_path: Path) -> None:
    first = record(tmp_path)
    second = record(tmp_path)
    with pytest.raises(SkillInventoryError, match="duplicate"):
        validate_skill_inventory([first, second], project_root=tmp_path)
    outside = tmp_path / "outside" / "SKILL.md"
    outside.parent.mkdir()
    outside.write_text("# outside\n", encoding="utf-8")
    with pytest.raises(SkillInventoryError, match="outside"):
        validate_skill_inventory(
            [record(tmp_path, path=str(outside))], project_root=tmp_path / "other"
        )
