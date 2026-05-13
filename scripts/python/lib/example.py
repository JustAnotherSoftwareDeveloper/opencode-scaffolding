from __future__ import annotations


def example_message(runtime: str) -> str:
    if not runtime:
        raise ValueError("runtime is required")

    return f"example runtime={runtime} status=ok"
