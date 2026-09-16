#!/usr/bin/env python3
"""CLI entry point for init-task-packet — atomically publish a completed task packet.

This script is invoked as:
  uv run --directory <scripts-python-dir> init-task-packet [options]

Exit codes:
  0 — Success, output path printed to stdout.
  1 — Invalid packet (including a missing or malformed canonical slug).
  2 — File-system error (collision, write failure).
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from contextlib import suppress
from pathlib import Path

import click

from lib.schema import load_task_packet_schema
from lib.validate_task_structure.core import validate_root


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

    Reads a complete canonical task-packet JSON object from stdin. Preserves its
    supplied ``slug`` unchanged, prepends an epoch-millisecond timestamp, and writes
    the object to ``<output-dir>/<timestamp>-<slug>.json``.

    Existing destination files are never replaced.
    """
    try:
        raw = click.get_text_stream("stdin").read()
    except OSError as exc:
        click.echo(f"Error: reading stdin: {exc}", err=True)
        raise SystemExit(1) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: stdin is not valid JSON: {exc}", err=True)
        raise SystemExit(1) from exc

    if not isinstance(data, dict):
        click.echo("Error: stdin JSON must be an object", err=True)
        raise SystemExit(1)

    try:
        schema = load_task_packet_schema()
    except Exception as exc:
        click.echo(
            f"Error: failed to load canonical task-packet schema: {exc}", err=True
        )
        raise SystemExit(2) from exc

    valid, errors = validate_root(data, schema)
    if not valid:
        click.echo(
            "Error: packet must satisfy the canonical task-packet schema: "
            + "; ".join(errors),
            err=True,
        )
        raise SystemExit(1)

    slug = data["slug"]
    assert isinstance(slug, str)  # Established by canonical root validation.

    timestamp = time.time_ns() // 1_000_000
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{timestamp}-{slug}.json"

    fd, tmp = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=output_dir
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(tmp, destination)
    except FileExistsError:
        click.echo(f"Error: output already exists: {destination}", err=True)
        raise SystemExit(2) from None
    except OSError as exc:
        click.echo(f"Error: writing output: {exc}", err=True)
        raise SystemExit(2) from exc
    finally:
        with suppress(FileNotFoundError):
            os.unlink(tmp)

    click.echo(str(destination))


if __name__ == "__main__":  # pragma: no cover
    main()
