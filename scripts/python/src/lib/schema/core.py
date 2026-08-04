"""Task-packet JSON Schema loading module.

Provides ``load_schema()`` (arbitrary path) and ``load_task_packet_schema()``
(reads the task-packet schema from the repository).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_OPENCODE_CONFIG = Path.home() / ".config" / "opencode"
_SCHEMA_PATH = (
    _OPENCODE_CONFIG
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)


def load_schema(path: str | Path) -> dict[str, Any]:
    """Load a JSON Schema dict from a file path."""
    with Path(path).open("r", encoding="utf-8") as fh:
        schema: dict[str, Any] = json.load(fh)
    return schema


def load_task_packet_schema() -> dict[str, Any]:
    """Load the task-packet schema from the repository."""
    with _SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    if not isinstance(schema, dict):
        raise ValueError("task-packet schema must contain a JSON object")
    return schema
