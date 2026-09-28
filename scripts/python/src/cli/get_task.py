"""Return one unchanged task object from a canonical tasks.json file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click


def select_task(packet: Any, task_id: str | None, index: int | None) -> dict[str, Any]:
    """Select exactly one task by its stable ID or zero-based array index."""
    if (task_id is None) == (index is None):
        raise ValueError("specify exactly one of --id or --index")
    if not isinstance(packet, dict) or not isinstance(packet.get("tasks"), list):
        raise ValueError("input must be a canonical task-packet object with tasks")

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
            raise ValueError(f"expected exactly one task with taskId {task_id!r}")
        selected = matches[0]

    if not isinstance(selected, dict):
        raise ValueError("selected task is not a JSON object")
    return selected


@click.command(name="get-task")
@click.argument(
    "task_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--id", "task_id", help="Exact taskId to select.")
@click.option("--index", type=click.IntRange(min=0), help="Zero-based task index.")
def main(task_file: Path, task_id: str | None, index: int | None) -> None:
    """Print one complete task from TASK_FILE as JSON without changing the plan."""
    try:
        packet = json.loads(task_file.read_text(encoding="utf-8"))
        task = select_task(packet, task_id, index)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    click.echo(json.dumps(task, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
