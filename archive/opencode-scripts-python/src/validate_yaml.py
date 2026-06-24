#!/usr/bin/env python3
"""Validate YAML syntax."""

from __future__ import annotations

import click

from lib.yaml_validation import YamlValidationError, validate_yaml_path


@click.command(name="validate-yaml")
@click.argument(
    "yaml_file",
    type=click.Path(exists=True, readable=True),
)
def cli(yaml_file: str) -> None:
    """Validate YAML syntax of a file.

    YAML_FILE is the path to the YAML file to validate.
    """
    try:
        validate_yaml_path(yaml_file)
    except YamlValidationError as exc:
        click.echo(f"validate-yaml: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"validate-yaml: valid: {yaml_file}", err=True)


if __name__ == "__main__":
    cli()