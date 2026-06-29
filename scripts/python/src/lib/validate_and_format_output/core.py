"""BreakdownTasksOutput validation and formatting.

Validates a full BreakdownTasksOutput object (summary + tasks) against the
task-packet JSON Schema and emits raw JSON output on success.
Consumed by: validate-and-format-output.
"""

from __future__ import annotations

import json
from typing import Any

import jsonschema


def validate_and_format(
    data: dict[str, Any], schema: dict[str, Any]
) -> tuple[bool, str | list[str]]:
    """Validate a BreakdownTasksOutput object against the schema.

    Performs JSON Schema validation (via *jsonschema*) against the full schema:

    * ``summary`` must be a string (max 2000 chars)
    * ``tasks`` must be a non-empty array of valid TaskPacket objects
    * No additional properties at root level

    Args:
        data: The full BreakdownTasksOutput dict to validate.
        schema: The BreakdownTasksOutput JSON Schema dict.

    Returns:
        ``(True, json.dumps(data, indent=2))`` if valid,
        ``(False, [error_messages])`` with descriptive messages otherwise.
    """
    errors: list[str] = []

    try:
        jsonschema.validate(
            data,
            schema,
            cls=jsonschema.Draft7Validator,
            format_checker=jsonschema.draft7_format_checker,
        )
    except jsonschema.ValidationError as exc:
        errors.append(exc.message)

    if errors:
        return False, errors

    return True, json.dumps(data, indent=2)
