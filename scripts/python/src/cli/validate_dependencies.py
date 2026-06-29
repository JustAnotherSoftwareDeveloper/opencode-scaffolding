#!/usr/bin/env python3
"""CLI entry point for validate-dependencies — validate task dependency graphs.

This script is invoked as:

    uv run --directory <scripts-python-dir> validate-dependencies [file-path | --stdin]

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
def main(file_path: str | None, stdin: bool) -> None:
    """Validate a task dependency graph from a JSON file or stdin.

    Input must be a JSON array of task objects. Each task must have an
    ``id`` (string/UUID) and ``dependencies`` (array of string/UUID).

    Validation checks for orphan references (dependencies that don't
    match any task id), self-loops (a task depending on itself), and
    cycles (circular dependency chains detected via DFS).
    """
    try:
        if stdin:
            raw: str = sys.stdin.read()
        elif file_path:
            raw = Path(file_path).read_text(encoding="utf-8")
        else:
            click.echo("Error: provide a file path or use --stdin", err=True)
            raise SystemExit(2)

        tasks: list[dict] = json.loads(raw)
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
