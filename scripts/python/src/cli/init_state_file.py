"""CLI entry point for init-state-file — create a decomposition state file.

This script is invoked as:
  uv run --directory <scripts-python-dir> init-state-file --output-dir <path>

Exit codes:
  0 — Success, state file path printed to stdout.
  1 — Runtime error (directory creation or file write failure).
  2 — User error (invalid arguments).
"""

from __future__ import annotations

import click

from lib.init_state_file.core import init_state


@click.command(name="init-state-file")
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    required=True,
    help="Path to the .tasks/ directory.",
)
def main(output_dir: str) -> None:
    """Create a stub decomposition state file and print its path."""
    try:
        state_path = init_state(output_dir)
    except FileExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    except OSError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(state_path)


if __name__ == "__main__":  # pragma: no cover
    main()
