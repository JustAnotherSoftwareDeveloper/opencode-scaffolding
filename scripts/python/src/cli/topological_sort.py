#!/usr/bin/env python3
"""CLI entry point for topological-sort — topological sort of tasks.

Reads a JSON array of task objects (each with ``id`` and optionally
``dependencies``) from a file or stdin, then writes a topologically
sorted JSON array to stdout.

Usage:

  topological-sort <file-path>
  topological-sort --stdin

Exit codes:

  0 — Success, sorted JSON array on stdout.
  1 — Cycle detected. Original input printed to stdout, cycle path to stderr.
  2 — Parse error (invalid JSON, missing ``id`` fields). Error to stderr.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from lib.topological_sort import sort


def _read_input(file_path: str | None) -> list[dict[str, object]]:
    """Read and parse JSON array from *file_path* or stdin."""
    raw: str
    if file_path:
        try:
            raw = Path(file_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"Cannot read file: {exc}") from exc
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON input: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Input must be a JSON array of task objects")

    return data  # type: ignore[return-value]


@click.command(name="topological-sort")
@click.argument(
    "file_path",
    required=False,
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--stdin",
    is_flag=True,
    default=False,
    help="Read input from stdin instead of a file",
)
def main(file_path: str | None, stdin: bool) -> None:
    """Topologically sort tasks by their dependency graph.

    FILE_PATH is an optional path to a JSON file. If omitted, use --stdin.
    """
    if not file_path and not stdin:
        click.echo(
            "Error: Provide a file path or use --stdin to read from stdin",
            err=True,
        )
        raise SystemExit(2)

    # Read and parse input
    try:
        tasks = _read_input(file_path)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc

    # Sort
    try:
        sorted_tasks = sort(tasks)
    except ValueError as exc:
        # Cycle detected — output original input unchanged, cycle path to stderr
        click.echo(json.dumps(tasks, default=str))
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(json.dumps(sorted_tasks, default=str))


if __name__ == "__main__":  # pragma: no cover
    main()
