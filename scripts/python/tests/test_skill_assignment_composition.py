"""Regression checks for executable skill-assignment class composition."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


ROOT = Path(__file__).resolve().parents[3]
BREAKDOWN = ROOT / "skills" / "breakdown-tasks"
ASSIGNMENT = BREAKDOWN / "reference" / "skill-assignment.md"
WORKFLOW = BREAKDOWN / "SKILL.md"
SCHEMA = BREAKDOWN / "schema" / "task-packet.schema.json"
PLAN_WRITER = ROOT / "skills" / "plan-writer" / "SKILL.md"
WORKER = ROOT / "agents" / "worker.md"
TASK_DELEGATION = ROOT / "skills" / "task-delegation" / "SKILL.md"


def normalized(path: Path) -> str:
    """Normalize policy prose across case and layout changes."""
    return " ".join(path.read_text(encoding="utf-8").split()).casefold()


def test_breakdown_assignment_requires_one_operation_plus_optional_docs() -> (
    None
):
    """Verify breakdown assignments require one operation and optional docs."""
    assignment = normalized(ASSIGNMENT)
    workflow = normalized(WORKFLOW)

    assert "select exactly one `class: operation` execution owner" in assignment
    assert "select zero to two `class: documentation` skills" in assignment
    assert "do not publish two operation owners" in assignment
    assert "no operation owner" in assignment
    assert "more than two documentation skills" in assignment
    assert "stale or substituted path" in assignment

    assert "select exactly one `class: operation` execution owner" in workflow
    assert (
        "add zero to two materially relevant `class: documentation` skills"
        in workflow
    )
    assert "do not publish multiple operation owners" in workflow
    assert (
        "exactly one operation and zero to two documentation skills" in workflow
    )


def test_plan_writer_uses_same_assignment_composition() -> None:
    """Verify plan-writer uses the same operation and documentation limits."""
    text = normalized(PLAN_WRITER)

    assert "select exactly one `class: operation` execution owner" in text
    assert "zero documentation assignments is valid" in text
    assert "assign no more than two" in text
    assert "do not publish multiple operation owners" in text
    assert (
        "confirm exactly one operation owner and zero to two materially "
        "relevant" in text
    )


def test_worker_cannot_silently_acquire_second_operation_owner() -> None:
    """Verify workers cannot silently acquire a second operation owner."""
    worker = normalized(WORKER)
    delegation = normalized(TASK_DELEGATION)

    assert "do not add a second operation owner during execution" in worker
    assert "supervisory adaptation may re-dispatch" in worker
    assert "one operation owner and zero to two documentation skills" in worker

    assert "block on stale or substituted paths" in delegation
    assert (
        "changing the operation owner requires supervisory adaptation"
        in delegation
    )
    assert (
        "may explicitly load a materially relevant `documentation` skill"
        in delegation
    )
    assert (
        "ordinary execution may not load an additional operation owner"
        in delegation
    )


def test_schema_keeps_compatible_flat_one_to_three_skill_representation() -> (
    None
):
    """Verify the task schema retains its compatible skill-array shape."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    skills = schema["definitions"]["TaskPacket"]["properties"]["skills"]

    assert skills["type"] == "array"
    assert skills["items"] == {"type": "string"}
    assert skills["uniqueItems"] is True
    assert skills["minItems"] == 1
    assert skills["maxItems"] == 3
