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

from lib.validate_skill_meta.core import compute_tag_frequencies, validate_skill_file


@click.command(name="validate-skill-meta")
@click.argument(
    "skill_paths",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    nargs=-1,
    required=True,
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
def main(skill_paths: tuple[str, ...], format: str, verbose: bool) -> None:
    """Validate YAML frontmatter fields (name, description, class) in SKILL_PATHS.

    SKILL_PATHS are one or more paths to SKILL.md files.
    """
    paths = [Path(skill_path) for skill_path in skill_paths]
    tag_frequencies = compute_tag_frequencies()
    results = []

    for path in paths:
        if verbose:
            click.echo(f"Validating: {path.resolve()}", err=True)
        result = validate_skill_file(path, tag_frequencies)
        results.append(result)

        if format == "text":
            if result["valid"]:
                click.echo(f"VALID {path}")
            else:
                click.echo(f"INVALID {path}")
                for err in result["errors"]:
                    click.echo(f"  - {err}")

    if format == "json":
        output = results[0] if len(results) == 1 else results
        click.echo(json.dumps(output, default=str))

    if any(not result["valid"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()  # pragma: no cover
