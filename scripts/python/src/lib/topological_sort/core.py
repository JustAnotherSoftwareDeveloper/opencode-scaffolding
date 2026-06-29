"""Topological sort of tasks by dependency graph using Kahn's algorithm.

Invoked by: topological-sort
"""

from __future__ import annotations

from typing import Any


def _find_cycle_path(
    remaining: list[str],
    task_map: dict[str, dict[str, Any]],
    in_degree: dict[str, int],
) -> str:
    """Trace a dependency cycle starting from one of *remaining* nodes.

    Follows dependency edges from a node with in_degree > 0 until a cycle
    is detected, then returns a human-readable cycle path string.
    """
    seen: dict[str, int] = {}
    current = remaining[0]
    path: list[str] = []

    while True:
        if current in seen:
            cycle_start_idx = seen[current]
            cycle = path[cycle_start_idx:] + [current]
            return " -> ".join(cycle)
        seen[current] = len(path)
        path.append(current)

        task = task_map.get(current)
        deps = task.get("dependencies", []) if task else []
        # Follow the first dependency that is also stuck (in_degree > 0)
        next_node: str | None = None
        for dep in deps:
            if in_degree.get(dep, 0) > 0:
                next_node = dep
                break
        if next_node is None:
            # No dependency leads to another stuck node — fall back to
            # showing the dead-end path anyway (should not happen if
            # a true cycle exists).
            return " -> ".join(path)  # pragma: no cover
        current = next_node


def sort(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return *tasks* sorted in topological order.

    Parallel tasks (tasks at the same dependency depth) are ordered by
    their ``id`` field lexicographically for deterministic output.

    Parameters
    ----------
    tasks:
        A list of task dicts. Each dict must have an ``"id"`` key
        (str) and may have a ``"dependencies"`` key (list of str).
        Dependencies reference other task ids in the same list.

    Returns
    -------
    list[dict]
        The tasks in topological order.

    Raises
    ------
    ValueError
        If a cycle is detected (message includes the cycle path),
        if a task is missing ``"id"``, if a task has duplicate ``"id"``,
        or if a task references an unknown dependency.
    """
    # ------------------------------------------------------------------
    # Phase 1 — Validate & index
    # ------------------------------------------------------------------
    task_map: dict[str, dict[str, Any]] = {}
    for task in tasks:
        raw_id = task.get("id")
        if not isinstance(raw_id, str):
            raise ValueError(
                f"Task missing or invalid 'id' field (expected str): {task}"
            )
        tid: str = raw_id
        if tid in task_map:
            raise ValueError(f"Duplicate task id: {tid}")
        task_map[tid] = task

    # ------------------------------------------------------------------
    # Phase 2 — Build adjacency and in-degree
    # ------------------------------------------------------------------
    adj: dict[str, list[str]] = {}
    in_degree: dict[str, int] = {}

    for task in tasks:
        tid = task["id"]  # guaranteed str from Phase 1
        deps = task.get("dependencies")
        if deps is not None and not isinstance(deps, list):
            raise ValueError(
                f"Task '{tid}' has invalid 'dependencies' field "
                f"(expected list, got {type(deps).__name__}): {deps}"
            )
        adj[tid] = []
        in_degree[tid] = 0

    for task in tasks:
        tid = task["id"]
        for dep in task.get("dependencies", []):
            if not isinstance(dep, str):
                raise ValueError(f"Task '{tid}' has non-string dependency: {dep}")
            if dep not in task_map:
                raise ValueError(f"Task '{tid}' depends on unknown task '{dep}'")
            adj.setdefault(dep, []).append(tid)
            in_degree[tid] = in_degree.get(tid, 0) + 1

    # Ensure every referenced dependency has an entry
    for tid in list(adj):  # pragma: no branch (all tids already in both maps)
        if tid not in in_degree:  # pragma: no cover
            in_degree[tid] = 0
        if tid not in adj:  # pragma: no cover
            adj[tid] = []

    # ------------------------------------------------------------------
    # Phase 3 — Kahn's algorithm
    # ------------------------------------------------------------------
    ready: list[str] = sorted([tid for tid in in_degree if in_degree[tid] == 0])
    result: list[dict[str, Any]] = []

    while ready:
        tid = ready.pop(0)  # always pick the smallest id (sorted)
        result.append(task_map[tid])
        for dependent in adj.get(tid, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                ready.append(dependent)
        ready.sort()

    # ------------------------------------------------------------------
    # Phase 4 — Cycle detection
    # ------------------------------------------------------------------
    remaining = [tid for tid in in_degree if in_degree[tid] > 0]
    if remaining:
        cycle_path = _find_cycle_path(remaining, task_map, in_degree)
        raise ValueError(f"Cycle detected: {cycle_path}")

    return result
