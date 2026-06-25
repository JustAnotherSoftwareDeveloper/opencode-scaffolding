"""CLI entry point for resolve-script-root — resolve scripts/python/ root path.

This script is invoked as:
  uv run --directory <scripts-python-dir> resolve-script-root [options]

It resolves the correct scripts/<runtime>/ directory based on:
1. $OPENCODE_SCRIPTS_PYTHON (highest priority)
2. <project-root>/.opencode/scripts/<runtime>
3. ~/.config/opencode/scripts/<runtime> (global fallback)

Exit codes:
  0 — Success, path printed to stdout.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.resolve_script_root.core import resolve_script_root


@click.command(name="resolve-script-root")
@click.option(
    "--runtime",
    type=click.Choice(["python", "node", "shell"]),
    default="python",
    show_default=True,
    help="Script runtime type.",
)
@click.option(
    "--project-root",
    type=click.Path(file_okay=False, dir_okay=True, readable=True),
    default=None,
    help="Explicit project root directory.",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
def main(
    runtime: str,
    project_root: str | None,
    format: str,
) -> None:
    """Resolve the scripts/<runtime>/ root directory path.

    Prints the resolved path and exits 0 on success.
    """
    pr = Path(project_root) if project_root else None
    resolved_path, source = resolve_script_root(runtime=runtime, project_root=pr)

    if format == "json":
        output = {
            "path": str(resolved_path),
            "runtime": runtime,
            "source": source,
        }
        click.echo(json.dumps(output, default=str))
    else:
        click.echo(str(resolved_path))


if __name__ == "__main__":
    main()  # pragma: no cover
