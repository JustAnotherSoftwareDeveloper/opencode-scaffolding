"""JSON/text output formatting helpers.

Consumers: shared by generated script CLIs.

Provides deterministic formatting utilities for script output.
CLI entry points should use ``click.echo`` for actual I/O; these
helpers produce the formatted strings.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def format_json(
    data: object,
    *,
    indent: int = 2,
    sort_keys: bool = False,
    default: Any = str,
) -> str:
    """Serialize *data* as a JSON string.

    Args:
        data: The data to serialize.
        indent: Indentation level (default ``2``).
        sort_keys: Whether to sort dictionary keys (default ``False``).
        default: Default serialization function for non-serializable types.

    Returns:
        A formatted JSON string with trailing newline.
    """
    return json.dumps(data, indent=indent, sort_keys=sort_keys, default=default) + "\n"


def format_text_result(
    data: Mapping[str, object],
    *,
    separator: str = ": ",
) -> str:
    """Format a mapping as human-readable text lines.

    Each key-value pair is rendered as ``{key}{separator}{value}`` on its own
    line with a trailing newline.

    Args:
        data: The mapping to format.
        separator: Separator between key and value (default ``": "``).

    Returns:
        Multi-line formatted text.
    """
    lines = [f"{key}{separator}{value}" for key, value in data.items()]
    return "\n".join(lines) + "\n"


def format_error(message: str) -> str:
    """Format an error message following the project convention.

    Args:
        message: The error description.

    Returns:
        A string with the ``"Error: "`` prefix and trailing newline.
    """
    return f"Error: {message}\n"
