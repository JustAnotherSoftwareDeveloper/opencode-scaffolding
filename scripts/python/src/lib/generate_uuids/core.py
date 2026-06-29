"""UUID generation library — generate N unique UUID v4 strings.

Usage:
    from lib.generate_uuids import generate

    uuids = generate(5)  # Returns list of 5 UUID v4 strings
"""

from __future__ import annotations

import uuid


def generate(count: int) -> list[str]:
    """Return *count* unique UUID v4 strings.

    Args:
        count: Number of UUIDs to generate (must be 1-100).

    Returns:
        List of UUID v4 strings in insertion order.

    Raises:
        ValueError: If *count* is not in the range 1-100.
    """
    if count < 1 or count > 100:
        msg = f"count must be between 1 and 100, got {count}"
        raise ValueError(msg)

    seen: set[str] = set()
    result: list[str] = []

    while len(result) < count:
        uid = str(uuid.uuid4())
        if uid not in seen:
            seen.add(uid)
            result.append(uid)

    return result
