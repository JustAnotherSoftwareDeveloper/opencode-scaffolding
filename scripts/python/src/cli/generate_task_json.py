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
import os
from pathlib import Path
from typing import Any

import click

from lib.generate_task_json.core import (
    GenerationValidationError,
    SummarySlugError,
    generate_task_json,
)

_SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@click.command(name="generate-task-json")
@click.option(
    "--summary-slug",
    type=str,
    required=False,
    help="Kebab-case slug for the epoch-prefixed local .tasks output.",
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
    click.echo(str(_relative_output_path(output_path)))


def _require_local_output(path: Path) -> None:
    """Reject an explicit output path outside the current working directory."""
    if not path.is_relative_to(_caller_working_directory()):
        raise ValueError("--output-file must be within the current working directory")


def _caller_working_directory() -> Path:
    """Return the caller directory preserved in PWD by ``uv --directory``."""
    current_directory = Path.cwd().resolve()
    if current_directory != _SCRIPT_PROJECT_ROOT:
        return current_directory
    return Path(os.environ.get("PWD", current_directory)).resolve()


def _relative_output_path(output_path: Path) -> Path:
    """Render output relative to the caller directory when possible."""
    caller_directory = _caller_working_directory()
    if output_path.is_relative_to(caller_directory):
        return output_path.relative_to(caller_directory)
    return output_path.relative_to(output_path.parent)


def _validate_destination_options(
    summary_slug: str | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> None:
    """Require either an output directory (slug may be derived) or an explicit file."""
    legacy = summary_slug is not None or output_dir is not None
    if output_file is not None and legacy:
        raise ValueError(
            "--output-file is mutually exclusive with legacy output options"
        )
    if output_file is None and output_dir is None:
        raise ValueError(
            "provide --output-file or --output-dir (--summary-slug is optional)"
        )


def _read_stdin_json() -> dict[str, Any]:
    """Read and parse one JSON object from standard input."""
    data = json.loads(click.get_text_stream("stdin").read())
    if not isinstance(data, dict):
        raise ValueError("stdin JSON must be an object")
    return data


if __name__ == "__main__":  # pragma: no cover
    main()
