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
    required=False,
    help="Kebab-case filename slug for the local .tasks output.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path, resolve_path=True),
    required=False,
    help="Directory for the generated task JSON file.",
)
@click.option(
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path, resolve_path=True),
    required=False,
    help="Explicit JSON output file, mutually exclusive with legacy output options.",
)
def main(
    summary_slug: str | None, output_dir: Path | None, output_file: Path | None
) -> None:
    """Assign skills to stdin TaskDraftList JSON and print its local path."""
    try:
        _validate_destination_options(summary_slug, output_dir, output_file)
        if output_file is not None:
            _require_local_output(output_file)
        data = _read_stdin_json()
        output_path = generate_task_json(
            data,
            summary_slug,
            output_dir=output_dir,
            output_file=output_file,
        )
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


def _require_local_output(path: Path) -> None:
    """Reject an explicit output path outside the current working directory."""
    if not path.is_relative_to(Path.cwd()):
        raise ValueError("--output-file must be within the current working directory")


def _validate_destination_options(
    summary_slug: str | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> None:
    """Require either the complete legacy destination or an explicit file."""
    legacy = summary_slug is not None or output_dir is not None
    if output_file is not None and legacy:
        raise ValueError(
            "--output-file is mutually exclusive with legacy output options"
        )
    if output_file is None and (summary_slug is None or output_dir is None):
        raise ValueError(
            "provide --output-file or both --summary-slug and --output-dir"
        )


def _read_stdin_json() -> dict[str, Any]:
    """Read and parse one JSON object from standard input."""
    data = json.loads(click.get_text_stream("stdin").read())
    if not isinstance(data, dict):
        raise ValueError("stdin JSON must be an object")
    return data


if __name__ == "__main__":  # pragma: no cover
    main()
