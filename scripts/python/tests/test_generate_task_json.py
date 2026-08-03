"""Unit tests for direct task packet generation."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import lib.schema.core as schema_core
from lib.generate_task_json.core import (
    GenerationValidationError,
    generate_task_json,
)
from lib.schema import load_task_packet_schema


def _inventory(root: Path) -> list[dict[str, object]]:
    skill = root / "demo" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text("# Demo\n", encoding="utf-8")
    return [
        {
            "name": "demo",
            "description": "Use when testing packets",
            "selection": {"role": "owner", "tags": {"actions": ["test"]}},
            "class": "operation",
            "path": str(skill),
            "source": "project",
        }
    ]


def _packet() -> dict[str, object]:
    return {
        "summary": "A valid packet",
        "tasks": [
            {
                "purpose": "Run the packet test.",
                "context": "x" * 200,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["demo"],
                "executionInstructions": [{"step": 1, "action": "Run it."}],
                "expectedOutput": "A passing test.",
            }
        ],
    }


def test_explicit_output_file_is_atomic_and_rejects_collision(tmp_path: Path) -> None:
    inventory = _inventory(tmp_path)
    destination = tmp_path / "packet.json"
    assert (
        generate_task_json(
            _packet(),
            skills_index=inventory,
            inventory_project_root=tmp_path,
            output_file=destination,
        )
        == destination
    )
    assert json.loads(destination.read_text(encoding="utf-8")) == _packet()
    with pytest.raises(OSError, match="already exists"):
        generate_task_json(
            _packet(),
            skills_index=inventory,
            inventory_project_root=tmp_path,
            output_file=destination,
        )


def test_output_directory_mode_derives_safe_name(tmp_path: Path) -> None:
    inventory = _inventory(tmp_path)
    destination = generate_task_json(
        _packet(),
        skills_index=inventory,
        inventory_project_root=tmp_path,
        output_dir=tmp_path / "tasks",
    )
    assert destination.parent == tmp_path / "tasks"
    assert destination.suffix == ".json"


def test_direct_selection_rejects_provider_and_invalid_packet(tmp_path: Path) -> None:
    inventory = _inventory(tmp_path)
    with pytest.raises(ValueError, match="completed packets"):
        generate_task_json(
            _packet(),
            skills_index=inventory,
            provider=object(),
            output_file=tmp_path / "x.json",
        )
    with pytest.raises(GenerationValidationError):
        generate_task_json({}, skills_index=inventory, output_file=tmp_path / "x.json")


def test_packaged_schema_matches_repository_schema() -> None:
    repository = (
        Path(__file__).resolve().parents[3]
        / "skills/breakdown-tasks/schema/task-packet.schema.json"
    )
    packaged = schema_core.resources.files("lib.generate_task_json").joinpath(
        "assets/task-packet.schema.json"
    )
    assert packaged.read_bytes() == repository.read_bytes()
    assert load_task_packet_schema() == json.loads(
        repository.read_text(encoding="utf-8")
    )


@pytest.mark.parametrize("payload", ["{", "[]"])
def test_packaged_schema_errors_are_not_silently_repaired(
    monkeypatch: pytest.MonkeyPatch, payload: str
) -> None:
    class BrokenResource:
        def joinpath(self, _name: str) -> BrokenResource:
            return self

        def open(self, *_args: object, **_kwargs: object) -> io.StringIO:
            return io.StringIO(payload)

    monkeypatch.setattr(schema_core.resources, "files", lambda _: BrokenResource())
    with pytest.raises((json.JSONDecodeError, ValueError)):
        load_task_packet_schema()


def test_packaged_schema_missing_resource_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MissingResource:
        def joinpath(self, _name: str) -> MissingResource:
            return self

        def open(self, *_args: object, **_kwargs: object) -> io.StringIO:
            raise FileNotFoundError("schema resource missing")

    monkeypatch.setattr(schema_core.resources, "files", lambda _: MissingResource())
    with pytest.raises(FileNotFoundError, match="missing"):
        load_task_packet_schema()
