"""test_sequential_schema.py — Schema-level structural invariant tests.

Validates the updated task-packet JSON Schema directly (not via CLI).
Tests cover valid packets, invalid packets with unknown fields, and
schema structural invariants.

Tests load the schema file directly via ``lib.schema.load_schema`` and
use ``jsonschema`` for validation — no script CLI invocation.

Run from ``scripts/python/``:

    uv run pytest tests/test_sequential_schema.py -v
"""

from __future__ import annotations

from pathlib import Path

import jsonschema
import pytest

from lib.schema import load_schema

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

assert SCHEMA_PATH.is_file(), f"Schema not found at {SCHEMA_PATH}"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def schema_dict() -> dict:
    """Load the task-packet schema once per module."""
    return load_schema(SCHEMA_PATH)


@pytest.fixture(scope="module")
def root_validator(schema_dict: dict) -> jsonschema.Draft7Validator:
    """Draft7Validator for the root BreakdownTasksOutput schema."""
    return jsonschema.Draft7Validator(
        schema_dict,
        format_checker=jsonschema.Draft7Validator.FORMAT_CHECKER,
    )


@pytest.fixture(scope="module")
def task_validator(schema_dict: dict) -> jsonschema.Draft7Validator:
    """Draft7Validator for the TaskPacket definition."""
    task_schema = schema_dict["definitions"]["TaskPacket"]
    return jsonschema.Draft7Validator(
        task_schema,
        format_checker=jsonschema.Draft7Validator.FORMAT_CHECKER,
    )


@pytest.fixture
def minimal_task() -> dict:
    """A minimal valid task packet with all required fields, no extras.

    Does NOT include ``dependencies`` or ``verification``.
    """
    return {
        "purpose": "Validate the sequential schema invariants",
        "context": "x" * 2000,
        "filesToRead": ["src/schema.json"],
        "filesToWrite": ["src/output.py"],
        "skills": ["python"],
        "executionInstructions": [
            {"step": 1, "action": "Load the schema"},
            {"step": 2, "action": "Validate invariants"},
        ],
        "expectedOutput": "Validation report",
    }


@pytest.fixture
def full_task() -> dict:
    """A full valid task packet including optional ``verification`` field."""
    return {
        "purpose": "Full task with verification checks",
        "context": "x" * 2000,
        "filesToRead": ["src/main.py", "src/lib.py"],
        "filesToWrite": ["src/output.py", "tests/test_output.py"],
        "skills": ["python", "testing"],
        "executionInstructions": [
            {"step": 1, "action": "Parse input files"},
            {"step": 2, "action": "Generate output"},
            {"step": 3, "action": "Run tests"},
        ],
        "verification": [
            "All tests pass with exit code 0",
            "Output file exists at expected path",
        ],
        "expectedOutput": "Generated source and passing test suite",
    }


# ===========================================================================
# TestValidPacketsWithoutDependencies
# ===========================================================================


class TestValidPacketsWithoutDependencies:
    """Valid task packets."""

    def test_minimal_valid_packet(
        self, task_validator: jsonschema.Draft7Validator, minimal_task: dict
    ) -> None:
        """A minimal task with all required fields passes schema validation."""
        task_validator.validate(minimal_task)

    def test_full_packet_with_verification(
        self, task_validator: jsonschema.Draft7Validator, full_task: dict
    ) -> None:
        """A task with all fields including optional ``verification`` is valid."""
        task_validator.validate(full_task)

    def test_multiple_tasks_in_root(
        self,
        root_validator: jsonschema.Draft7Validator,
        minimal_task: dict,
        full_task: dict,
    ) -> None:
        """Multiple tasks in the root ``tasks`` array pass root schema."""
        packet = {
            "summary": "Break down the sequential schema validation work.",
            "tasks": [minimal_task, full_task],
        }
        root_validator.validate(packet)

    def test_minimal_single_task_in_root(
        self,
        root_validator: jsonschema.Draft7Validator,
        minimal_task: dict,
    ) -> None:
        """A single task in the root ``tasks`` array is valid (minItems: 1)."""
        packet = {
            "summary": "Single task for the sequential schema.",
            "tasks": [minimal_task],
        }
        root_validator.validate(packet)


# ===========================================================================
# TestInvalidPacketsWithDependencies
# ===========================================================================


class TestInvalidPacketsWithDependencies:
    """Packets that should be invalid under the updated schema.

    The updated schema enforces ``additionalProperties: false`` on the
    TaskPacket definition.  Since ``dependencies`` has been removed from
    the schema, a task WITH ``dependencies`` is now schema-invalid.
    """

    def test_extra_unknown_field_rejected(
        self, task_validator: jsonschema.Draft7Validator, minimal_task: dict
    ) -> None:
        """An extra unknown field not in ``properties`` raises ValidationError."""
        task = dict(minimal_task)
        task["unknownField"] = "should be rejected"
        with pytest.raises(jsonschema.ValidationError):
            task_validator.validate(task)

    def test_extra_field_foo_rejected(
        self, task_validator: jsonschema.Draft7Validator, minimal_task: dict
    ) -> None:
        """An arbitrary unknown property (``foo``) is rejected."""
        task = dict(minimal_task)
        task["foo"] = "bar"
        with pytest.raises(jsonschema.ValidationError):
            task_validator.validate(task)

    def test_old_flat_array_format_rejected(
        self, root_validator: jsonschema.Draft7Validator, minimal_task: dict
    ) -> None:
        """A flat array of tasks (old format) is rejected by root schema."""
        with pytest.raises(jsonschema.ValidationError):
            root_validator.validate([minimal_task])

    def test_empty_task_array_rejected(
        self, root_validator: jsonschema.Draft7Validator
    ) -> None:
        """An empty tasks array violates ``minItems: 1``."""
        packet = {"summary": "No tasks.", "tasks": []}
        with pytest.raises(jsonschema.ValidationError):
            root_validator.validate(packet)

    def test_root_without_summary_rejected(
        self, root_validator: jsonschema.Draft7Validator, minimal_task: dict
    ) -> None:
        """Root packet missing required ``summary`` field is rejected."""
        packet = {"tasks": [minimal_task]}
        with pytest.raises(jsonschema.ValidationError):
            root_validator.validate(packet)

    def test_root_without_tasks_rejected(
        self, root_validator: jsonschema.Draft7Validator
    ) -> None:
        """Root packet missing required ``tasks`` field is rejected."""
        packet = {"summary": "No tasks array."}
        with pytest.raises(jsonschema.ValidationError):
            root_validator.validate(packet)

    def test_root_extra_unknown_field_rejected(
        self, root_validator: jsonschema.Draft7Validator, minimal_task: dict
    ) -> None:
        """Root schema with unknown field violates ``additionalProperties: false``."""
        packet = {
            "summary": "Has extra field.",
            "tasks": [minimal_task],
            "extraRootField": True,
        }
        with pytest.raises(jsonschema.ValidationError):
            root_validator.validate(packet)


# ===========================================================================
# TestSchemaStructuralInvariants
# ===========================================================================


class TestSchemaStructuralInvariants:
    """Structural invariants of the task-packet schema itself."""

    def test_root_required_fields(self, schema_dict: dict) -> None:
        """Root schema requires ``summary`` and ``tasks``."""
        assert "required" in schema_dict
        assert schema_dict["required"] == ["summary", "tasks"]

    def test_root_additional_properties_false(self, schema_dict: dict) -> None:
        """Root schema enforces ``additionalProperties: false``."""
        assert schema_dict.get("additionalProperties") is False

    def test_root_has_tasks_array(self, schema_dict: dict) -> None:
        """Root ``tasks`` property is an array with $ref to TaskPacket."""
        tasks_prop = schema_dict["properties"]["tasks"]
        assert tasks_prop["type"] == "array"
        assert "$ref" in tasks_prop["items"]
        assert tasks_prop["items"]["$ref"] == "#/definitions/TaskPacket"
        assert tasks_prop.get("minItems") == 1

    def test_task_packet_required_fields(self, schema_dict: dict) -> None:
        """TaskPacket has the expected set of required fields."""
        expected_required = {
            "purpose",
            "context",
            "filesToRead",
            "filesToWrite",
            "skills",
            "executionInstructions",
            "expectedOutput",
        }
        task_def = schema_dict["definitions"]["TaskPacket"]
        actual_required = set(task_def["required"])
        assert actual_required == expected_required

    def test_task_packet_additional_properties_false(self, schema_dict: dict) -> None:
        """TaskPacket enforces ``additionalProperties: false``."""
        task_def = schema_dict["definitions"]["TaskPacket"]
        assert task_def.get("additionalProperties") is False

    def test_task_packet_has_optional_verification(self, schema_dict: dict) -> None:
        """``verification`` is an optional field in TaskPacket properties."""
        props = schema_dict["definitions"]["TaskPacket"]["properties"]
        assert "verification" in props
        assert props["verification"]["type"] == "array"
        assert props["verification"]["minItems"] == 1
        assert props["verification"]["uniqueItems"] is True

    def test_task_packet_enforces_context_and_instruction_limits(
        self, schema_dict: dict
    ) -> None:
        """TaskPacket requires detailed context and at most five steps."""
        props = schema_dict["definitions"]["TaskPacket"]["properties"]
        assert props["context"]["minLength"] == 2000
        assert props["executionInstructions"]["maxItems"] == 5
        assert props["skills"]["maxItems"] == 3

    def test_dependencies_is_removed_from_properties(
        self, schema_dict: dict
    ) -> None:
        """``dependencies`` has been removed from TaskPacket properties."""
        props = schema_dict["definitions"]["TaskPacket"]["properties"]
        assert "dependencies" not in props

    def test_task_packet_has_summary_at_root_only(self, schema_dict: dict) -> None:
        """``summary`` exists only at root, not in TaskPacket."""
        props = schema_dict["definitions"]["TaskPacket"]["properties"]
        assert "summary" not in props

    def test_task_packet_property_count(self, schema_dict: dict) -> None:
        """TaskPacket has exactly the expected number of properties."""
        props = schema_dict["definitions"]["TaskPacket"]["properties"]
        expected_properties = {
            "purpose",
            "context",
            "filesToRead",
            "filesToWrite",
            "skills",
            "executionInstructions",
            "verification",
            "expectedOutput",
        }
        assert set(props.keys()) == expected_properties

    def test_schema_title(self, schema_dict: dict) -> None:
        """Schema title is 'BreakdownTasksOutput'."""
        assert schema_dict.get("title") == "BreakdownTasksOutput"

    def test_schema_draft_version(self, schema_dict: dict) -> None:
        """Schema uses draft-07."""
        assert "$schema" in schema_dict
        assert "draft-07" in schema_dict["$schema"]

    def test_required_fields_not_in_required_list_if_optional(
        self, schema_dict: dict
    ) -> None:
        """Fields not in 'required' list are indeed optional.

        Checks that ``verification`` is optional.
        """
        task_def = schema_dict["definitions"]["TaskPacket"]
        assert "verification" in task_def["properties"]
        assert "verification" not in task_def["required"]
