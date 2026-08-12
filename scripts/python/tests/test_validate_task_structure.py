"""test_validate_task_structure.py — Tests for validate-task-structure.

Covers the Click CLI (via CliRunner) and the lib validation module
(direct function calls), achieving 100% coverage of both
``cli.validate_task_structure`` and ``lib.validate_task_structure``.

Also verifies staged atomicity diagnostics, dependency validation, coupled-file
exceptions, and representative compound-task signals.

Run from ``scripts/python/``:

    uv run pytest tests/test_validate_task_structure.py -v \
        --cov=cli.validate_task_structure --cov=lib.validate_task_structure \
        --cov-report=term-missing
"""

from __future__ import annotations

import json
import unittest.mock
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.validate_task_structure import main
from lib.validate_task_structure import (
    _validate_execution_steps,
    _validate_file_array,
    auto_fix,
    auto_fix_task_structure,
    validate,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)

VALID_CONTEXT = (
    "Update the target source file while preserving its public behavior and existing "
    "interfaces. Read the listed files first, make only the requested change, and run "
    "the relevant checks before reporting the resulting deliverable."
)

assert SCHEMA_PATH.is_file(), f"Schema not found at {SCHEMA_PATH}"

# ---------------------------------------------------------------------------
# Fixtures — valid task data
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def schema_dict() -> dict:
    """Load the actual task-packet schema once per module."""
    from lib.schema import load_schema

    return load_schema(SCHEMA_PATH)


@pytest.fixture
def valid_task_1() -> dict:
    return {
        "taskId": "task-one",
        "purpose": "Task one purpose",
        "context": VALID_CONTEXT,
        "filesToRead": ["src/file1.py"],
        "filesToWrite": ["src/out1.py"],
        "skills": ["python"],
        "executionInstructions": [
            {"step": 1, "action": "Do step one"},
            {"step": 2, "action": "Do step two"},
        ],
        "expectedOutput": "Output for task one",
        "verificationCoverage": {
            "observable": ["Output exists"],
            "coverage": "complete",
        },
        "antiPatternSignals": ["none"],
        "purposeOutputAlignment": {
            "status": "aligned",
            "evidence": "The purpose maps to the single output.",
        },
    }


@pytest.fixture
def valid_task_2() -> dict:
    return {
        "taskId": "task-two",
        "purpose": "Task two purpose",
        "context": VALID_CONTEXT,
        "filesToRead": ["src/file2.py"],
        "filesToWrite": ["src/out2.py"],
        "skills": ["typescript"],
        "executionInstructions": [
            {"step": 1, "action": "Do step one"},
        ],
        "expectedOutput": "Output for task two",
        "verificationCoverage": {
            "observable": ["Output exists"],
            "coverage": "complete",
        },
        "antiPatternSignals": ["none"],
        "purposeOutputAlignment": {
            "status": "aligned",
            "evidence": "The purpose maps to the single output.",
        },
    }


@pytest.fixture
def valid_task_3() -> dict:
    return {
        "taskId": "task-three",
        "purpose": "Task three purpose",
        "context": VALID_CONTEXT,
        "filesToRead": ["src/file3a.py", "src/file3b.py"],
        "filesToWrite": ["src/out3.py"],
        "skills": ["python", "testing"],
        "executionInstructions": [
            {"step": 1, "action": "Do first thing"},
            {"step": 2, "action": "Do second thing"},
            {"step": 3, "action": "Do third thing"},
        ],
        "expectedOutput": "Output for task three",
        "verificationCoverage": {
            "observable": ["Output exists"],
            "coverage": "complete",
        },
        "antiPatternSignals": ["none"],
        "purposeOutputAlignment": {
            "status": "aligned",
            "evidence": "The purpose maps to the single output.",
        },
    }


@pytest.fixture
def valid_tasks(valid_task_1, valid_task_2, valid_task_3) -> list[dict]:
    """A valid task list with three tasks."""
    return [valid_task_1, valid_task_2, valid_task_3]


# ===========================================================================
# Unit tests — lib.validate_task_structure helper functions
# ===========================================================================


class TestValidateFileArray:
    """Tests for the file array validation helper."""

    def test_valid_non_empty_strings(self) -> None:
        """A list of non-empty unique strings produces no errors."""
        errors = _validate_file_array(
            ["src/a.py", "src/b.py"], "tasks[0]", "filesToRead"
        )
        assert errors == []

    def test_empty_array(self) -> None:
        """An empty array is allowed and returns no errors."""
        errors = _validate_file_array([], "tasks[0]", "filesToRead")
        assert errors == []

    def test_non_string_item(self) -> None:
        """A non-string item is rejected with a type error."""
        errors = _validate_file_array([42, "src/b.py"], "tasks[0]", "filesToRead")
        assert any("expected string, got int" in e for e in errors)

    def test_empty_string_item(self) -> None:
        """An empty string entry is rejected."""
        errors = _validate_file_array(["src/a.py", ""], "tasks[0]", "filesToRead")
        assert any("empty string not allowed" in e for e in errors)

    def test_duplicate_entry(self) -> None:
        """Duplicate entries are detected."""
        errors = _validate_file_array(
            ["src/a.py", "src/a.py"], "tasks[0]", "filesToRead"
        )
        assert any("duplicate entry" in e for e in errors)

    def test_multiple_errors(self) -> None:
        """Multiple errors are all reported."""
        errors = _validate_file_array([42, ""], "tasks[0]", "filesToWrite")
        assert len(errors) >= 2


class TestValidateExecutionSteps:
    """Tests for the execution steps validation helper."""

    def test_correct_sequential_steps(self) -> None:
        """Steps numbered 1, 2, 3 produce no errors."""
        steps = [
            {"step": 1, "action": "a"},
            {"step": 2, "action": "b"},
            {"step": 3, "action": "c"},
        ]
        assert _validate_execution_steps(steps, "tasks[0]") == []

    def test_wrong_starting_step(self) -> None:
        """Steps starting at 0 instead of 1 are caught."""
        steps = [{"step": 0, "action": "a"}]
        errors = _validate_execution_steps(steps, "tasks[0]")
        assert any("expected step 1, got 0" in e for e in errors)

    def test_skipped_step_number(self) -> None:
        """A gap in step numbering is caught."""
        steps = [
            {"step": 1, "action": "a"},
            {"step": 3, "action": "c"},
        ]
        errors = _validate_execution_steps(steps, "tasks[0]")
        assert any("expected step 2, got 3" in e for e in errors)

    def test_out_of_order_steps(self) -> None:
        """Steps in wrong order are caught."""
        steps = [
            {"step": 2, "action": "b"},
            {"step": 1, "action": "a"},
        ]
        errors = _validate_execution_steps(steps, "tasks[0]")
        assert any("expected step 1, got 2" in e for e in errors)


# ===========================================================================
# Unit tests — lib.validate_task_structure.validate()
# ===========================================================================


class TestValidateFunction:
    """Direct tests of the ``validate()`` function."""

    def test_valid_tasks(self, valid_tasks, schema_dict) -> None:
        """A fully valid task list returns (True, [])."""
        valid, errors = validate(valid_tasks, schema_dict)
        assert valid is True
        assert errors == []

    # --- Missing required keys (caught by jsonschema) ---

    def test_purpose_maxlength_exceeded(self, valid_task_1, schema_dict) -> None:
        """purpose longer than 200 chars is rejected."""
        task = dict(valid_task_1)
        task["purpose"] = "x" * 201
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("too long" in e for e in errors)

    def test_context_maxlength_exceeded(self, valid_task_1, schema_dict) -> None:
        """context longer than 8000 chars is rejected."""
        task = dict(valid_task_1)
        task["context"] = "x" * 8001
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("too long" in e for e in errors)

    def test_context_below_minimum_is_rejected(self, valid_task_1, schema_dict) -> None:
        """context shorter than 200 chars is rejected."""
        task = dict(valid_task_1)
        task["context"] = "x" * 199
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("too short" in error for error in errors)

    def test_context_at_minimum_is_accepted(self, valid_task_1, schema_dict) -> None:
        """context with exactly 200 chars is accepted."""
        task = dict(valid_task_1)
        task["context"] = "x" * 200
        valid, errors = validate([task], schema_dict)
        assert valid is True
        assert errors == []

    def test_expected_output_maxlength_exceeded(
        self, valid_task_1, schema_dict
    ) -> None:
        """expectedOutput longer than 2000 chars is rejected."""
        task = dict(valid_task_1)
        task["expectedOutput"] = "x" * 2001
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("too long" in e for e in errors)

    # --- Missing required keys (caught by jsonschema) ---

    @pytest.mark.parametrize(
        "missing_key",
        [
            "purpose",
            "context",
            "filesToRead",
            "filesToWrite",
            "skills",
            "executionInstructions",
            "expectedOutput",
        ],
    )
    def test_missing_required_key(self, valid_task_1, schema_dict, missing_key) -> None:
        """Each required key when missing triggers a schema validation error."""
        task = dict(valid_task_1)
        task.pop(missing_key)
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("tasks[0]" in e for e in errors), f"errors={errors}"

    # --- Type errors (caught by jsonschema) ---

    def test_string_instead_of_array_for_files_to_read(
        self, valid_task_1, schema_dict
    ) -> None:
        """filesToRead as string instead of array is rejected."""
        task = dict(valid_task_1)
        task["filesToRead"] = "not-an-array"
        valid, errors = validate([task], schema_dict)
        assert valid is False

    def test_string_instead_of_array_for_execution_instructions(
        self, valid_task_1, schema_dict
    ) -> None:
        """executionInstructions as string instead of array is rejected."""
        task = dict(valid_task_1)
        task["executionInstructions"] = "not-an-array"
        valid, errors = validate([task], schema_dict)
        assert valid is False

    # --- Custom validation: step numbering ---

    def test_bad_step_numbering(self, valid_task_1, schema_dict) -> None:
        """Non-sequential steps are caught."""
        task = dict(valid_task_1)
        task["executionInstructions"] = [
            {"step": 1, "action": "a"},
            {"step": 3, "action": "c"},
        ]
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("expected step 2" in e for e in errors)

    # --- Custom validation: file arrays ---

    def test_empty_files_to_read(self, valid_task_1, schema_dict) -> None:
        """Empty filesToRead is allowed and produces no errors."""
        task = dict(valid_task_1)
        task["filesToRead"] = []
        valid, errors = validate([task], schema_dict)
        assert valid is True
        assert not any("non-empty array" in e for e in errors)

    def test_empty_files_to_write(self, valid_task_1, schema_dict) -> None:
        """Empty filesToWrite is allowed and produces no errors."""
        task = dict(valid_task_1)
        task["filesToWrite"] = []
        valid, errors = validate([task], schema_dict)
        assert valid is True
        assert not any("non-empty array" in e for e in errors)

    def test_duplicate_in_files_to_read(self, valid_task_1, schema_dict) -> None:
        """Duplicate entries in filesToRead are caught."""
        task = dict(valid_task_1)
        task["filesToRead"] = ["src/a.py", "src/a.py"]
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("duplicate entry" in e for e in errors)

    # --- Mixed: schema + custom errors ---

    def test_multiple_errors_in_one_task(self, valid_task_1, schema_dict) -> None:
        """Multiple validation issues in one task produce all errors."""
        task = dict(valid_task_1)
        task["purpose"] = "x" * 201
        task["executionInstructions"] = [
            {"step": 2, "action": "wrong start"},
        ]
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("too long" in e for e in errors)
        assert any("expected step 1" in e for e in errors)


class TestAutoFix:
    """Tests for skills-only structural auto-fixes."""

    def test_auto_fix_normalizes_skills(self, valid_task_1: dict) -> None:
        """Remove empty skills, duplicates, and entries beyond the first three."""
        valid_task_1["skills"] = [
            "python",
            "",
            "python",
            "testing",
            "linting",
            "authoring",
        ]

        changed = auto_fix([valid_task_1])

        assert changed is True
        assert valid_task_1["skills"] == ["python", "testing", "linting"]

    def test_auto_fix_reports_no_change_for_normalized_skills(
        self, valid_task_1: dict
    ) -> None:
        """Leave an already normalized skills array unchanged."""
        assert auto_fix([valid_task_1]) is False

    def test_auto_fix_ignores_non_array_skills(self, valid_task_1: dict) -> None:
        valid_task_1["skills"] = "python"
        assert auto_fix([valid_task_1]) is False

    def test_auto_fix_state_file_writes_valid_normalized_tasks(
        self, valid_task_1: dict, schema_dict: dict, tmp_path: Path
    ) -> None:
        """Persist a valid state file after normalizing its skills array."""
        valid_task_1["skills"] = [
            "python",
            "",
            "python",
            "testing",
            "linting",
            "authoring",
        ]
        state_file = tmp_path / "state.json"
        state_file.write_text(
            json.dumps({"summary": "Test state", "tasks": [valid_task_1]})
        )

        result = auto_fix_task_structure(state_file, schema_dict)

        assert result == {"valid": True, "fixed": True}
        persisted = json.loads(state_file.read_text())
        assert persisted["tasks"][0]["skills"] == ["python", "testing", "linting"]

    def test_auto_fix_state_file_accepts_empty_skills(
        self, valid_task_1: dict, schema_dict: dict, tmp_path: Path
    ) -> None:
        """Accept an empty skills array without inventing a fallback skill."""
        valid_task_1["skills"] = []
        state_file = tmp_path / "state.json"
        state_file.write_text(
            json.dumps({"summary": "Test state", "tasks": [valid_task_1]})
        )

        result = auto_fix_task_structure(state_file, schema_dict)

        assert result["valid"] is False
        assert "errors" in result

    def test_cli_auto_fix_writes_state_file(
        self, valid_task_1: dict, tmp_path: Path
    ) -> None:
        """Expose normalized skills through the state-file CLI mode."""
        valid_task_1["skills"] = ["python", "python", "testing", "linting"]
        state_file = tmp_path / "state.json"
        state_file.write_text(
            json.dumps({"summary": "Test state", "tasks": [valid_task_1]})
        )

        result = CliRunner().invoke(
            main,
            [
                "--state-file",
                str(state_file),
                "--schema",
                str(SCHEMA_PATH),
                "--auto-fix",
            ],
        )

        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == {"valid": True, "fixed": True}

    def test_auto_fix_state_returns_migration_diagnostics(
        self, valid_task_1: dict, schema_dict: dict, tmp_path: Path
    ) -> None:
        for key in (
            "taskId",
            "verificationCoverage",
            "antiPatternSignals",
            "purposeOutputAlignment",
        ):
            valid_task_1.pop(key)
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": [valid_task_1]}))
        result = auto_fix_task_structure(state_file, schema_dict)
        assert result["valid"] is True
        assert result["fixed"] is False
        assert result["diagnostics"]

    def test_auto_fix_state_rejects_non_array_tasks(
        self, schema_dict: dict, tmp_path: Path
    ) -> None:
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": "not-an-array"}))
        with pytest.raises(ValueError, match="tasks.*array"):
            auto_fix_task_structure(state_file, schema_dict)

    def test_auto_fix_state_rejects_non_object_task(
        self, schema_dict: dict, tmp_path: Path
    ) -> None:
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": ["not-an-object"]}))
        with pytest.raises(ValueError, match="JSON objects"):
            auto_fix_task_structure(state_file, schema_dict)

    def test_auto_fix_state_stops_after_three_changed_invalid_passes(
        self, valid_task_1: dict, schema_dict: dict, tmp_path: Path
    ) -> None:
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": [valid_task_1]}))
        with (
            unittest.mock.patch(
                "lib.validate_task_structure.core.auto_fix", return_value=True
            ),
            unittest.mock.patch(
                "lib.validate_task_structure.core.validate",
                return_value=(False, ["still invalid"]),
            ),
        ):
            result = auto_fix_task_structure(state_file, schema_dict)
        assert result == {"valid": False, "errors": ["still invalid"]}


class TestAtomicityDiagnostics:
    """Regression fixtures for staged atomicity publication behavior."""

    @pytest.mark.parametrize(
        "signal,purpose",
        [
            ("implementation-plus-tests", "Implement checkout and run tests"),
            ("multiple-helpers", "Write three independent helpers"),
            ("analysis-plus-planning", "Analyze checkout and propose a plan"),
            ("multiple-comparisons", "Compare framework A and framework B"),
        ],
    )
    def test_compound_patterns_enter_split_review(
        self, valid_task_1, schema_dict, signal, purpose
    ) -> None:
        """Emit a named warning for every declared compound-task signal."""
        task = dict(valid_task_1)
        task["purpose"] = purpose
        task["antiPatternSignals"] = [signal]
        task["purposeOutputAlignment"] = {
            "status": "needs-review",
            "evidence": "The named compound signal requires a split decision.",
        }
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert any(
            item.startswith(f"WARNING [anti-pattern-{signal}]") for item in diagnostics
        )

    def test_missing_verification_is_a_migration_warning(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task.pop("verificationCoverage")
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert any("WARNING [verification-coverage]" in item for item in diagnostics)

    def test_ambiguous_output_is_actionable_warning(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["expectedOutput"] = "Updated source, test results"
        task["antiPatternSignals"] = []
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert any("WARNING [compound-task-signal]" in item for item in diagnostics)

    def test_compound_purpose_is_actionable_warning(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["purpose"] = "Implement checkout and add its tests"
        task["antiPatternSignals"] = []
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert any("WARNING [compound-task-signal]" in item for item in diagnostics)

    def test_invalid_dependency_reference_is_hard_error(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["dependencies"] = [{"taskId": "missing-task", "reason": "prior output"}]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any("ERROR [dependency-reference]" in item for item in diagnostics)

    def test_dependency_cycle_is_hard_error(
        self, valid_task_1, valid_task_2, schema_dict
    ) -> None:
        first = dict(valid_task_1)
        second = dict(valid_task_2)
        first["dependencies"] = [{"taskId": "task-two"}]
        second["dependencies"] = [{"taskId": "task-one"}]
        valid, diagnostics = validate([first, second], schema_dict)
        assert valid is False
        assert any("ERROR [dependency-cycle]" in item for item in diagnostics)

    def test_tightly_coupled_multi_file_result_is_accepted(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["filesToWrite"] = ["docs/contract.md", "docs/reference.md"]
        task["couplingRationale"] = {
            "group": "publication-contract",
            "rationale": "Both files publish one inseparable contract.",
            "sharedResult": "One reviewed contract package.",
            "verification": "One documentation review covers both files.",
        }
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert not any("coupling-rationale" in item for item in diagnostics)

    def test_unrelated_multi_file_result_requires_split_review(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["filesToWrite"] = ["src/feature.py", "docs/unrelated.md"]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert any("WARNING [coupling-rationale]" in item for item in diagnostics)

    def test_legacy_identity_and_metadata_emit_migration_warnings(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        keys = (
            "taskId",
            "verificationCoverage",
            "purposeOutputAlignment",
            "antiPatternSignals",
        )
        for key in keys:
            task.pop(key)
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        for criterion in (
            "identity",
            "verification-coverage",
            "purpose-output-alignment",
            "anti-pattern-signals",
        ):
            assert any(f"WARNING [{criterion}]" in item for item in diagnostics)

    def test_legacy_verification_supplies_observable_coverage(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task.pop("verificationCoverage")
        task["verification"] = ["Output exists"]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is True
        assert not any("verification-coverage" in item for item in diagnostics)

    def test_conflicting_id_is_rejected_as_additional_property(
        self, valid_task_1, schema_dict
    ) -> None:
        """Reject the unsupported ``id`` alias as an additional property."""
        task = dict(valid_task_1)
        task["id"] = "some-legacy-id"
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any(
            "Additional properties" in item or "id" in item for item in diagnostics
        )

    def test_empty_verification_coverage_is_hard_error(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["verificationCoverage"] = {"observable": []}
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any("ERROR [verification-coverage]" in item for item in diagnostics)

    def test_not_aligned_is_hard_error(self, valid_task_1, schema_dict) -> None:
        task = dict(valid_task_1)
        task["purposeOutputAlignment"] = {
            "status": "not-aligned",
            "evidence": "The output does not match the purpose.",
        }
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any("ERROR [purpose-output-alignment]" in item for item in diagnostics)

    def test_non_array_signals_are_hard_error(self, valid_task_1, schema_dict) -> None:
        task = dict(valid_task_1)
        task["antiPatternSignals"] = "implementation-plus-tests"
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any("ERROR [anti-pattern-signals]" in item for item in diagnostics)

    def test_unknown_signal_is_schema_error(self, valid_task_1, schema_dict) -> None:
        task = dict(valid_task_1)
        task["antiPatternSignals"] = ["unknown-signal"]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert diagnostics

    def test_none_cannot_be_combined_with_named_signal(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["antiPatternSignals"] = ["none", "multiple-helpers"]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any("cannot combine 'none'" in item for item in diagnostics)

    def test_non_object_dependency_is_schema_error(
        self, valid_task_1, schema_dict
    ) -> None:
        task = dict(valid_task_1)
        task["dependencies"] = ["task-one"]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert diagnostics

    def test_self_dependency_is_hard_error(self, valid_task_1, schema_dict) -> None:
        task = dict(valid_task_1)
        task["dependencies"] = [{"taskId": "task-one"}]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert any("self-reference creates a cycle" in item for item in diagnostics)

    def test_non_string_write_is_schema_error(self, valid_task_1, schema_dict) -> None:
        task = dict(valid_task_1)
        task["filesToWrite"] = [1]
        valid, diagnostics = validate([task], schema_dict)
        assert valid is False
        assert diagnostics

    def test_write_conflict_is_hard_error(
        self, valid_task_1, valid_task_2, schema_dict
    ) -> None:
        first = dict(valid_task_1)
        second = dict(valid_task_2)
        second["filesToWrite"] = first["filesToWrite"]
        valid, diagnostics = validate([first, second], schema_dict)
        assert valid is False
        assert any("ERROR [write-target-conflict]" in item for item in diagnostics)

    def test_serialized_shared_write_is_accepted(
        self, valid_task_1, valid_task_2, schema_dict
    ) -> None:
        first = dict(valid_task_1)
        second = dict(valid_task_2)
        second["filesToWrite"] = first["filesToWrite"]
        second["dependencies"] = [{"taskId": "task-one"}]
        valid, diagnostics = validate([first, second], schema_dict)
        assert valid is True
        assert not any("write-target-conflict" in item for item in diagnostics)

    def test_duplicate_task_identity_is_hard_error(
        self, valid_task_1, valid_task_2, schema_dict
    ) -> None:
        first = dict(valid_task_1)
        second = dict(valid_task_2)
        second["taskId"] = first["taskId"]
        valid, diagnostics = validate([first, second], schema_dict)
        assert valid is False
        assert any("is duplicated" in item for item in diagnostics)

    def test_shared_coupling_group_allows_shared_write(
        self, valid_task_1, valid_task_2, schema_dict
    ) -> None:
        first = dict(valid_task_1)
        second = dict(valid_task_2)
        second["filesToWrite"] = first["filesToWrite"]
        rationale = {
            "group": "shared-publication",
            "rationale": "Both tasks contribute to one serialized publication.",
            "sharedResult": "One shared publication.",
            "verification": "One publication check.",
        }
        first["couplingRationale"] = rationale
        second["couplingRationale"] = rationale
        valid, diagnostics = validate([first, second], schema_dict)
        assert valid is True
        assert not any("write-target-conflict" in item for item in diagnostics)


# ===========================================================================
# CLI integration tests
# ===========================================================================


class TestCliValid:
    """Tests for valid CLI invocations."""

    def test_valid_file_path(self, valid_tasks, tmp_path: Path) -> None:
        """A valid task file passed as path argument succeeds."""
        input_file = tmp_path / "tasks.json"
        input_file.write_text(json.dumps(valid_tasks))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["valid"] is True

    def test_valid_stdin(self, valid_tasks) -> None:
        """A valid task list piped via --stdin succeeds."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--stdin", "--schema", str(SCHEMA_PATH)],
            input=json.dumps(valid_tasks),
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["valid"] is True

    def test_valid_single_task(self, valid_task_1, tmp_path: Path) -> None:
        """A single valid task succeeds."""
        input_file = tmp_path / "single.json"
        input_file.write_text(json.dumps([valid_task_1]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["valid"] is True

    def test_migration_warnings_are_returned(
        self, valid_task_1, tmp_path: Path
    ) -> None:
        task = dict(valid_task_1)
        for key in (
            "taskId",
            "verificationCoverage",
            "antiPatternSignals",
            "purposeOutputAlignment",
        ):
            task.pop(key)
        input_file = tmp_path / "migration.json"
        input_file.write_text(json.dumps([task]))
        result = CliRunner().invoke(
            main, [str(input_file), "--schema", str(SCHEMA_PATH)]
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["valid"] is True
        assert data["diagnostics"]

    def test_empty_files_to_read_passes(self, valid_task_1, tmp_path: Path) -> None:
        """Empty filesToRead is allowed and passes validation."""
        task = dict(valid_task_1)
        task["filesToRead"] = []
        input_file = tmp_path / "empty_read.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["valid"] is True


class TestCliInvalid:
    """Tests for invalid task data — exit code 1."""

    def test_missing_required_key_returns_invalid(
        self, valid_task_1, tmp_path: Path
    ) -> None:
        """A task missing a required key produces validation errors."""
        task = dict(valid_task_1)
        task.pop("purpose")
        input_file = tmp_path / "bad.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_maxlength_violation_returns_invalid(
        self, valid_task_1, tmp_path: Path
    ) -> None:
        """A task with purpose over 200 chars produces validation errors."""
        task = dict(valid_task_1)
        task["purpose"] = "x" * 201
        input_file = tmp_path / "bad.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["valid"] is False

    def test_bad_step_numbering_returns_invalid(
        self, valid_task_1, tmp_path: Path
    ) -> None:
        """Non-sequential steps produce validation errors."""
        task = dict(valid_task_1)
        task["executionInstructions"] = [
            {"step": 1, "action": "a"},
            {"step": 3, "action": "c"},
        ]
        input_file = tmp_path / "bad.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["valid"] is False
        assert any("expected step 2" in e for e in data["errors"])

    def test_string_instead_of_array_returns_invalid(
        self, valid_task_1, tmp_path: Path
    ) -> None:
        """filesToRead as string instead of array produces errors."""
        task = dict(valid_task_1)
        task["filesToRead"] = "not-an-array"
        input_file = tmp_path / "bad.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["valid"] is False

    def test_cli_rejects_unknown_dependency(self, valid_task_1, tmp_path: Path) -> None:
        """An unresolved dependency produces a hard validation error."""
        task = dict(valid_task_1)
        task["dependencies"] = [{"taskId": "missing-task"}]
        input_file = tmp_path / "bad.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["valid"] is False
        assert any("dependency-reference" in error for error in data["errors"]), (
            f"errors={data['errors']}"
        )


class TestCliErrors:
    """Tests for parse/file/schema errors — exit code 2."""

    def test_both_file_and_stdin(self, tmp_path: Path) -> None:
        """Specifying both a file path and --stdin raises an error."""
        input_file = tmp_path / "tasks.json"
        input_file.write_text("[]")
        runner = CliRunner()
        result = runner.invoke(
            main,
            [str(input_file), "--stdin", "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "not both" in result.output

    def test_neither_file_nor_stdin(self) -> None:
        """Specifying neither a file path nor --stdin raises an error."""
        runner = CliRunner()
        result = runner.invoke(main, ["--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "provide a file path, --stdin, or --state-file" in result.output

    def test_nonexistent_schema_path(self, tmp_path: Path) -> None:
        """A nonexistent --schema path raises an error."""
        input_file = tmp_path / "tasks.json"
        input_file.write_text("[{}]")
        runner = CliRunner()
        result = runner.invoke(
            main, [str(input_file), "--schema", "/nonexistent/schema.json"]
        )
        assert result.exit_code == 2
        assert "does not exist" in result.output

    def test_non_json_input(self, tmp_path: Path) -> None:
        """Non-JSON file input raises an error."""
        input_file = tmp_path / "bad.txt"
        input_file.write_text("this is not json")
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "invalid JSON" in result.output

    def test_non_json_stdin(self) -> None:
        """Non-JSON stdin input raises an error."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--stdin", "--schema", str(SCHEMA_PATH)],
            input="this is not json",
        )
        assert result.exit_code == 2
        assert "invalid JSON" in result.output

    def test_input_is_object_not_array(self, tmp_path: Path) -> None:
        """JSON object (not array) input raises an error."""
        input_file = tmp_path / "obj.json"
        input_file.write_text('{"summary": "foo", "tasks": []}')
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "must be a JSON array" in result.output

    def test_nonexistent_input_file(self) -> None:
        """A nonexistent input file path raises a Click error (exit 2)."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["/nonexistent/input.json", "--schema", str(SCHEMA_PATH)]
        )
        assert result.exit_code == 2
        assert "does not exist" in result.output

    def test_missing_schema_flag(self, tmp_path: Path) -> None:
        """Missing --schema flag raises a Click usage error."""
        input_file = tmp_path / "tasks.json"
        input_file.write_text("[]")
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file)])
        assert result.exit_code == 2
        assert "Missing option" in result.output or "--schema" in result.output

    def test_invalid_schema_json(self, tmp_path: Path) -> None:
        """A schema file that exists but contains invalid JSON raises an error."""
        input_file = tmp_path / "tasks.json"
        input_file.write_text("[]")
        bad_schema = tmp_path / "bad_schema.json"
        bad_schema.write_text("not valid json")
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(bad_schema)])
        assert result.exit_code == 2
        assert "failed to load schema" in result.output

    def test_invalid_utf8_input_file(self, tmp_path: Path) -> None:
        """A binary file with invalid UTF-8 raises a read error."""
        input_file = tmp_path / "binary.dat"
        input_file.write_bytes(b"\xff\xfe\x00\x01")
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "failed to read input" in result.output

    def test_stdin_read_error(self, monkeypatch) -> None:
        """When stdin read raises an exception, it is handled."""

        def failing_read(*_args: object, **_kwargs: object) -> object:
            raise OSError("stdin error")

        monkeypatch.setattr(
            "cli.validate_task_structure.click.get_text_stream",
            failing_read,
        )
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--stdin", "--schema", str(SCHEMA_PATH)],
            input="[]",
        )
        assert result.exit_code == 2
        assert "failed to read input" in result.output

    def test_validation_logic_exception(self, tmp_path: Path) -> None:
        """When the validate() function raises an unexpected exception, it is caught."""
        input_file = tmp_path / "tasks.json"
        input_file.write_text("[]")
        runner = CliRunner()
        with unittest.mock.patch(
            "cli.validate_task_structure.validate",
            side_effect=RuntimeError("validation crash"),
        ):
            result = runner.invoke(
                main, [str(input_file), "--schema", str(SCHEMA_PATH)]
            )
            assert result.exit_code == 2
            assert "validation error" in result.output

    def test_state_file_with_stdin_mutually_exclusive(self, tmp_path: Path) -> None:
        """``--state-file`` combined with ``--stdin`` exits with code 2."""
        runner = CliRunner()
        state_file = tmp_path / "state.json"
        state_file.write_text("{}")
        result = runner.invoke(
            main,
            ["--state-file", str(state_file), "--stdin", "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output

    def test_state_file_tasks_not_an_array(self, tmp_path: Path) -> None:
        """State file with ``tasks`` that is not an array exits with code 2."""
        runner = CliRunner()
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": "not an array"}))
        result = runner.invoke(
            main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "must be a JSON array" in result.output

    def test_state_file_missing_tasks(self, tmp_path: Path) -> None:
        runner = CliRunner()
        state_file = tmp_path / "state.json"
        state_file.write_text("{}")
        result = runner.invoke(
            main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "must contain a JSON object" in result.output

    def test_auto_fix_requires_state_file(self, tmp_path: Path) -> None:
        input_file = tmp_path / "tasks.json"
        input_file.write_text("[]")
        result = CliRunner().invoke(
            main,
            [str(input_file), "--auto-fix", "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "requires --state-file" in result.output

    def test_auto_fix_failure_is_reported(self, tmp_path: Path) -> None:
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": []}))
        with unittest.mock.patch(
            "cli.validate_task_structure.auto_fix_task_structure",
            side_effect=RuntimeError("fix crash"),
        ):
            result = CliRunner().invoke(
                main,
                [
                    "--state-file",
                    str(state_file),
                    "--auto-fix",
                    "--schema",
                    str(SCHEMA_PATH),
                ],
            )
        assert result.exit_code == 2
        assert "auto-fix failed" in result.output

    def test_auto_fix_invalid_result_exits_one(self, tmp_path: Path) -> None:
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"tasks": []}))
        with unittest.mock.patch(
            "cli.validate_task_structure.auto_fix_task_structure",
            return_value={"valid": False, "errors": ["invalid"]},
        ):
            result = CliRunner().invoke(
                main,
                [
                    "--state-file",
                    str(state_file),
                    "--auto-fix",
                    "--schema",
                    str(SCHEMA_PATH),
                ],
            )
        assert result.exit_code == 1
        assert json.loads(result.output)["valid"] is False


class TestCliHelp:
    """Tests for the --help flag."""

    def test_help_text(self) -> None:
        """--help displays usage information."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "validate-task-structure" in result.output
        assert "--schema" in result.output
        assert "--stdin" in result.output
