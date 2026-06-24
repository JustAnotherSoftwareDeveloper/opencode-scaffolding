#!/usr/bin/env python3
"""Initialize runbook state from a runbook file (v3 XML target, v2 XML
transitional, or legacy v1 JSON)."""

from __future__ import annotations

from pathlib import Path

import click

from lib.runbook_state import HARNESS_ROOT, seed_runbook_state
from lib.runbook_xml import RunbookLoadError, load_runbook


@click.command(name="init-runbook-state")
@click.argument(
    "runbook_file",
    type=click.Path(exists=True, readable=True),
)
def cli(runbook_file: str) -> None:
    """Initialize runbook state from a runbook file.

    RUNBOOK_FILE is the path to main.xml (v3/v2) or legacy runbook.json.
    """
    try:
        runbook_path = Path(runbook_file).resolve()
        if runbook_path.parent.parent.name != ".runbooks":
            click.echo(
                f"Error: Runbook file {runbook_path} must be located at "
                f".runbooks/<runbook_id>/main.xml or .runbooks/<runbook_id>/runbook.json.",
                err=True,
            )
            raise SystemExit(1)

        if runbook_path.name == "runbook.json":
            schema_path = HARNESS_ROOT / "skills/build-runbook/schemas/schema.json"
            if schema_path.exists():
                from lib.json_validation import validate_json_path

                validate_json_path(runbook_path, schema_path)

        result = load_runbook(runbook_path, require_workspace_xml=False)
        runbook_data = result.data
        runbook_id = runbook_data.get("id")
        if not runbook_id:
            click.echo(
                f"Error: Runbook file {runbook_file} does not contain an 'id' field.",
                err=True,
            )
            raise SystemExit(1)
        if runbook_path.parent.name != runbook_id:
            click.echo(
                f"Error: Runbook directory name '{runbook_path.parent.name}' "
                f"must match runbook id '{runbook_id}'.",
                err=True,
            )
            raise SystemExit(1)

        if result.format_version == 3:
            seed_runbook_state(runbook_data, runbook_path)
            state_path = runbook_path.parent / runbook_data.get("state", "state.xml")
            click.echo(f"Successfully initialized runbook-local state: {state_path}")
            raise SystemExit(0)

        state_dir_path = runbook_data.get("state_dir")
        if not state_dir_path:
            click.echo(
                f"Error: Runbook file {runbook_file} does not contain a 'state_dir' field.",
                err=True,
            )
            raise SystemExit(1)
        expected_state_dir = f"../../.state/{runbook_id}/"
        if state_dir_path != expected_state_dir:
            click.echo(
                f"Error: Runbook state_dir must be '{expected_state_dir}' "
                f"so state keys off the runbook id; got '{state_dir_path}'.",
                err=True,
            )
            raise SystemExit(1)
        state_dir = (runbook_path.parent / state_dir_path).resolve()
        if state_dir.exists() and any(state_dir.iterdir()):
            click.echo(
                f"Error: Target state directory {state_dir} already exists and is not empty.",
                err=True,
            )
            raise SystemExit(1)
        state_dir.mkdir(parents=True, exist_ok=True)
        seed_runbook_state(runbook_data, runbook_path, state_dir)
        click.echo(f"Successfully initialized state directory: {state_dir}")
        raise SystemExit(0)

    except RunbookLoadError as exc:
        click.echo(f"init-runbook-state: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"init-runbook-state: Unexpected error: {exc}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()