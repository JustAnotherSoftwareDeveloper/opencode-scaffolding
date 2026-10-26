"""JSON-object validation helpers.

Consumers: shared by generated script CLIs and ``lib.render_task_markdown``.

Uses the existing ``jsonschema`` dependency for full JSON Schema validation.
When it is unavailable, JSON Schema validation fails closed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import jsonschema as _jsonschema

# jsonschema is an existing project dependency (see pyproject.toml).
# Defer the import so this module remains importable without jsonschema.
try:
    import jsonschema as _jsonschema

    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


def validate_required_keys(
    data: Mapping[str, object],
    required: list[str],
) -> list[str]:
    """Check that all keys in *required* are present in *data*.

    Args:
        data: The dictionary to check.
        required: List of required key names.

    Returns:
        A list of missing key names (empty if all are present).
    """
    return [key for key in required if key not in data]


def validate_type(
    data: Mapping[str, object],
    schema: Mapping[str, type[object]],
) -> list[str]:
    """Check that fields in *data* match the expected types in *schema*.

    Only checks keys that are present in *data*.  Missing keys are not
    reported as type errors (use :func:`validate_required_keys` for that).

    Args:
        data: The dictionary to check.
        schema: A mapping of field names to expected types, such as
            ``{"count": int}``.

    Returns:
        A list of error messages (empty if all types match).
    """
    errors: list[str] = []
    for key, expected_type in schema.items():
        if key in data and not isinstance(data[key], expected_type):
            actual = type(data[key]).__name__
            errors.append(
                f"Field {key!r}: expected {expected_type.__name__}, "
                f"got {actual}"
            )
    return errors


def validate_json_schema(
    instance: object,
    schema: dict[str, Any],
) -> list[str]:
    """Validate *instance* against a JSON Schema using ``jsonschema``.

    If ``jsonschema`` is not installed, return an error rather than treating
    partial validation as successful.

    Args:
        instance: The data to validate (typically a ``dict``).
        schema: A JSON Schema dict.

    Returns:
        A list of error messages (empty if valid).
    """
    if _HAS_JSONSCHEMA:
        try:
            _jsonschema.validate(instance, schema)
            return []
        except _jsonschema.ValidationError as exc:
            return [exc.message]

    return [
        "jsonschema is unavailable; full JSON Schema validation "
        "cannot be performed"
    ]
