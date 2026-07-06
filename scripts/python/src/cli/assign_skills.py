"""CLI entry point for assign-skills — populate skills on task drafts.

This script is invoked as:
  uv run --directory <scripts-python-dir> assign-skills \\
      --state-file <path> --schema <path> [options]

Exit codes:
   0 — Success, skills populated and state file written.
   1 — Runtime error (no matching skills, discovery failure).
   2 — User error (invalid args, schema validation failure).
"""

from __future__ import annotations

import click

from lib.assign_skills.core import (
    DEFAULT_CLASSES,
    DEFAULT_FLOOR,
    DEFAULT_MIN,
    assign_skills,
)
from lib.shared.skill_class import SkillClass

VALID_CLASS_NAMES = [c.value for c in SkillClass]


@click.command(name="assign-skills")
@click.option(
    "--state-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help="Path to the .tasks/<epoch>-decomposition.json state file.",
)
@click.option(
    "--schema",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help="Path to the TaskDraft JSON Schema file.",
)
@click.option(
    "--floor",
    type=float,
    default=DEFAULT_FLOOR,
    show_default=True,
    help="Minimum relevance score (raw logit) for skill inclusion.",
)
@click.option(
    "--min-skills",
    type=int,
    default=DEFAULT_MIN,
    show_default=True,
    help="Minimum skills per task (always satisfied).",
)
@click.option(
    "--skill-classes",
    type=str,
    default=",".join(c.value for c in DEFAULT_CLASSES),
    show_default=True,
    help="Comma-separated SkillClass values to consider as candidates.",
)
@click.option(
    "--model-name",
    type=str,
    default="ms-marco-MiniLM-L-12-v2",
    show_default=True,
    help="FlashRank cross-encoder model name.",
)
@click.option(
    "--skills-json",
    type=str,
    default=None,
    help="External skill index JSON (auto-discovers if omitted).",
)
def main(
    state_file: str,
    schema: str,
    floor: float,
    min_skills: int,
    skill_classes: str,
    model_name: str,
    skills_json: str | None,
) -> None:
    """Populate skills on each task draft using a FlashRank cross-encoder.

    Discovers skills, renders them as text passages, reranks against each
    draft, and selects skills above the floor threshold.
    """
    # --- Parse skill classes ---
    class_list: list[str] = [c.strip() for c in skill_classes.split(",") if c.strip()]
    invalid = [c for c in class_list if c not in VALID_CLASS_NAMES]
    if invalid:
        click.echo(
            f"Error: invalid class names: {', '.join(invalid)}. "
            f"Valid: {', '.join(VALID_CLASS_NAMES)}",
            err=True,
        )
        raise SystemExit(2)

    skill_class_tup: tuple[SkillClass, ...] = tuple(
        SkillClass(c) for c in class_list
    )

    # --- Validate floor and min_skills ---
    if floor < 0:
        click.echo(f"Error: floor must be >= 0, got {floor}", err=True)
        raise SystemExit(2)
    if min_skills < 1:
        click.echo(f"Error: min-skills must be >= 1, got {min_skills}", err=True)
        raise SystemExit(2)

    # --- Parse external skills if provided ---
    skills_index: list[dict] | None = None
    if skills_json is not None:
        import json

        try:
            skills_index = json.loads(skills_json)
            if not isinstance(skills_index, list):
                click.echo(
                    "Error: --skills-json must be a JSON array.",
                    err=True,
                )
                raise SystemExit(2)
        except json.JSONDecodeError as exc:
            click.echo(f"Error: invalid --skills-json: {exc}", err=True)
            raise SystemExit(2) from exc

    # --- Assign ---
    try:
        assign_skills(
            state_file=state_file,
            schema_path=schema,
            skills_index=skills_index,
            floor=floor,
            min_skills=min_skills,
            skill_classes=skill_class_tup,
            model_name=model_name,
        )
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except RuntimeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()
