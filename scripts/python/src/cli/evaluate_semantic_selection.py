"""Emit deterministic release-gate results for semantic skill selection."""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.semantic_selection_evaluation.core import (
    EvaluationError,
    evaluate_fixture,
    load_fixture,
    load_responses,
)


@click.command(name="evaluate-semantic-selection")
@click.argument("fixture", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    show_default=True,
)
@click.option(
    "--mode",
    type=click.Choice(["deterministic", "configured-llm"]),
    default="deterministic",
    show_default=True,
)
@click.option(
    "--responses",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
)
@click.option("--provider", default=None)
@click.option("--model", default=None)
@click.option("--host", default=None)
def main(
    fixture: Path,
    root: Path,
    mode: str,
    responses: Path | None,
    provider: str | None,
    model: str | None,
    host: str | None,
) -> None:
    """Evaluate FIXTURE and print one JSON release-gate report."""
    try:
        result = evaluate_fixture(
            load_fixture(fixture),
            root=root,
            mode=mode,
            responses=load_responses(responses) if responses else None,
            provider=provider,
            model=model,
            host=host,
        )
    except (EvaluationError, OSError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    click.echo(json.dumps(result, sort_keys=True))


if __name__ == "__main__":  # pragma: no cover
    main()
