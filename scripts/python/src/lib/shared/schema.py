"""Lightweight JSON-object validation helpers.

Consumers: shared by generated script CLIs.

Uses the existing ``jsonschema`` dependency when available for full JSON Schema
validation, and provides simple required-key checks that work without it.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import jsonschema as _jsonschema

# jsonschema is an existing project dependency (see pyproject.toml).
# Import is deferred so the module can be imported when jsonschema is unavailable.
try:
    import jsonschema as _jsonschema

    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
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
        schema: A mapping of field name to expected type (e.g. ``{"count": int}``).

    Returns:
        A list of error messages (empty if all types match).
    """
    errors: list[str] = []
    for key, expected_type in schema.items():
        if key in data and not isinstance(data[key], expected_type):
            actual = type(data[key]).__name__
            errors.append(
                f"Field {key!r}: expected {expected_type.__name__}, got {actual}"
            )
    return errors


def validate_json_schema(
    instance: object,
    schema: dict[str, Any],
) -> list[str]:
    """Validate *instance* against a JSON Schema using ``jsonschema``.

    If ``jsonschema`` is not installed, falls back to a simple required-key
    check that expects *schema* to have a ``"required"`` list.

    Args:
        instance: The data to validate (typically a ``dict``).
        schema: A JSON Schema dict (or a dict with at least ``"required"``).

    Returns:
        A list of error messages (empty if valid).
    """
    if _HAS_JSONSCHEMA:
        try:
            _jsonschema.validate(instance, schema)
            return []
        except _jsonschema.ValidationError as exc:
            return [exc.message]

    # Fallback: simple required-key check.
    if not isinstance(instance, dict):
        return ["Instance must be a dict"]

    required: list[str] = schema.get("required", [])
    if not isinstance(required, list):
        return []

    return validate_required_keys(instance, required)
