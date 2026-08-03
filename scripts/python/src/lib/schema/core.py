"""Task-packet JSON Schema loading module.

Provides ``load_schema()``, a zero-dependency function that reads a JSON
Schema file and returns it as a ``dict``.

Consumers: :mod:`src.cli.generate_task_json` and
:mod:`src.cli.validate_task_structure`.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any

_TASK_PACKET_SCHEMA_RESOURCE = "assets/task-packet.schema.json"


def load_schema(path: str | Path) -> dict[str, Any]:
    """Load a JSON Schema dict from a file path.

    Args:
        path: Path to a JSON Schema file (``.json``).

    Returns:
        The parsed JSON Schema as a Python ``dict``.

    Raises:
        FileNotFoundError: If *path* does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path_obj = Path(path)

    with path_obj.open("r", encoding="utf-8") as fh:
        schema: dict[str, Any] = json.load(fh)

    return schema


def load_task_packet_schema() -> dict[str, Any]:
    """Load the task-packet schema bundled in the installed package."""
    resource = resources.files("lib.generate_task_json").joinpath(
        _TASK_PACKET_SCHEMA_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    if not isinstance(schema, dict):
        raise ValueError("task-packet schema resource must contain a JSON object")
    return schema
