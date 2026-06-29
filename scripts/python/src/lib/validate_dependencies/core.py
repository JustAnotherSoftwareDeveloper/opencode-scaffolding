"""Dependency graph validation for task IDs, orphans, self-loops, and cycles."""

from __future__ import annotations

from typing import Any


def validate(tasks: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Validate a list of task objects for dependency graph integrity.

    Checks performed:
    - Every dependency UUID references an existing task id (no orphans).
    - No task depends on itself (no self-loops).
    - No circular dependencies (no cycles, DFS-based).

    Args:
        tasks: List of dicts, each with ``id`` (str) and ``dependencies``
            (list[str]).

    Returns:
        ``(True, [])`` if valid, or ``(False, [error messages])`` with
        descriptive messages for each violation found.
    """
    errors: list[str] = []

    # Build a set of all task IDs for O(1) lookup
    task_ids: set[str] = {t["id"] for t in tasks}

    # Build adjacency map: task_id -> list of dependency ids
    adjacency: dict[str, list[str]] = {}
    for task in tasks:
        adjacency[task["id"]] = list(task.get("dependencies", []))

    # 1. Self-loop check
    for task in tasks:
        tid: str = task["id"]
        for dep in adjacency.get(tid, []):
            if dep == tid:
                errors.append(f"Self-loop: task '{tid}' depends on itself")

    # 2. Orphan reference check
    for task in tasks:
        tid = task["id"]
        for dep in adjacency.get(tid, []):
            if dep != tid and dep not in task_ids:
                errors.append(
                    f"Orphan reference: task '{tid}' depends on '{dep}' "
                    f"which does not exist"
                )

    # 3. Cycle check (DFS with color markers)
    # 0 = WHITE (unvisited), 1 = GRAY (in progress), 2 = BLACK (done)
    color: dict[str, int] = {tid: 0 for tid in task_ids}

    def _dfs(node: str) -> None:
        color[node] = 1  # GRAY
        for neighbor in adjacency.get(node, []):
            if neighbor not in color:
                # Orphan reference — already flagged above, skip
                continue
            if color[neighbor] == 1:
                errors.append(
                    f"Cycle detected: dependency cycle involving "
                    f"task '{node}' -> '{neighbor}'"
                )
            elif color[neighbor] == 0:
                _dfs(neighbor)
        color[node] = 2  # BLACK

    for tid in task_ids:
        if color[tid] == 0:
            _dfs(tid)

    if errors:
        return False, errors
    return True, []
