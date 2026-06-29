#!/usr/bin/env python3
"""CLI entry point for validate-dependencies — validate task dependency graphs.

This script is invoked as:

    uv run --directory <scripts-python-dir> validate-dependencies [file-path | --stdin | --state-file PATH]

Exit codes:
    0 — Valid dependency graph.
    1 — Violations found (orphans, cycles, self-loops).
    2 — Parse or file error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from lib.validate_dependencies import validate


@click.command(name="validate-dependencies")
@click.argument(
    "file_path",
    required=False,
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "--stdin",
    is_flag=True,
    default=False,
    help="Read JSON input from stdin instead of a file",
)
@click.option(
    "--state-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Read tasks array from a .tasks state file (mutually exclusive with file_path and --stdin)",
)
def main(file_path: str | None, stdin: bool, state_file: str | None) -> None:
    """Validate a task dependency graph from a JSON file, stdin, or .tasks state file.

    Input must be a JSON array of task objects. Each task must have an
    ``id`` (string/UUID) and ``dependencies`` (array of string/UUID).

    When --state-file is provided, the file must be a JSON object with a
    ``tasks`` array. The state file is not modified.

    Validation checks for orphan references (dependencies that don't
    match any task id), self-loops (a task depending on itself), and
    cycles (circular dependency chains detected via DFS).
    """
    try:
        # Count how many input sources were specified
        input_sources = sum([bool(file_path), stdin, bool(state_file)])
        if input_sources == 0:
            click.echo(
                "Error: provide a file path, use --stdin, or use --state-file",
                err=True,
            )
            raise SystemExit(2)
        if input_sources > 1:
            click.echo(
                "Error: --state-file is mutually exclusive with file_path and --stdin",
                err=True,
            )
            raise SystemExit(2)

        if state_file:
            raw: str = Path(state_file).read_text(encoding="utf-8")
            data: dict = json.loads(raw)
            if not isinstance(data, dict):
                click.echo("Error: state file must be a JSON object", err=True)
                raise SystemExit(2)
            tasks_list = data.get("tasks")
            if not isinstance(tasks_list, list):
                click.echo(
                    "Error: state file must contain a 'tasks' array", err=True
                )
                raise SystemExit(2)
            tasks: list[dict] = tasks_list
        elif stdin:
            raw = sys.stdin.read()
            tasks = json.loads(raw)
            if not isinstance(tasks, list):
                click.echo("Error: input must be a JSON array", err=True)
                raise SystemExit(2)
        elif file_path:
            raw = Path(file_path).read_text(encoding="utf-8")
            tasks = json.loads(raw)
            if not isinstance(tasks, list):
                click.echo("Error: input must be a JSON array", err=True)
                raise SystemExit(2)

    except (json.JSONDecodeError, OSError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc

    valid, errors = validate(tasks)

    if valid:
        click.echo(json.dumps({"valid": True}))
    else:
        click.echo(json.dumps({"valid": False, "errors": errors}))
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
