"""Validate a complete skill entry point against the profile contract."""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.skill_validator import validate_skill_file
from lib.skill_validator.skill_md import _body_errors as _body_errors


@click.command(name="validate-skill-md")
@click.argument(
    "skill_paths", type=click.Path(dir_okay=False), nargs=-1, required=True
)
def main(skill_paths: tuple[str, ...]) -> None:
    """Validate one or more complete SKILL.md files."""
    results = [validate_skill_file(Path(value)) for value in skill_paths]
    click.echo(json.dumps(results[0] if len(results) == 1 else results))
    if any(not result["valid"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
