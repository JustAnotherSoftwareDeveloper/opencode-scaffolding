"""CLI for publishing a completed task packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from lib.generate_task_json.core import (
    GenerationValidationError,
    SummarySlugError,
    generate_task_json,
)


@click.command(name="generate-task-json")
@click.option(
    "--skills-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Frozen bare JSON array produced by collect-skills.",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Caller project root used to authorize project skill paths.",
)
@click.option("--summary-slug", default=None)
@click.option(
    "--output-dir", type=click.Path(file_okay=False, path_type=Path), default=None
)
@click.option(
    "--output-file", type=click.Path(dir_okay=False, path_type=Path), default=None
)
def main(
    skills_file: Path,
    project_root: Path | None,
    summary_slug: str | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> None:
    """Validate a completed packet against a frozen collector inventory."""
    try:
        if output_file is None and output_dir is None:
            raise ValueError("provide --output-file or --output-dir")
        inventory = _read_inventory(skills_file)
        data = _read_stdin_json()
        path = generate_task_json(
            data,
            summary_slug,
            skills_index=inventory,
            inventory_project_root=project_root or Path.cwd(),
            output_dir=output_dir,
            output_file=output_file,
        )
    except (
        GenerationValidationError,
        SummarySlugError,
        ValueError,
        json.JSONDecodeError,
        OSError,
    ) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    click.echo(str(path))


def _read_stdin_json() -> dict[str, Any]:
    value = json.loads(click.get_text_stream("stdin").read())
    if not isinstance(value, dict):
        raise ValueError("stdin JSON must be an object")
    return value


def _read_inventory(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError("--skills-file must contain a bare JSON array of objects")
    return value


if __name__ == "__main__":  # pragma: no cover
    main()
