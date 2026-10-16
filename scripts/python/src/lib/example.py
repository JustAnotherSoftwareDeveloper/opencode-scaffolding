"""Example library function for the scripts-python project."""

from __future__ import annotations


def example_message(runtime: str) -> str:
    """Return a status message for *runtime* or reject an empty value."""
    if not runtime:
        raise ValueError("runtime is required")

    return f"example runtime={runtime} status=ok"
