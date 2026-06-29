#!/usr/bin/env python3
"""CLI entry point for generate-uuids — generate N unique UUID v4 strings.

Invocation:
  uv run --directory <scripts-python-dir> generate-uuids <count>

Exit codes:
  0 — Success, JSON array of UUIDs written to stdout.
  1 — Internal error (unexpected exception).
  2 — User error (count not in 1-100 range).
"""

from __future__ import annotations

import json

import click

from lib.generate_uuids import generate


@click.command(name="generate-uuids")
@click.argument("count", type=int)
def main(count: int) -> None:
    """Generate COUNT unique UUID v4 strings and print as JSON array."""
    try:
        uuids = generate(count)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(json.dumps(uuids))


if __name__ == "__main__":  # pragma: no cover
    main()
