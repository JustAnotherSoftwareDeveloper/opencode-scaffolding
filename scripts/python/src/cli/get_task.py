"""Return one unchanged task object from a canonical tasks.json file."""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.get_task.core import select_task


@click.command(name="get-task")
@click.argument(
    "task_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--id", "task_id", help="Exact taskId to select.")
@click.option(
    "--index", type=click.IntRange(min=0), help="Zero-based task index."
)
def main(task_file: Path, task_id: str | None, index: int | None) -> None:
    """Print one TASK_FILE task as JSON without changing the plan."""
    try:
        packet = json.loads(task_file.read_text(encoding="utf-8"))
        task = select_task(packet, task_id, index)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    click.echo(json.dumps(task, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
