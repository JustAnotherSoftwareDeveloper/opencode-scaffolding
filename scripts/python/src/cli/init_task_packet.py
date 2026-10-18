#!/usr/bin/env python3
"""CLI entry point for init-task-packet — atomically publish a task packet.

This script is invoked as:
  uv run --directory <scripts-python-dir> init-task-packet [options]

Exit codes:
  0 — Success, output path printed to stdout.
  2 — Malformed JSON, non-object JSON, or invalid packet input.
  3 — Stdin read, schema-loading, or filesystem/environment error.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.task_packet import (
    InvalidTaskPacketError,
    TaskPacketSchemaError,
    initialize_task_packet,
)


@click.command(name="init-task-packet")
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path(".tasks"),
    show_default=True,
    help="Directory to write the packet",
)
def main(output_dir: Path) -> None:
    """Atomically publish a task packet read from stdin.

    Read a complete canonical task-packet JSON object from stdin. Preserve its
    supplied ``slug`` unchanged, prepend an epoch-millisecond timestamp,
    and write the object to ``<output-dir>/<timestamp>-<slug>.json``.

    Existing destination files are never replaced.
    """
    try:
        raw = click.get_text_stream("stdin").read()
    except OSError as exc:
        click.echo(f"Error: reading stdin: {exc}", err=True)
        raise SystemExit(3) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: stdin is not valid JSON: {exc}", err=True)
        raise SystemExit(2) from exc

    if not isinstance(data, dict):
        click.echo("Error: stdin JSON must be an object", err=True)
        raise SystemExit(2)

    try:
        destination = initialize_task_packet(data, output_dir)
    except InvalidTaskPacketError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except (OSError, TaskPacketSchemaError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(3) from exc

    click.echo(str(destination))


if __name__ == "__main__":  # pragma: no cover
    main()
