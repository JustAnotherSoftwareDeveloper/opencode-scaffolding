"""test_validate_task_structure.py — Tests for validate-task-structure.

Covers the Click CLI (via CliRunner) and the lib validation module
(direct function calls), achieving 100% coverage of both
``cli.validate_task_structure`` and ``lib.validate_task_structure``.

Also verifies that a task packet containing a ``dependencies`` field
is rejected by schema ``additionalProperties: false``.

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
    }


@pytest.fixture
def valid_task_2() -> dict:
    return {
        "purpose": "Task two purpose",
        "context": VALID_CONTEXT,
        "filesToRead": ["src/file2.py"],
        "filesToWrite": ["src/out2.py"],
        "skills": ["typescript"],
        "executionInstructions": [
            {"step": 1, "action": "Do step one"},
        ],
        "expectedOutput": "Output for task two",
    }


@pytest.fixture
def valid_task_3() -> dict:
    return {
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

    def test_auto_fix_state_file_preserves_unfixable_errors(
        self, valid_task_1: dict, schema_dict: dict, tmp_path: Path
    ) -> None:
        """Report an empty skills array without inventing a fallback skill."""
        valid_task_1["skills"] = []
        state_file = tmp_path / "state.json"
        state_file.write_text(
            json.dumps({"summary": "Test state", "tasks": [valid_task_1]})
        )

        result = auto_fix_task_structure(state_file, schema_dict)

        assert result["valid"] is False
        assert result["errors"]

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


class TestRejectDependencies:
    """Tests that task packets with a ``dependencies`` field are rejected.

    The task-packet schema uses ``additionalProperties: false``, so any
    property not explicitly listed (including ``dependencies``) causes a
    validation error.
    """

    def test_rejects_task_with_dependencies_field(
        self, valid_task_1, schema_dict
    ) -> None:
        """Adding ``dependencies`` to a valid task yields an invalid result."""
        task = dict(valid_task_1)
        task["dependencies"] = []
        valid, errors = validate([task], schema_dict)
        assert valid is False
        assert any("dependencies" in e for e in errors), f"errors={errors}"
        assert any("Additional properties" in e for e in errors), f"errors={errors}"


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

    def test_cli_rejects_dependencies_field(self, valid_task_1, tmp_path: Path) -> None:
        """A task with ``dependencies`` field produces validation errors."""
        task = dict(valid_task_1)
        task["dependencies"] = []
        input_file = tmp_path / "bad.json"
        input_file.write_text(json.dumps([task]))
        runner = CliRunner()
        result = runner.invoke(main, [str(input_file), "--schema", str(SCHEMA_PATH)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["valid"] is False
        assert any("dependencies" in error for error in data["errors"]), (
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
