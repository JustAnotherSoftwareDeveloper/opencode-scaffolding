#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import click

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))


@click.command(name="collect-skills")
@click.option(
    "--project-root",
    type=click.Path(file_okay=False, dir_okay=True, readable=True),
    default=str(Path.cwd()),
    show_default=True,
    help="Project root directory",
)
@click.option(
    "--config-dir",
    type=click.Path(file_okay=False, dir_okay=True, readable=True),
    default=str(Path.home() / ".config" / "opencode"),
    show_default=True,
    help="Global configuration directory",
)
@click.option(
    "--extra-paths",
    type=click.Path(file_okay=False, dir_okay=True, readable=True),
    multiple=True,
    default=[],
    help="Additional scan directories (may be specified multiple times)",
)
@click.option(
    "--include-archive",
    is_flag=True,
    default=False,
    help="Include archive/ directories in skill discovery",
)
@click.option(
    "--builtins-manifest",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    default=None,
    help="JSON file listing built-in skills",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print warnings and progress to stderr",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    default=None,
    help="Write JSON output to file instead of stdout",
)
def main(
    project_root: str,
    config_dir: str,
    extra_paths: tuple[str, ...],
    include_archive: bool,
    builtins_manifest: str | None,
    verbose: bool,
    output: str | None,
) -> None:
    """Collect OpenCode skills from the project and configuration directories.

    Discovers SKILL.md files across project roots, global config, archives,
    and extra paths, then produces a deduplicated JSON index.
    """
    from lib.collect_skills.discovery import discover_all_skills
    from lib.collect_skills.models import SkillIndex

    index = SkillIndex()

    try:
        discover_all_skills(
            index,
            verbose=verbose,
            project_root=Path(project_root),
            config_dir=Path(config_dir),
            extra_paths=[Path(p) for p in extra_paths],
            include_archive=include_archive,
        )
    except Exception as exc:
        click.echo(f"[collect-skills] Error during discovery: {exc}", err=True)
        raise SystemExit(1)

    json_output = index.to_json()

    if output:
        output_path = Path(output)
        try:
            output_path.write_text(json_output, encoding="utf-8")
        except OSError as exc:
            click.echo(f"[collect-skills] Error writing output: {exc}", err=True)
            raise SystemExit(1)
    else:
        click.echo(json_output)

    if verbose and index.warnings:
        for warning in index.warnings:
            click.echo(f"[collect-skills] Warning: {warning}", err=True)


if __name__ == "__main__":
    main()