"""CLI entry point for validate-skill-meta — validate skill SKILL.md YAML frontmatter.

This script is invoked as:
  uv run --directory <scripts-python-dir> validate-skill-meta <skill-path> [options]

Exit codes:
  0 — Validation passed (valid: true).
  1 — Validation failed (valid: false, errors listed).
  2 — User error (invalid arguments).
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.validate_skill_meta.core import validate_skill_file


@click.command(name="validate-skill-meta")
@click.argument(
    "skill_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Print diagnostic information to stderr.",
)
def main(skill_path: str, format: str, verbose: bool) -> None:
    """Validate YAML frontmatter fields (name, description, class) in SKILL_PATH.

    SKILL_PATH is the path to a SKILL.md file.
    """
    path = Path(skill_path)

    if verbose:
        click.echo(f"Validating: {path.resolve()}", err=True)

    result = validate_skill_file(path)

    if format == "json":
        click.echo(json.dumps(result, default=str))
    else:
        if result["valid"]:
            click.echo("VALID")
        else:
            click.echo("INVALID")
            for err in result["errors"]:
                click.echo(f"  - {err}")

    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()  # pragma: no cover
