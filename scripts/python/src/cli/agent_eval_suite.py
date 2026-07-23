#!/usr/bin/env python3
"""CLI for Inspect AI and Terminal-Bench agent evaluations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from lib.agent_eval_suite import (
    DEFAULT_INSPECT_TASK_PATH,
    preflight_frameworks,
    run_inspect_eval,
)
from lib.agent_eval_suite import (
    list_cases as list_eval_cases,
)
from lib.agent_eval_suite import (
    run_terminal_bench as run_terminal_bench_eval,
)
from lib.agent_eval_suite import (
    write_inspect_task as write_inspect_task_file,
)


@click.command(name="agent-eval-suite")
@click.option("--list-cases", is_flag=True, help="Print bundled Inspect cases.")
@click.option(
    "--write-inspect-task",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_INSPECT_TASK_PATH,
    show_default=True,
    help="Write the generated Inspect AI task module to this path.",
)
@click.option(
    "--run-inspect",
    is_flag=True,
    help="Run inspect eval after writing the task file.",
)
@click.option(
    "--inspect-model",
    help="Inspect model id, e.g. openai/gpt-4o or ollama/model.",
)
@click.option(
    "--inspect-log-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Optional Inspect log directory.",
)
@click.option("--inspect-limit", type=int, help="Optional Inspect sample limit.")
@click.option(
    "--run-terminal-bench",
    is_flag=True,
    help="Run Terminal-Bench via tb run.",
)
@click.option(
    "--tb-agent",
    default="opencode",
    show_default=True,
    help="Terminal-Bench agent.",
)
@click.option(
    "--tb-agent-import-path",
    help="Terminal-Bench custom agent import path.",
)
@click.option(
    "--tb-agent-kwarg",
    multiple=True,
    help="Additional Terminal-Bench agent kwarg as key=value. Repeatable.",
)
@click.option("--tb-model", help="Terminal-Bench model id.")
@click.option(
    "--tb-dataset",
    default="terminal-bench-core==0.1.1",
    show_default=True,
    help="Terminal-Bench dataset spec.",
)
@click.option(
    "--tb-output-path",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("/tmp/opencode/terminal-bench-runs"),
    show_default=True,
    help="Terminal-Bench output directory.",
)
@click.option(
    "--tb-task-id",
    multiple=True,
    help="Terminal-Bench task id/glob. Repeatable.",
)
@click.option("--tb-n-tasks", type=int, help="Limit Terminal-Bench task count.")
@click.option("--tb-n-concurrent", type=int, default=1, show_default=True)
@click.option("--tb-no-rebuild", is_flag=True, help="Pass --no-rebuild to tb run.")
@click.option("--tb-no-cleanup", is_flag=True, help="Pass --no-cleanup to tb run.")
def main(
    list_cases: bool,
    write_inspect_task: Path,
    run_inspect: bool,
    inspect_model: str | None,
    inspect_log_dir: Path | None,
    inspect_limit: int | None,
    run_terminal_bench: bool,
    tb_agent: str,
    tb_agent_import_path: str | None,
    tb_agent_kwarg: tuple[str, ...],
    tb_model: str | None,
    tb_dataset: str,
    tb_output_path: Path,
    tb_task_id: tuple[str, ...],
    tb_n_tasks: int | None,
    tb_n_concurrent: int,
    tb_no_rebuild: bool,
    tb_no_cleanup: bool,
) -> None:
    """Run OpenCode-focused evals, including generic worker contract cases."""
    try:
        status = preflight_frameworks()
    except Exception as exc:
        click.echo(f"Error: framework preflight failed: {exc}", err=True)
        raise SystemExit(2) from exc

    output: dict[str, Any] = {"frameworks": status.__dict__}

    if list_cases:
        output["cases"] = list_eval_cases()

    try:
        inspect_task_path = write_inspect_task_file(write_inspect_task)
    except Exception as exc:
        click.echo(f"Error: failed to write Inspect task: {exc}", err=True)
        raise SystemExit(2) from exc
    output["inspect_task"] = str(inspect_task_path)

    if run_inspect:
        if inspect_model is None:
            click.echo("Error: --run-inspect requires --inspect-model.", err=True)
            raise SystemExit(2)
        result = run_inspect_eval(
            inspect_task_path,
            inspect_model,
            log_dir=inspect_log_dir,
            limit=inspect_limit,
        )
        output["inspect"] = _completed_process_output(
            result.returncode,
            result.stdout,
            result.stderr,
        )
        if result.returncode != 0:
            click.echo(json.dumps(output, indent=2))
            raise SystemExit(result.returncode)

    if run_terminal_bench:
        if tb_model is None:
            click.echo("Error: --run-terminal-bench requires --tb-model.", err=True)
            raise SystemExit(2)
        result = run_terminal_bench_eval(
            agent=tb_agent,
            agent_import_path=tb_agent_import_path,
            agent_kwargs=tb_agent_kwarg,
            model=tb_model,
            dataset=tb_dataset,
            output_path=tb_output_path,
            task_ids=tb_task_id,
            n_tasks=tb_n_tasks,
            n_concurrent=tb_n_concurrent,
            no_rebuild=tb_no_rebuild,
            no_cleanup=tb_no_cleanup,
        )
        output["terminal_bench"] = _completed_process_output(
            result.returncode,
            result.stdout,
            result.stderr,
        )
        if result.returncode != 0:
            click.echo(json.dumps(output, indent=2))
            raise SystemExit(result.returncode)

    click.echo(json.dumps(output, indent=2))


def _completed_process_output(
    returncode: int,
    stdout: str,
    stderr: str,
) -> dict[str, object]:
    """Return a stable JSON representation of a subprocess result."""
    return {"returncode": returncode, "stdout": stdout, "stderr": stderr}


if __name__ == "__main__":  # pragma: no cover
    main()
