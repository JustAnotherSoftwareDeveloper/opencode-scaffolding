"""CLI entry point for render-task-markdown."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from lib.render_task_markdown.core import RenderValidationError, render_task_markdown


@click.command(name="render-task-markdown")
@click.option(
    "--input",
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "--output",
    "output_file",
    type=click.Path(dir_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Atomically replace an existing output after a bounded plan correction.",
)
def main(
    input_file: Path,
    output_file: Path,
    overwrite: bool,
) -> None:
    """Render validated INPUT task JSON as OUTPUT Markdown."""
    try:
        _require_local_output(output_file)
        data = _read_json(input_file)
        result = render_task_markdown(
            data,
            output_file,
            overwrite=overwrite,
        )
    except (OSError, ValueError, json.JSONDecodeError, RenderValidationError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    click.echo(str(result.relative_to(Path.cwd())))


def _require_local_output(path: Path) -> None:
    """Reject an output path outside the current working directory."""
    if not path.is_relative_to(Path.cwd()):
        raise ValueError("--output must be within the current working directory")


def _read_json(input_file: Path) -> dict[str, Any]:
    """Read one JSON object from *input_file*."""
    data = json.loads(input_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")
    return data


if __name__ == "__main__":  # pragma: no cover
    main()
