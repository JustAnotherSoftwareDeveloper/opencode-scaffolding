"""Direct-call coverage for task structure validation and bounded auto-fixes."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from lib.validate_task_structure import core

pytestmark = pytest.mark.unit


def _task(task_id: str = "one", **updates: object) -> dict[str, object]:
    task: dict[str, object] = {
        "taskId": task_id,
        "verificationCoverage": {"observable": ["the result is checked"]},
        "dependencies": [],
        "filesToWrite": [],
        "filesToRead": [],
        "skills": [],
        "executionInstructions": [],
    }
    task.update(updates)
    return task


def _root(*tasks: dict[str, object]) -> dict[str, object]:
    ids = [str(task["taskId"]) for task in tasks]
    return {
        "summary": "A canonical structural packet.",
        "slug": "structural-tests",
        "tasks": list(tasks),
        "boundaryReview": {
            "taskReviews": {
                task_id: {
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
                for task_id in ids
            },
            "warningDispositions": {},
        },
    }


def test_root_validation_reports_task_review_and_warning_references() -> None:
    """Check exact review coverage and consistency for each final task ID."""
    packet = _root(_task())
    review = packet["boundaryReview"]["taskReviews"]
    del review["one"]
    review["unknown"] = {
        "preAssignmentDisposition": "single-result",
        "acceptanceDisposition": "accepted",
    }
    review["extra-evidence"] = {
        "preAssignmentDisposition": "single-result",
        "acceptanceDisposition": "accepted",
        "indivisibilityEvidence": {},
    }
    packet["boundaryReview"]["warningDispositions"] = {
        "unknown-reference": {
            "taskId": "absent",
            "disposition": "split",
        },
        "inconsistent-acceptance": {
            "taskId": "one",
            "disposition": "accepted-indivisible",
        },
    }

    valid, diagnostics = core.validate_root(packet, {})

    assert valid is False
    assert any(
        "boundary-review-task-coverage" in item for item in diagnostics
    )
    assert any(
        "boundary-review-task-reference" in item for item in diagnostics
    )
    assert any(
        "boundary-review-indivisibility-evidence" in item
        for item in diagnostics
    )
    assert any(
        "boundary-review-warning-reference" in item for item in diagnostics
    )
    assert any(
        "boundary-review-warning-consistency" in item
        for item in diagnostics
    )


def test_metadata_validation_reports_identity_and_write_conflicts() -> None:
    """Reject duplicate IDs, missing observables, and write races."""
    first = _task(
        "same",
        verificationCoverage={"observable": []},
        dependencies=[{"taskId": "same"}, {"taskId": "missing"}],
        filesToWrite=["shared.txt", 4],
    )
    second = _task("same", filesToWrite=["shared.txt"])
    packet = _root(first, second)

    valid, diagnostics = core.validate(packet, {})

    assert valid is False
    assert any("identity" in item for item in diagnostics)
    assert any("verification-coverage" in item for item in diagnostics)
    assert any("dependency-reference" in item for item in diagnostics)
    assert sum("dependency-cycle" in item for item in diagnostics) >= 1
    assert any("write-target-conflict" in item for item in diagnostics)


def test_metadata_cycles_and_write_sharing_distinguish_safe_edges() -> None:
    """Allow serialized or coupled writes while detecting graph back-edges."""
    first = _task("first", filesToWrite=["shared.txt"])
    second = _task(
        "second",
        dependencies=[{"taskId": "first"}],
        filesToWrite=["shared.txt"],
        couplingRationale={"group": "one publication"},
    )
    packet = _root(first, second)
    packet["tasks"][0]["couplingRationale"] = {"group": "one publication"}
    assert core.validate(packet, {}) == (True, [])

    second["dependencies"] = [{"taskId": "first"}]
    packet["tasks"][0]["dependencies"] = [{"taskId": "second"}]
    valid, diagnostics = core.validate(packet, {})
    assert valid is False
    assert any(
        "dependency graph contains a cycle" in item for item in diagnostics
    )


def test_metadata_skips_dependency_items_already_rejected_by_schema() -> None:
    """Let JSON Schema own type diagnostics for malformed dependency entries."""
    assert core._validate_metadata([_task(dependencies=[42])]) == []


def test_root_schema_errors_are_stably_formatted() -> None:
    """Format schema failures with a JSON path and boundary-specific context."""
    valid, diagnostics = core.validate_root(
        {"summary": "missing slug"},
        {"type": "object", "required": ["slug", "boundaryReview"]},
    )
    assert valid is False
    assert len(diagnostics) == 2
    assert any(
        item.startswith("ERROR [boundary-review-interface]")
        for item in diagnostics
    )


def test_file_and_step_helpers_cover_types_placeholders_and_order() -> None:
    """Report all actionable input and sequence problems in helper output."""
    errors = core._validate_file_array(
        ["", "<path>", "${root}", "{{name}}", "repeat", "repeat", None],
        "tasks[0]",
        "filesToRead",
    )
    assert len(errors) == 6
    assert any("placeholder path" in error for error in errors)
    assert any("duplicate entry" in error for error in errors)
    assert any("expected string" in error for error in errors)
    assert core._validate_file_array([], "task", "filesToWrite") == []
    assert core._validate_execution_steps(
        [{"step": 1}, {"step": 4}], "tasks[0]"
    ) == ["tasks[0].executionInstructions[1]: expected step 2, got 4"]


def test_auto_fix_normalizes_skills_and_leaves_non_lists_untouched() -> None:
    """Remove empty/duplicate entries and cap the list without side effects."""
    task_list = [
        {"skills": ["a", "", "a", "b", "c", "d"]},
        {"skills": "not-an-array"},
        {},
    ]
    assert core.auto_fix(task_list) is True
    assert task_list[0]["skills"] == ["a", "b", "c"]
    assert task_list[1]["skills"] == "not-an-array"
    assert core.auto_fix(task_list) is False


def test_auto_fix_task_structure_handles_bad_roots_and_repairable_schema_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Reject nonrepairable roots and persist valid skill repairs only."""
    path = tmp_path / "rootless.json"
    path.write_text("[]", encoding="utf-8")
    assert core.auto_fix_task_structure(path, {})["valid"] is False
    assert path.read_text(encoding="utf-8") == "[]"

    path.write_text("{}", encoding="utf-8")
    before = path.read_bytes()
    result = core.auto_fix_task_structure(path, {"required": ["summary"]})
    assert result["valid"] is False
    assert path.read_bytes() == before

    packet = _root(_task(skills=["one", "one", "", "two", "three", "four"]))
    path.write_text(json.dumps(packet), encoding="utf-8")
    error = jsonschema.ValidationError("duplicate skills")
    error.absolute_path.extend(["tasks", 0, "skills"])
    error.validator = "uniqueItems"
    calls = 0

    def schema_errors(_parsed: object, _schema: dict[str, object]):
        nonlocal calls
        calls += 1
        if calls == 1:
            return [error]
        return []

    monkeypatch.setattr(core, "_root_schema_errors", schema_errors)
    fixed = core.auto_fix_task_structure(path, {})
    assert fixed == {"valid": True, "fixed": True}
    repaired = json.loads(path.read_text(encoding="utf-8"))
    assert repaired["tasks"][0]["skills"] == ["one", "two", "three"]


def test_auto_fix_task_structure_rejects_bad_task_shapes_and_reports_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Return structured errors without writing malformed task arrays."""
    path = tmp_path / "bad-tasks.json"
    path.write_text(json.dumps({"tasks": ["not-a-task"]}), encoding="utf-8")
    assert core.auto_fix_task_structure(path, {})["valid"] is False

    packet = _root(_task(skills=["stable"]))
    path.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr(core, "validate", lambda *_: (False, ["still invalid"]))
    result = core.auto_fix_task_structure(path, {})
    assert result == {"valid": False, "errors": ["still invalid"]}


def test_auto_fix_task_structure_preserves_warnings_and_enforces_retry_limit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Retain advisory diagnostics and stop after bounded repair attempts."""
    path = tmp_path / "packet.json"
    packet = _root(_task(skills=["stable"]))
    path.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr(
        core, "validate", lambda *_: (True, ["WARNING advisory"])
    )
    result = core.auto_fix_task_structure(path, {})
    assert result == {
        "valid": True,
        "fixed": False,
        "diagnostics": ["WARNING advisory"],
    }

    attempts = 0

    def changing_fix(tasks: list[dict[str, object]]) -> bool:
        nonlocal attempts
        attempts += 1
        tasks[0]["cycle"] = attempts
        return True

    monkeypatch.setattr(core, "auto_fix", changing_fix)
    monkeypatch.setattr(core, "validate", lambda *_: (False, ["still invalid"]))
    bounded = core.auto_fix_task_structure(path, {})
    assert bounded == {"valid": False, "errors": ["still invalid"]}
    assert attempts == 3


def test_auto_fix_revalidates_schema_and_boundary_after_skill_repair(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Do not write repairs when revalidation exposes additional errors."""
    path = tmp_path / "packet.json"
    packet = _root(_task(skills=["a", "a"]))
    packet["boundaryReview"]["warningDispositions"] = {
        "unknown-task": {"taskId": "absent", "disposition": "split"}
    }
    original = json.dumps(packet)
    path.write_text(original, encoding="utf-8")

    repairable = jsonschema.ValidationError("duplicate skills")
    repairable.absolute_path.extend(["tasks", 0, "skills"])
    repairable.validator = "uniqueItems"
    changed_root = jsonschema.ValidationError("new root constraint")
    changed_root.absolute_path.append("slug")
    changed_root.validator = "minLength"
    calls = 0

    def root_errors(_packet: object, _schema: dict[str, object]):
        nonlocal calls
        calls += 1
        if calls == 1:
            return [repairable]
        if calls == 2:
            return [changed_root]
        return []

    monkeypatch.setattr(core, "_root_schema_errors", root_errors)
    schema_failure = core.auto_fix_task_structure(path, {})
    assert schema_failure["valid"] is False
    assert "new root constraint" in schema_failure["errors"][0]
    assert path.read_text(encoding="utf-8") == original

    calls = 0

    def root_valid_after_repair(
        _packet: object, _schema: dict[str, object]
    ):
        nonlocal calls
        calls += 1
        return [repairable] if calls == 1 else []

    monkeypatch.setattr(core, "_root_schema_errors", root_valid_after_repair)
    boundary_failure = core.auto_fix_task_structure(path, {})
    assert boundary_failure["valid"] is False
    assert any(
        "unknown taskId" in error for error in boundary_failure["errors"]
    )
    assert path.read_text(encoding="utf-8") == original
