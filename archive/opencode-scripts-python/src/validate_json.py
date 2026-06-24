#!/usr/bin/env python3
"""Validate JSON syntax and optional JSON Schema conformance."""

from __future__ import annotations

import click

from lib.json_validation import JsonValidationError, validate_json_path


@click.command(name="validate-json")
@click.argument(
    "json_file",
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--schema",
    type=click.Path(exists=True, readable=True),
    default=None,
    help="Optional path to a JSON Schema file",
)
def cli(json_file: str, schema: str | None) -> None:
    """Validate JSON syntax and optional JSON Schema conformance.

    JSON_FILE is the path to the JSON file to validate.
    """
    try:
        validate_json_path(json_file, schema)
    except JsonValidationError as exc:
        click.echo(f"validate-json: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"validate-json: valid: {json_file}", err=True)


if __name__ == "__main__":
    cli()