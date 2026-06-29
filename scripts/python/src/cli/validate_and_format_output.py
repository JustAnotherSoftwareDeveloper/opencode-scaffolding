#!/usr/bin/env python3
"""CLI entry point for validate-and-format-output.

Validates a full BreakdownTasksOutput object (summary + tasks) against the
task-packet JSON Schema and emits raw JSON on success.

Invocation:
  uv run --directory <scripts-python-dir> validate-and-format-output \\
      [file-path | --stdin] --schema PATH

Exit codes:
  0 — Valid, raw JSON on stdout.
  1 — Schema validation failed.
  2 — Parse/file/schema error (bad input, unreadable file, invalid JSON,
      bad schema).
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.schema import load_schema
from lib.validate_and_format_output import validate_and_format


@click.command(name="validate-and-format-output")
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
)
@click.option(
    "--stdin",
    is_flag=True,
    default=False,
    help="Read input from stdin instead of a file.",
)
@click.option(
    "--schema",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help="Path to the BreakdownTasksOutput JSON Schema file.",
)
def main(
    file_path: str | None,
    stdin: bool,
    schema: str,
) -> None:
    """Validate a BreakdownTasksOutput JSON object against a JSON Schema.

    Reads a full BreakdownTasksOutput JSON object from FILE_PATH or stdin,
    validates it against the schema, and outputs raw JSON on success or
    ``{"valid": false, "errors": [...]}`` on failure.
    """
    # --- Resolve input ---
    if stdin and file_path:
        click.echo(
            "Error: specify either a file path or --stdin, not both.",
            err=True,
        )
        raise SystemExit(2)

    if not stdin and file_path is None:
        click.echo(
            "Error: provide a file path or use --stdin to read from stdin.",
            err=True,
        )
        raise SystemExit(2)

    # --- Load schema ---
    try:
        schema_dict: dict = load_schema(Path(schema))
    except Exception as exc:
        click.echo(f"Error: failed to load schema: {exc}", err=True)
        raise SystemExit(2) from exc

    # --- Read input ---
    try:
        if stdin:
            raw: str = click.get_text_stream("stdin").read()
        else:
            raw = Path(file_path).read_text(encoding="utf-8")  # type: ignore[arg-type]
    except Exception as exc:
        click.echo(f"Error: failed to read input: {exc}", err=True)
        raise SystemExit(2) from exc

    # --- Parse JSON ---
    try:
        data: dict = json.loads(raw)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid JSON input: {exc}", err=True)
        raise SystemExit(2) from exc

    if not isinstance(data, dict):
        click.echo(
            "Error: input must be a JSON object (BreakdownTasksOutput).",
            err=True,
        )
        raise SystemExit(2)

    # --- Validate and format ---
    try:
        valid: bool
        result: str | list[str]
        valid, result = validate_and_format(data, schema_dict)
    except Exception as exc:
        click.echo(f"Error: validation error: {exc}", err=True)
        raise SystemExit(2) from exc

    # --- Output ---
    if valid:
        click.echo(result)
    else:
        click.echo(json.dumps({"valid": False, "errors": result}))
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
