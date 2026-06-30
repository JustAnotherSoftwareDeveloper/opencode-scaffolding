"""test_validate_and_format_output.py — Tests for validate-and-format-output.

Covers both the library (validate_and_format) and the Click CLI (main).
Validates that tasks with a ``dependencies`` field are rejected — the
schema no longer includes ``dependencies`` as a recognised property.
Follows the conventions established in test_collect_skills_cli.py.

Run from ``scripts/python/``:

    uv run pytest tests/test_validate_and_format_output.py -v --cov
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import jsonschema
import pytest
from click.testing import CliRunner

from cli.validate_and_format_output import main
from lib.schema import load_schema
from lib.validate_and_format_output import validate_and_format

# ============================================================================
# Constants
# ============================================================================

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)

_VALID_TASKS = [
    {
        "purpose": "Task one purpose.",
        "context": "Context for task one.",
        "filesToRead": [],
        "filesToWrite": [],
        "skills": [],
        "executionInstructions": [{"step": 1, "action": "Do the first thing."}],
        "verification": [],
        "expectedOutput": "Output for task one.",
    },
    {
        "purpose": "Task two purpose.",
        "context": "Context for task two.",
        "filesToRead": [],
        "filesToWrite": [],
        "skills": [],
        "executionInstructions": [{"step": 1, "action": "Do the second thing."}],
        "verification": [],
        "expectedOutput": "Output for task two.",
    },
    {
        "purpose": "Task three purpose.",
        "context": "Context for task three.",
        "filesToRead": [],
        "filesToWrite": [],
        "skills": [],
        "executionInstructions": [{"step": 1, "action": "Do the third thing."}],
        "verification": [],
        "expectedOutput": "Output for task three.",
    },
]

_VALID_DATA = {
    "summary": "Test summary of the overall user request.",
    "tasks": _VALID_TASKS,
}


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def schema_dict() -> dict:
    """Load the canonical task-packet schema as a dict."""
    return load_schema(_SCHEMA_PATH)


@pytest.fixture
def valid_data() -> dict:
    """Return a deep copy of the valid BreakdownTasksOutput fixture."""
    return json.loads(json.dumps(_VALID_DATA))


# ============================================================================
# Library Tests — validate_and_format()
# ============================================================================


class TestValidateAndFormat:
    """Tests for the ``validate_and_format()`` library function."""

    # --- valid cases --------------------------------------------------------

    def test_valid_full_output(self, valid_data: dict, schema_dict: dict) -> None:
        """A full valid output returns (True, formatted-JSON)."""
        valid, result = validate_and_format(valid_data, schema_dict)
        assert valid is True
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["summary"] == valid_data["summary"]
        assert len(parsed["tasks"]) == 3

    # --- missing required fields --------------------------------------------

    def test_missing_summary(self, valid_data: dict, schema_dict: dict) -> None:
        """Missing ``summary`` field triggers a validation error."""
        data = {k: v for k, v in valid_data.items() if k != "summary"}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    def test_missing_tasks(self, valid_data: dict, schema_dict: dict) -> None:
        """Missing ``tasks`` field triggers a validation error."""
        data = {k: v for k, v in valid_data.items() if k != "tasks"}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    # --- extra keys ---------------------------------------------------------

    def test_extra_keys_at_root(self, valid_data: dict, schema_dict: dict) -> None:
        """Extra keys at root are rejected (additionalProperties: false)."""
        data = {**valid_data, "unknownKey": "should fail"}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        error_text = " ".join(str(e) for e in errors)
        assert "unknownKey" in error_text or "Additional properties" in error_text

    # --- maxLength violations -----------------------------------------------

    def test_maxlength_summary(self, valid_data: dict, schema_dict: dict) -> None:
        """Summary exceeding maxLength 2000 is rejected."""
        data = {**valid_data, "summary": "x" * 2001}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    def test_maxlength_purpose(self, valid_data: dict, schema_dict: dict) -> None:
        """Purpose exceeding maxLength 200 is rejected."""
        task = dict(valid_data["tasks"][0], purpose="x" * 201)
        data = {**valid_data, "tasks": [task]}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    def test_maxlength_context(self, valid_data: dict, schema_dict: dict) -> None:
        """Context exceeding maxLength 8000 is rejected."""
        task = dict(valid_data["tasks"][0], context="x" * 8001)
        data = {**valid_data, "tasks": [task]}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    def test_maxlength_expected_output(
        self, valid_data: dict, schema_dict: dict
    ) -> None:
        """ExpectedOutput exceeding maxLength 2000 is rejected."""
        task = dict(valid_data["tasks"][0], expectedOutput="x" * 2001)
        data = {**valid_data, "tasks": [task]}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    # --- tasks with dependencies field (removed from schema) -----------------

    def test_rejects_tasks_with_dependencies_field(
        self,
        valid_data: dict,
        schema_dict: dict,
    ) -> None:
        """A task with ``dependencies`` is rejected (no longer in schema)."""
        task = dict(valid_data["tasks"][0], dependencies=[])
        data = {**valid_data, "tasks": [task]}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        error_text = " ".join(str(e) for e in errors)
        assert "dependencies" in error_text
        assert "additional properties" in error_text.lower() or "not a valid" in error_text.lower()

    # --- empty tasks array --------------------------------------------------

    def test_empty_tasks_array(self, valid_data: dict, schema_dict: dict) -> None:
        """An empty tasks array (minItems: 1) is rejected."""
        data = {**valid_data, "tasks": []}
        valid, errors = validate_and_format(data, schema_dict)
        assert valid is False
        assert len(errors) > 0

    # --- schema-level error (SchemaError, not ValidationError) -------------

    def test_invalid_schema_causes_schema_error(self, valid_data: dict) -> None:
        """Passing a schema with a bad ``type`` value raises SchemaError
        (not caught by the library's ValidationError handler)."""
        bad_schema: dict = {"type": "BOGUS"}
        with pytest.raises(jsonschema.SchemaError):
            validate_and_format(valid_data, bad_schema)


# ============================================================================
# CLI Tests — Click main() via CliRunner
# ============================================================================


class TestCli:
    """Tests for the Click CLI command via CliRunner."""

    # --- valid invocations --------------------------------------------------

    def test_valid_file(self, valid_data: dict, tmp_path: Path) -> None:
        """Valid JSON file produces exit code 0 and raw JSON on stdout."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 0
        # Raw JSON: no markdown fences, no preamble
        assert not result.output.startswith("```")
        assert not result.output.startswith("Here")
        parsed = json.loads(result.output.strip())
        assert parsed["summary"] == valid_data["summary"]
        assert len(parsed["tasks"]) == 3

    def test_valid_stdin(self, valid_data: dict) -> None:
        """``--stdin`` with valid JSON produces exit code 0 and raw JSON."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--stdin", "--schema", str(_SCHEMA_PATH)],
            input=json.dumps(valid_data),
        )
        assert result.exit_code == 0
        assert not result.output.startswith("```")
        assert not result.output.startswith("Here")
        parsed = json.loads(result.output.strip())
        assert parsed["summary"] == valid_data["summary"]

    # --- non-JSON input -----------------------------------------------------

    def test_non_json_input(self, tmp_path: Path) -> None:
        """Non-JSON input produces exit code 2 and an error message."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text("this is not valid json")
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "invalid JSON" in result.output.lower() or "Error" in result.output

    def test_binary_input_file(self, tmp_path: Path) -> None:
        """A file with invalid UTF-8 bytes is caught by the read handler."""
        runner = CliRunner()
        input_file = tmp_path / "binary_input.bin"
        # Write raw bytes that cannot be decoded as UTF-8
        input_file.write_bytes(b"\xff\xfe\x00\x01")
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "Error" in result.output

    # --- non-dict JSON (e.g. JSON array at top level) -----------------------

    def test_json_array_input(self, tmp_path: Path) -> None:
        """A JSON array (not a dict) produces exit code 2."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text("[1, 2, 3]")
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 2
        assert (
            "object" in result.output.lower() or "BreakdownTasksOutput" in result.output
        )

    # --- missing required fields via CLI ------------------------------------

    def test_cli_missing_summary(self, valid_data: dict, tmp_path: Path) -> None:
        """Input missing ``summary`` exits with code 1 and validation error."""
        runner = CliRunner()
        data = {k: v for k, v in valid_data.items() if k != "summary"}
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 1
        assert "valid" in result.output.lower()

    def test_cli_missing_tasks(self, valid_data: dict, tmp_path: Path) -> None:
        """Input missing ``tasks`` exits with code 1 and validation error."""
        runner = CliRunner()
        data = {k: v for k, v in valid_data.items() if k != "tasks"}
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 1
        assert "valid" in result.output.lower()

    # --- extra keys via CLI -------------------------------------------------

    def test_cli_extra_keys(self, valid_data: dict, tmp_path: Path) -> None:
        """Extra keys at root level exit with code 1."""
        runner = CliRunner()
        data = {**valid_data, "bogusField": "will be rejected"}
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 1

    def test_cli_rejects_dependencies_field(
        self, valid_data: dict, tmp_path: Path
    ) -> None:
        """A task with ``dependencies`` exits with code 1."""
        runner = CliRunner()
        task = dict(valid_data["tasks"][0], dependencies=[])
        data = {**valid_data, "tasks": [task]}
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 1

    # --- schema path errors -------------------------------------------------

    def test_invalid_schema_path(self, valid_data: dict, tmp_path: Path) -> None:
        """An invalid ``--schema`` path exits with code 2."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        bad_schema = tmp_path / "nonexistent_schema.json"
        result = runner.invoke(main, [str(input_file), "--schema", str(bad_schema)])
        assert result.exit_code == 2
        assert "Error" in result.output or "does not exist" in result.output

    def test_missing_schema_option(self, valid_data: dict, tmp_path: Path) -> None:
        """Omitting ``--schema`` triggers a usage error (exit code != 0)."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        result = runner.invoke(main, [str(input_file)])
        assert result.exit_code != 0
        assert "schema" in result.output.lower() or "Error" in result.output

    # --- schema file with valid path but invalid JSON content ---------------

    def test_invalid_json_schema_file(self, valid_data: dict, tmp_path: Path) -> None:
        """A schema file that exists but contains invalid JSON exits with code 2."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        bad_schema = tmp_path / "bad_schema.json"
        bad_schema.write_text("this is not valid @@json")
        result = runner.invoke(main, [str(input_file), "--schema", str(bad_schema)])
        assert result.exit_code == 2
        assert "Error" in result.output

    # --- validation exception handler (SchemaError from bad schema) ---------

    def test_validation_exception_from_bad_schema(
        self,
        valid_data: dict,
        tmp_path: Path,
    ) -> None:
        """A schema with a malformed ``type`` value raises SchemaError
        → caught by CLI's ``except Exception`` handler → exit code 2."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        bad_schema = tmp_path / "bad_schema.json"
        # This schema is valid JSON but has an illegal type value => SchemaError
        bad_schema.write_text(json.dumps({"type": "BOGUS"}))
        result = runner.invoke(main, [str(input_file), "--schema", str(bad_schema)])
        assert result.exit_code == 2
        assert "Error" in result.output

    # --- argument conflicts -------------------------------------------------

    def test_both_file_and_stdin(self, tmp_path: Path) -> None:
        """Specifying both a file path and ``--stdin`` exits with code 2."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text("{}")
        result = runner.invoke(
            main,
            [str(input_file), "--stdin", "--schema", str(_SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "not both" in result.output.lower()

    def test_neither_file_nor_stdin(self) -> None:
        """Omitting both file path and ``--stdin`` exits with code 2."""
        runner = CliRunner()
        result = runner.invoke(main, ["--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 2
        assert "provide a file path" in result.output.lower()

    def test_state_file_with_stdin_mutually_exclusive(self, tmp_path: Path) -> None:
        """``--state-file`` combined with ``--stdin`` exits with code 2."""
        runner = CliRunner()
        state_file = tmp_path / "state.json"
        state_file.write_text("{}")
        result = runner.invoke(
            main,
            ["--state-file", str(state_file), "--stdin", "--schema", str(_SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_atomic_write_cleanup_on_error(self, valid_data: dict, tmp_path: Path, monkeypatch) -> None:
        """When ``os.replace`` fails in atomic write, the temp file is cleaned up."""
        runner = CliRunner()
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps(valid_data))

        def failing_call(*args: object, **kwargs: object) -> None:
            raise OSError("simulated failure")

        monkeypatch.setattr("cli.validate_and_format_output.os.replace", failing_call)
        monkeypatch.setattr("cli.validate_and_format_output.os.unlink", failing_call)
        result = runner.invoke(
            main,
            ["--state-file", str(state_file), "--schema", str(_SCHEMA_PATH)],
        )
        assert result.exit_code != 0

    # --- raw JSON verification ----------------------------------------------

    def test_output_raw_json_no_fences(self, valid_data: dict, tmp_path: Path) -> None:
        """Valid output is raw JSON — no markdown fences or preamble."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 0
        output = result.output
        # No markdown fences
        assert "```" not in output
        assert "```json" not in output
        # No preamble text
        assert not output.startswith("Here")
        assert not output.startswith("The")
        assert not output.startswith("Result")
        # Output is parseable standalone JSON
        parsed = json.loads(output.strip())
        assert isinstance(parsed, dict)

    def test_output_trailing_newline(self, valid_data: dict, tmp_path: Path) -> None:
        """Valid output ends with a trailing newline (from click.echo)."""
        runner = CliRunner()
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(valid_data))
        result = runner.invoke(main, [str(input_file), "--schema", str(_SCHEMA_PATH)])
        assert result.exit_code == 0
        raw = result.stdout_bytes if result.stdout_bytes else result.output.encode()
        # The last byte should be '\n' (click.echo adds trailing newline)
        assert raw[-1:] == b"\n"
