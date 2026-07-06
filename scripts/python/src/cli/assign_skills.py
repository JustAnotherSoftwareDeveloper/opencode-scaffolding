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
    DEFAULT_BACKEND,
    DEFAULT_CLASSES,
    DEFAULT_FLOOR,
    DEFAULT_MIN,
    DEFAULT_THRESHOLD,
    DEFAULT_WEIGHTS,
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
    "--backend",
    type=click.Choice(["weighted", "flashrank"]),
    default=DEFAULT_BACKEND,
    show_default=True,
    help="Assignment backend. Weighted is deterministic and dependency-light.",
)
@click.option(
    "--floor",
    type=float,
    default=DEFAULT_FLOOR,
    show_default=True,
    help="FlashRank-only minimum raw logit score for skill inclusion.",
)
@click.option(
    "--threshold",
    type=float,
    default=DEFAULT_THRESHOLD,
    show_default=True,
    help="Weighted-backend minimum score for skill inclusion.",
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
    help="FlashRank-only cross-encoder model name.",
)
@click.option(
    "--weight-keyword-overlap",
    type=float,
    default=DEFAULT_WEIGHTS["keyword_overlap"],
    show_default=True,
    help="Weighted-backend keyword overlap weight.",
)
@click.option(
    "--weight-class-match",
    type=float,
    default=DEFAULT_WEIGHTS["class_match"],
    show_default=True,
    help="Weighted-backend class match weight.",
)
@click.option(
    "--weight-tag-similarity",
    type=float,
    default=DEFAULT_WEIGHTS["tag_similarity"],
    show_default=True,
    help="Weighted-backend tag similarity weight.",
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
    backend: str,
    floor: float,
    threshold: float,
    min_skills: int,
    skill_classes: str,
    model_name: str,
    weight_keyword_overlap: float,
    weight_class_match: float,
    weight_tag_similarity: float,
    skills_json: str | None,
) -> None:
    """Populate skills on each task draft.

    The default weighted backend scores lexical and metadata overlap. The
    legacy FlashRank backend remains available with --backend flashrank.
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

    skill_class_tup: tuple[SkillClass, ...] = tuple(SkillClass(c) for c in class_list)

    # --- Validate scoring options and min_skills ---
    if floor < 0:
        click.echo(f"Error: floor must be >= 0, got {floor}", err=True)
        raise SystemExit(2)
    if threshold < 0:
        click.echo(f"Error: threshold must be >= 0, got {threshold}", err=True)
        raise SystemExit(2)
    if min_skills < 1:
        click.echo(f"Error: min-skills must be >= 1, got {min_skills}", err=True)
        raise SystemExit(2)
    weights = {
        "keyword_overlap": weight_keyword_overlap,
        "class_match": weight_class_match,
        "tag_similarity": weight_tag_similarity,
    }
    if any(value < 0 for value in weights.values()):
        click.echo("Error: weights must be >= 0", err=True)
        raise SystemExit(2)
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        click.echo("Error: weights must sum to 1.0", err=True)
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
            backend=backend,
            floor=floor,
            threshold=threshold,
            min_skills=min_skills,
            skill_classes=skill_class_tup,
            model_name=model_name,
            weights=weights,
        )
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except RuntimeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()
