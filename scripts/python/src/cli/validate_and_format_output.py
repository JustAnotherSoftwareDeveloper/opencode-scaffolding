#!/usr/bin/env python3
"""CLI entry point for validate-and-format-output.

Validates a full BreakdownTasksOutput object (summary + tasks) against the
task-packet JSON Schema and emits raw JSON on success.

Invocation:
  uv run --directory <scripts-python-dir> validate-and-format-output \\
      [file-path | --stdin | --state-file PATH] --schema PATH

  --state-file is mutually exclusive with file-path and --stdin.
  When --state-file is provided, the validated JSON is written back to the
  state file on success (exit 0). On failure (exit 1) the file is unchanged.

Exit codes:
  0 — Valid, raw JSON on stdout.
  1 — Schema validation failed.
  2 — Parse/file/schema error (bad input, unreadable file, invalid JSON,
      bad schema).
"""

from __future__ import annotations

import json
import os
import tempfile
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
@click.option(
    "--state-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help=(
        "Path to a .tasks state file. Read, validate, and write back the"
        " validated JSON on success. Mutually exclusive with file path and"
        " --stdin."
    ),
)
def main(
    file_path: str | None,
    stdin: bool,
    schema: str,
    state_file: str | None,
) -> None:
    """Validate a BreakdownTasksOutput JSON object against a JSON Schema.

    Reads a full BreakdownTasksOutput JSON object from FILE_PATH, stdin, or
    --state-file, validates it against the schema, and outputs raw JSON on
    success or ``{"valid": false, "errors": [...]}`` on failure.

    When --state-file is provided: on success the validated JSON is written
    back to the state file atomically; on failure the file is left unchanged.
    """
    # --- Mutually exclusive check ---
    if state_file and (stdin or file_path):
        click.echo(
            "Error: --state-file is mutually exclusive with file path and"
            " --stdin.",
            err=True,
        )
        raise SystemExit(2)

    # --- Resolve input ---
    if state_file:
        # No additional checks needed -- state_file is the input source.
        pass
    elif stdin and file_path:
        click.echo(
            "Error: specify either a file path or --stdin, not both.",
            err=True,
        )
        raise SystemExit(2)
    elif not stdin and file_path is None:
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
        if state_file:
            _write_atomically(state_file, result)
        click.echo(result)
    else:
        click.echo(json.dumps({"valid": False, "errors": result}))
        raise SystemExit(1)


def _write_atomically(path: str, content: str) -> None:
    """Write *content* to *path* atomically via a temp file + rename.

    The temp file is created in the same directory to ensure the rename is
    on the same filesystem.
    """
    dst = Path(path)
    parent = dst.parent
    tmp_dir = parent if parent.exists() and parent.is_dir() else None

    fd, tmp_path = tempfile.mkstemp(
        dir=tmp_dir,
        prefix=f".{dst.name}.tmp_",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up temp file on any error (including KeyboardInterrupt)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
