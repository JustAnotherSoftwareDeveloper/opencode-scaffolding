"""Task-packet JSON Schema loading module.

Provides ``load_schema()``, a zero-dependency function that reads a JSON
Schema file and returns it as a ``dict``.

Consumers: :mod:`src.cli.validate_task_structure` and
:mod:`src.cli.validate_and_format_output`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
