"""Regression checks for executable skill-assignment class composition."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BREAKDOWN = ROOT / "skills" / "breakdown-tasks"
ASSIGNMENT = BREAKDOWN / "reference" / "skill-assignment.md"
WORKFLOW = BREAKDOWN / "SKILL.md"
SCHEMA = BREAKDOWN / "schema" / "task-packet.schema.json"
PLAN_WRITER = ROOT / "skills" / "plan-writer" / "SKILL.md"
WORKER = ROOT / "agents" / "worker.md"
TASK_DELEGATION = ROOT / "skills" / "task-delegation" / "SKILL.md"


def test_breakdown_assignment_requires_one_operation_plus_optional_docs() -> None:
    assignment = ASSIGNMENT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "exactly one `class: operation`" in assignment
    assert "zero to two `class: documentation`" in assignment
    assert "do not publish two operation owners" in assignment
    assert "no operation owner" in assignment
    assert "more than two documentation assignments" in assignment

    assert "exactly one `class: operation` execution owner" in workflow
    assert "zero to two materially relevant `class: documentation`" in workflow
    assert "do not publish multiple operation owners" in workflow
    assert "exactly one operation owner and zero to two" in workflow


def test_plan_writer_uses_same_assignment_composition() -> None:
    text = PLAN_WRITER.read_text(encoding="utf-8")

    assert "exactly one `class: operation` execution owner" in text
    assert "zero to two materially relevant `class: documentation`" in text
    assert "do not publish multiple operation owners" in text
    assert "exactly one operation owner and zero to two documentation" in text


def test_worker_cannot_silently_acquire_second_operation_owner() -> None:
    worker = WORKER.read_text(encoding="utf-8")
    delegation = TASK_DELEGATION.read_text(encoding="utf-8")

    assert "do not add or substitute another operation skill inline" in worker
    assert "do not add a second operation owner during execution" in worker
    assert "supervisory adaptation may re-dispatch" in worker

    assert "may not silently add or substitute a\nsecond operation owner" in delegation
    assert "changing the operation owner is a supervisory adaptation" in delegation
    assert "may gain passive documentation context" in delegation


def test_schema_keeps_compatible_flat_one_to_three_skill_representation() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    skills = schema["definitions"]["TaskPacket"]["properties"]["skills"]

    assert skills["type"] == "array"
    assert skills["items"] == {"type": "string"}
    assert skills["uniqueItems"] is True
    assert skills["minItems"] == 1
    assert skills["maxItems"] == 3
