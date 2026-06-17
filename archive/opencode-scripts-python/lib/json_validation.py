from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


class JsonValidationError(Exception):
    """Raised when a JSON document or schema fails validation."""


def load_json(path: Path) -> Any:
    """Load JSON from an explicit file path."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise JsonValidationError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise JsonValidationError(f"invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise JsonValidationError(f"could not read {path}: {exc}") from exc


def validate_json_path(json_path: str | Path, schema_path: str | Path | None = None) -> None:
    """Validate JSON syntax and, when supplied, validate against a JSON Schema."""
    data = load_json(Path(json_path))

    if schema_path is None:
        return

    schema_file = Path(schema_path)
    schema = load_json(schema_file)

    try:
        validator = Draft202012Validator(schema)
        validator.check_schema(schema)
        validator.validate(data)
    except SchemaError as exc:
        raise JsonValidationError(f"invalid JSON Schema in {schema_file}: {exc.message}") from exc
    except ValidationError as exc:
        location = "/".join(str(part) for part in exc.absolute_path)
        suffix = f" at {location}" if location else ""
        raise JsonValidationError(f"schema validation failed for {json_path}{suffix}: {exc.message}") from exc
