#!/usr/bin/env python3
"""Validate a generated skill directory against skill-writer rules.

Usage:
    uv run --directory ~/.config/opencode/scripts/python \
        python -m src.cli.skill_validator <path/to/skill/dir>

Returns structured JSON and exits 0 if all checks pass, 1 if any fail.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.skill_validator import run_all


@click.command(name="skill-validator")
@click.argument(
    "skill_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)
def cli(skill_path: str) -> None:
    """Validate a generated skill directory against skill-writer rules.

    SKILL_PATH is the path to the skill directory to validate.

    Returns structured JSON and exits 0 if all checks pass, 1 if any fail.
    """
    result = run_all(Path(skill_path))
    click.echo(json.dumps(result, indent=2))

    # Exit 0 if all checks pass, 1 if any fail
    passed = all(check.get("passed", False) for check in result["checks"])
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":  # pragma: no cover
    cli()
