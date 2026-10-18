"""Select one task from a canonical task packet."""

from __future__ import annotations

from typing import Any


def select_task(
    packet: Any, task_id: str | None, index: int | None
) -> dict[str, Any]:
    """Select exactly one task by stable ID or zero-based array index."""
    if (task_id is None) == (index is None):
        raise ValueError("specify exactly one of --id or --index")
    if not isinstance(packet, dict) or not isinstance(
        packet.get("tasks"), list
    ):
        raise ValueError(
            "input must be a canonical task-packet object with tasks"
        )

    tasks = packet["tasks"]
    if index is not None:
        if index < 0 or index >= len(tasks):
            raise ValueError(f"task index {index} is out of range")
        selected = tasks[index]
    else:
        matches = [
            task
            for task in tasks
            if isinstance(task, dict) and task.get("taskId") == task_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one task with taskId {task_id!r}"
            )
        selected = matches[0]

    if not isinstance(selected, dict):
        raise ValueError("selected task is not a JSON object")
    return selected
