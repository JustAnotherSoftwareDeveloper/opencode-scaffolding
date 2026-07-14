"""CLI entry point for generate-task-json.

Reads a TaskDraftList JSON object from stdin and creates a valid,
skill-assigned BreakdownTasksOutput JSON object in the requested output directory.

Exit codes:
  0 — Output path written to stdout.
  1 — Input validation, skill assignment, or final validation failed.
  2 — JSON, path, schema, or argument error.
"""

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
    "--summary-slug",
    type=str,
    required=True,
    help="Kebab-case filename slug for the local .tasks output.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path, resolve_path=True),
    required=True,
    help="Directory for the generated task JSON file.",
)
def main(summary_slug: str, output_dir: Path) -> None:
    """Assign skills to stdin TaskDraftList JSON and print its local path."""
    try:
        data = _read_stdin_json()
        output_path = generate_task_json(data, summary_slug, output_dir=output_dir)
    except (GenerationValidationError, SummarySlugError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    except RuntimeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    click.echo(str(output_path.relative_to(Path.cwd())))


def _read_stdin_json() -> dict[str, Any]:
    """Read and parse one JSON object from standard input."""
    data = json.loads(click.get_text_stream("stdin").read())
    if not isinstance(data, dict):
        raise ValueError("stdin JSON must be an object")
    return data


if __name__ == "__main__":  # pragma: no cover
    main()
