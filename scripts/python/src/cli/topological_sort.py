#!/usr/bin/env python3
"""CLI entry point for topological-sort — topological sort of tasks.

Reads a JSON array of task objects (each with ``id`` and optionally
``dependencies``) from a file, stdin, or a .tasks state file, then
writes a topologically sorted JSON array to stdout.

When ``--state-file`` is used, the file must be a JSON object with a
``tasks`` array.  On successful sort the sorted array is written back
into the file's ``tasks`` field (atomic write).  On cycle detection the
file is not modified.

Usage:

  topological-sort <file-path>
  topological-sort --stdin
  topological-sort --state-file <path>

Exit codes:

  0 — Success, sorted JSON array on stdout.
  1 — Cycle detected. Original input printed to stdout, cycle path to stderr.
  2 — Parse error (invalid JSON, missing ``id`` fields). Error to stderr.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
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


def _read_state_tasks(state_path: str) -> list[dict[str, object]]:
    """Read and parse the ``tasks`` array from a .tasks state file.

    The file must be a JSON object containing a ``tasks`` key (array).
    """
    try:
        raw = Path(state_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read state file: {exc}") from exc

    try:
        state = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in state file: {exc}") from exc

    if not isinstance(state, dict):
        raise ValueError("State file must contain a JSON object")

    tasks = state.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("State file is missing a 'tasks' array")

    return tasks  # type: ignore[return-value]


def _write_state_tasks(state_path: str, tasks: list[dict[str, object]]) -> None:
    """Atomically write *tasks* back into the state file's ``tasks`` field.

    Reads the existing state file, replaces the ``tasks`` field, writes
    to a temporary file in the same directory, then renames atomically.
    """
    path = Path(state_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read state file for update: {exc}") from exc

    try:
        state = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in state file: {exc}") from exc

    if not isinstance(state, dict):
        raise ValueError("State file must contain a JSON object")

    state["tasks"] = tasks
    content = json.dumps(state, indent=2, default=str) + "\n"

    # Atomic write via temp file + rename
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


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
@click.option(
    "--state-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a .tasks state file (JSON object with 'tasks' array)",
)
def main(file_path: str | None, stdin: bool, state_file: str | None) -> None:
    """Topologically sort tasks by their dependency graph.

    FILE_PATH is an optional path to a JSON file.  If omitted, use
    --stdin or --state-file.
    """
    # -- Mutual exclusivity check -------------------------------------------
    provided_count = sum([bool(file_path), bool(stdin), bool(state_file)])
    if provided_count == 0:
        click.echo(
            "Error: Provide a file path, --stdin, or --state-file",
            err=True,
        )
        raise SystemExit(2)
    if provided_count > 1:
        click.echo(
            "Error: --state-file is mutually exclusive with a file path and --stdin",
            err=True,
        )
        raise SystemExit(2)

    # -- Read input ---------------------------------------------------------
    try:
        if state_file:
            tasks = _read_state_tasks(state_file)
        else:
            tasks = _read_input(file_path)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc

    # -- Sort ---------------------------------------------------------------
    try:
        sorted_tasks = sort(tasks)
    except ValueError as exc:
        # Cycle detected — do NOT modify state file (if any); output
        # original input unchanged, cycle path to stderr
        click.echo(json.dumps(tasks, default=str))
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    # -- Write back to state file on success --------------------------------
    if state_file:
        try:
            _write_state_tasks(state_file, sorted_tasks)
        except ValueError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(2) from exc

    # -- Output -------------------------------------------------------------
    click.echo(json.dumps(sorted_tasks, default=str))


if __name__ == "__main__":  # pragma: no cover
    main()
