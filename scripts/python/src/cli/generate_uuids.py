#!/usr/bin/env python3
"""CLI entry point for generate-uuids — generate N unique UUID v4 strings.

Invocation:
  uv run --directory <scripts-python-dir> generate-uuids <count>
  uv run --directory <scripts-python-dir> generate-uuids --state-file <path>

Exit codes:
  0 — Success, JSON array of UUIDs written to stdout.
  1 — Internal error (unexpected exception).
  2 — User error (count not in 1-100 range, missing argument, or state-file write failure).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import click

from lib.generate_uuids import generate


@click.command(name="generate-uuids")
@click.argument("count", type=int, required=False)
@click.option(
    "--state-file",
    type=click.Path(exists=True, dir_okay=False, readable=True, writable=True),
    default=None,
    help="Path to a .tasks state file — read tasks, assign UUIDs to each task id, write back.",
)
def main(count: int | None = None, state_file: str | None = None) -> None:
    """Generate COUNT unique UUID v4 strings and print as JSON array.

    Provide COUNT (a number 1-100) to generate that many UUIDs, or provide
    --state-file PATH to read a .tasks state file, assign one UUID per task,
    and write the updated file back.
    """
    # --- Validate mutual exclusivity ----------------------------------------
    if count is not None and state_file is not None:
        click.echo(
            "Error: COUNT argument and --state-file are mutually exclusive. "
            "Provide exactly one.",
            err=True,
        )
        raise SystemExit(2)

    if count is None and state_file is None:
        click.echo(
            "Error: Either a COUNT argument or --state-file is required.",
            err=True,
        )
        raise SystemExit(2)

    # --- State-file mode ----------------------------------------------------
    if state_file is not None:
        try:
            state_path = Path(state_file)
            raw = state_path.read_text(encoding="utf-8")
            state: dict = json.loads(raw)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as exc:
            click.echo(f"Error: Failed to read state file {state_file}: {exc}", err=True)
            raise SystemExit(2) from exc

        if not isinstance(state.get("tasks"), list):
            click.echo(
                f"Error: State file {state_file} is missing a 'tasks' array.",
                err=True,
            )
            raise SystemExit(2)

        task_count = len(state["tasks"])
        if task_count < 1 or task_count > 100:
            click.echo(
                f"Error: Task count {task_count} in state file is out of range (1-100).",
                err=True,
            )
            raise SystemExit(2)

        try:
            uuids = generate(task_count)
        except ValueError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(2) from exc
        except Exception as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1) from exc

        # Assign each UUID to the corresponding task's id field
        for task, uid in zip(state["tasks"], uuids):
            task["id"] = uid  # type: ignore[typeddict-unknown-key]

        # Atomic write-back using tempfile + os.replace
        try:
            fd, tmp_path_str = tempfile.mkstemp(
                dir=str(state_path.parent),
                prefix=f".{state_path.name}.",
                suffix=".tmp",
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
                f.write("\n")
            os.replace(tmp_path_str, str(state_path))
        except (OSError, PermissionError) as exc:
            # Clean up temp file if it still exists
            try:
                if tmp_path_str and Path(tmp_path_str).exists():
                    Path(tmp_path_str).unlink()
            except OSError:
                pass
            click.echo(
                f"Error: Failed to write state file {state_file}: {exc}",
                err=True,
            )
            raise SystemExit(2) from exc

        # Output UUID array to stdout for backward compatibility
        click.echo(json.dumps(uuids))
        return

    # --- Count mode (existing behaviour) ------------------------------------
    if count is None:
        # Guard — should be unreachable due to the checks above, but keeps
        # the type checker happy.
        click.echo("Error: COUNT argument is required.", err=True)
        raise SystemExit(2)

    try:
        uuids = generate(count)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(json.dumps(uuids))


if __name__ == "__main__":  # pragma: no cover
    main()
