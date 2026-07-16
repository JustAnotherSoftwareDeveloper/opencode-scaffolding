#!/usr/bin/env python3
"""CLI entry point for validate-task-structure.

Validates task objects against the task-packet JSON Schema.

Invocation:
  uv run --directory <scripts-python-dir> validate-task-structure \\
      [file-path | --stdin] --schema PATH

Exit codes:
  0 — All tasks valid.
  1 — Validation violations found.
  2 — Parse/file/schema error (bad input, unreadable file, invalid JSON,
      bad schema).
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.schema import load_schema
from lib.validate_task_structure import auto_fix_task_structure, validate


@click.command(name="validate-task-structure")
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
)
@click.option(
    "--stdin",
    is_flag=True,
    default=False,
    help="Read task input from stdin instead of a file.",
)
@click.option(
    "--state-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help="Path to a .tasks state file (JSON object with 'tasks' array). "
    "Mutually exclusive with file_path and --stdin.",
)
@click.option(
    "--auto-fix",
    is_flag=True,
    default=False,
    help="Auto-fix skills-only structural errors (maxItems, uniqueItems, "
    "empty strings) in the state file. Requires --state-file.",
)
@click.option(
    "--schema",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help="Path to the task-packet JSON Schema file.",
)
def main(
    file_path: str | None,
    stdin: bool,
    state_file: str | None,
    auto_fix: bool,
    schema: str,
) -> None:
    """Validate task objects from FILE_PATH, --stdin, or --state-file
    against a JSON Schema.

    Reads a JSON array of task objects (or extracts them from a .tasks
    state file) and validates each one against the task-packet schema.
    Outputs ``{"valid": true}`` or ``{"valid": false, "errors": [...]}``
    to stdout.
    """
    # --- Resolve input ---
    if state_file and (stdin or file_path):
        click.echo(
            "Error: --state-file is mutually exclusive with file_path and --stdin.",
            err=True,
        )
        raise SystemExit(2)

    if stdin and file_path:
        click.echo(
            "Error: specify either a file path or --stdin, not both.",
            err=True,
        )
        raise SystemExit(2)

    if not state_file and not stdin and file_path is None:
        click.echo(
            "Error: provide a file path, --stdin, or --state-file.",
            err=True,
        )
        raise SystemExit(2)

    if auto_fix and not state_file:
        click.echo(
            "Error: --auto-fix requires --state-file.",
            err=True,
        )
        raise SystemExit(2)

    # --- Load schema ---
    try:
        schema_dict: dict = load_schema(Path(schema))
    except Exception as exc:
        click.echo(f"Error: failed to load schema: {exc}", err=True)
        raise SystemExit(2) from exc

    # --- Auto-fix mode ---
    if auto_fix:
        try:
            result: dict = auto_fix_task_structure(Path(state_file), schema_dict)  # type: ignore[arg-type]
        except Exception as exc:
            click.echo(f"Error: auto-fix failed: {exc}", err=True)
            raise SystemExit(2) from exc

        click.echo(json.dumps(result))
        if not result.get("valid"):
            raise SystemExit(1)
        return

    # --- Read input ---
    try:
        if state_file:
            raw: str = Path(state_file).read_text(encoding="utf-8")
        elif stdin:
            raw = click.get_text_stream("stdin").read()
        else:
            raw = Path(file_path).read_text(encoding="utf-8")  # type: ignore[arg-type]
    except Exception as exc:
        click.echo(f"Error: failed to read input: {exc}", err=True)
        raise SystemExit(2) from exc

    # --- Parse JSON ---
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid JSON input: {exc}", err=True)
        raise SystemExit(2) from exc

    if state_file:
        if not isinstance(parsed, dict) or "tasks" not in parsed:
            click.echo(
                "Error: --state-file must contain a JSON object with a 'tasks' array.",
                err=True,
            )
            raise SystemExit(2)
        tasks: list[dict] = parsed["tasks"]
        if not isinstance(tasks, list):
            click.echo(
                "Error: 'tasks' in state file must be a JSON array.",
                err=True,
            )
            raise SystemExit(2)
    else:
        if not isinstance(parsed, list):
            click.echo(
                "Error: input must be a JSON array of task objects.",
                err=True,
            )
            raise SystemExit(2)
        tasks = parsed

    # --- Validate ---
    try:
        valid: bool
        errors: list[str]
        valid, errors = validate(tasks, schema_dict)
    except Exception as exc:
        click.echo(f"Error: validation error: {exc}", err=True)
        raise SystemExit(2) from exc

    # --- Output ---
    if valid:
        click.echo(json.dumps({"valid": True}))
    else:
        click.echo(json.dumps({"valid": False, "errors": errors}))
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
