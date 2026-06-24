#!/usr/bin/env python3
"""CLI command to validate runbooks in v1 JSON or v2 XML format.

Usage:
    validate-runbook <runbook_path> [--strict]

Examples:
    # Validate a v2 XML runbook
    validate-runbook .runbooks/my-runbook/main.xml

    # Validate a legacy v1 JSON runbook  
    validate-runbook .runbooks/my-runbook/runbook.json

    # Validate with strict mode (unreferenced steps are errors)
    validate-runbook .runbooks/my-runbook/main.xml --strict

    # Output as JSON
    validate-runbook .runbooks/my-runbook/main.xml --json
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.runbook_xml import validate_runbook, RunbookLoadError


@click.command(name="validate-runbook")
@click.argument(
    "runbook_path",
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Treat warnings as errors (e.g., unreferenced step files)",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output results as JSON",
)
def cli(runbook_path: str, strict: bool, json_output: bool) -> None:
    """Validate a runbook in v1 JSON or v2 XML format.

    RUNBOOK_PATH is the path to runbook.json (v1) or main.xml (v2).
    """
    path = Path(runbook_path)

    try:
        is_valid, messages = validate_runbook(path, strict=strict)

        if json_output:
            result = {
                "valid": is_valid,
                "messages": messages,
            }
            click.echo(json.dumps(result))
        else:
            for msg in messages:
                click.echo(msg)

            if is_valid:
                click.echo("\n✓ Runbook is valid")
                raise SystemExit(0)
            else:
                click.echo("\n✗ Runbook validation failed")
                raise SystemExit(1)

    except RunbookLoadError as e:
        if json_output:
            result = {
                "valid": False,
                "messages": [f"Error: {e}"],
            }
            if e.details:
                result["details"] = e.details
            click.echo(json.dumps(result))
        else:
            click.echo(f"Error: {e}", err=True)
            if e.details:
                for key, value in e.details.items():
                    click.echo(f"  {key}: {value}", err=True)
        raise SystemExit(1)

    except FileNotFoundError:
        if json_output:
            result = {
                "valid": False,
                "messages": [f"Error: File not found: {path}"],
            }
            click.echo(json.dumps(result))
        else:
            click.echo(f"Error: File not found: {path}", err=True)
        raise SystemExit(1)

    except Exception as e:
        if json_output:
            result = {
                "valid": False,
                "messages": [f"Unexpected error: {e}"],
            }
            click.echo(json.dumps(result))
        else:
            click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()