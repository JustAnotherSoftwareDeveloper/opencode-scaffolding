"""Regression tests for v1 JSON and v2 TOON runbook validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from toon_format import encode

from lib.runbook_state import seed_runbook_state
from lib.runbook_toon import load_runbook, validate_runbook


REPO_ROOT = Path(__file__).resolve().parents[3]


def _step(step_id: str, depends_on: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": step_id,
        "depends_on": depends_on or [],
        "parallel_group": "group-1",
        "worker": {"family": "coding", "size": "md"},
        "skill": None,
        "minimum_capable_tier": "md",
        "context_package": {
            "user_requirement_slice": f"Test requirement for {step_id}",
            "relevant_proposal_sections": [],
            "relevant_state_files": [],
            "files_in_scope": [],
            "files_out_scope": [],
            "expected_return_format": "Test format",
        },
        "objective": f"Test step {step_id}",
        "expected_output": f"Test output {step_id}",
        "state_updates": [],
        "acceptance_criteria": [],
        "verification": f"Test verification {step_id}",
        "recovery": f"Test recovery {step_id}",
    }


def _runbook_data(runbook_id: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    step_ids = [step["id"] for step in steps]
    return {
        "artifact_type": "runbook",
        "schema_version": 1,
        "id": runbook_id,
        "title": "Test Runbook",
        "status": "executing",
        "created_at": "2026-05-15T00:00:00Z",
        "updated_at": "2026-05-15T00:00:00Z",
        "proposal": "../../.proposals/test.md",
        "plan": "../../.plans/test.md",
        "state_dir": f"../../.state/{runbook_id}/",
        "active_step": step_ids[0] if step_ids else None,
        "objective": "Test runbook validation",
        "plan_summary": "Testing runbook validation",
        "inputs": [],
        "constraints": [],
        "execution_strategy": "Test strategy",
        "delegation_map": {},
        "steps": steps,
        "dependency_graph": {},
        "parallel_groups": {"group-1": step_ids} if step_ids else {},
        "state_initialization": {
            "metadata_schema_version": 1,
            "require_step_files": True,
            "step_file_extension": ".json",
            "main_dashboard": "MAIN.json",
        },
        "verification_gates": [],
        "embedded_quality_check": {
            "performed_by": None,
            "findings": [],
            "status": "pending",
        },
        "rollback_recovery": "Test recovery",
        "final_report_contract": "Test contract",
    }


def _write_v1_runbook(tmp_path: Path, runbook_id: str = "test-legacy-runbook") -> Path:
    runbook_dir = tmp_path / ".runbooks" / runbook_id
    runbook_dir.mkdir(parents=True)
    runbook_file = runbook_dir / "runbook.json"
    runbook_file.write_text(json.dumps(_runbook_data(runbook_id, [_step("01-example")]), indent=2), encoding="utf-8")
    return runbook_file


def _write_v2_runbook(
    tmp_path: Path,
    runbook_id: str = "test-v2-runbook",
    steps: list[dict[str, Any]] | None = None,
    *,
    step_refs: list[dict[str, str]] | None = None,
    state_dir: str | None = None,
) -> Path:
    steps = steps or [_step("01-example"), _step("02-another", ["01-example"])]
    runbook_dir = tmp_path / ".runbooks" / runbook_id
    steps_dir = runbook_dir / "steps"
    steps_dir.mkdir(parents=True)

    main_data = _runbook_data(runbook_id, steps)
    main_data["schema_version"] = 2
    main_data["format_version"] = 2
    main_data["state_dir"] = state_dir or f"../../.state/{runbook_id}/"
    main_data["steps"] = step_refs or [
        {"id": step["id"], "file": f"steps/{step['id']}.toon"} for step in steps
    ]

    main_file = runbook_dir / "main.toon"
    main_file.write_text(encode(main_data), encoding="utf-8")

    for step in steps:
        (steps_dir / f"{step['id']}.toon").write_text(encode(step), encoding="utf-8")

    return main_file


def test_legacy_v1_compatibility(tmp_path: Path) -> None:
    runbook_file = _write_v1_runbook(tmp_path)

    is_valid, messages = validate_runbook(runbook_file)
    assert is_valid, f"Legacy v1 runbook should pass validation: {messages}"

    result = load_runbook(runbook_file)
    assert result.runbook_id == "test-legacy-runbook"
    assert result.format_version == 1
    assert len(result.data["steps"]) == 1


def test_existing_execution_runbook_still_validates() -> None:
    runbook_path = REPO_ROOT / ".runbooks" / "1778843937-upgrade-runbooks-to-toon" / "runbook.json"

    is_valid, messages = validate_runbook(runbook_path)
    assert is_valid, f"Existing runbook should pass validation: {messages}"

    result = load_runbook(runbook_path)
    assert result.runbook_id == "1778843937-upgrade-runbooks-to-toon"
    assert result.format_version == 1


def test_valid_v2_runbook_loads_and_seeds_state(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path)

    is_valid, messages = validate_runbook(main_file)
    assert is_valid, f"Valid v2 runbook should pass validation: {messages}"

    result = load_runbook(main_file)
    assert result.runbook_id == "test-v2-runbook"
    assert result.format_version == 2
    assert [step.id for step in result.steps] == ["01-example", "02-another"]
    assert [step["id"] for step in result.data["steps"]] == ["01-example", "02-another"]

    state_dir = tmp_path / ".state" / "test-v2-runbook"
    state_dir.mkdir(parents=True)
    seed_runbook_state(result.data, main_file, state_dir)
    assert (state_dir / "metadata.json").exists()
    assert (state_dir / "MAIN.json").exists()
    assert (state_dir / "01-example.json").exists()
    assert (state_dir / "02-another.json").exists()


def test_v2_step_dependency_cycle_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(
        tmp_path,
        "test-cycle-runbook",
        [_step("01-example", ["02-another"]), _step("02-another", ["01-example"])],
    )

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("circular dependency" in msg.lower() for msg in messages), messages


def test_v2_filename_stem_mismatch_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(
        tmp_path,
        "test-mismatch-runbook",
        [_step("01-example")],
        step_refs=[{"id": "01-example", "file": "steps/02-wrong-name.toon"}],
    )
    wrong_file = main_file.parent / "steps" / "02-wrong-name.toon"
    wrong_file.write_text(encode(_step("01-example")), encoding="utf-8")

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("filename mismatch" in msg.lower() for msg in messages), messages


def test_v2_wrong_state_dir_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(
        tmp_path,
        "test-wrong-state-runbook",
        [_step("01-example")],
        state_dir="../../.state/wrong-runbook/",
    )

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("state_dir" in msg.lower() for msg in messages), messages


def test_v2_missing_step_file_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(
        tmp_path,
        "test-missing-step-runbook",
        [_step("01-example")],
        step_refs=[
            {"id": "01-example", "file": "steps/01-example.toon"},
            {"id": "02-missing", "file": "steps/02-missing.toon"},
        ],
    )

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("not found" in msg.lower() for msg in messages), messages


def test_v2_unknown_dependency_reference_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(
        tmp_path,
        "test-unknown-dependency-runbook",
        [_step("01-example", ["99-missing"])],
    )

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("unknown step" in msg.lower() for msg in messages), messages


def test_v2_unsafe_step_path_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(
        tmp_path,
        "test-unsafe-path-runbook",
        [_step("01-example")],
        step_refs=[{"id": "01-example", "file": "../01-example.toon"}],
    )

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("traversal" in msg.lower() or "steps/" in msg.lower() for msg in messages), messages


def test_v2_malformed_toon_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-malformed-runbook", [_step("01-example")])
    (main_file.parent / "steps" / "01-example.toon").write_text(
        'id: "01-example"\nbad[2]: only-one-value\n',
        encoding="utf-8",
    )

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("toon" in msg.lower() or "parsing" in msg.lower() for msg in messages), messages


def test_v2_non_object_root_fails(tmp_path: Path) -> None:
    runbook_dir = tmp_path / ".runbooks" / "test-non-object-runbook"
    runbook_dir.mkdir(parents=True)
    main_file = runbook_dir / "main.toon"
    main_file.write_text('["not", "an", "object"]\n', encoding="utf-8")

    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("root must be an object" in msg.lower() or "missing required" in msg.lower() for msg in messages), messages
