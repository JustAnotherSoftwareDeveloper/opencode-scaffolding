"""FlashRank-based skill assignment — render, rerank, select.

Consumers: :mod:`cli.assign_skills`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.collect_skills.discovery import discover_all_skills
from lib.collect_skills.models import Skill, SkillIndex
from lib.shared.schema import validate_json_schema
from lib.shared.skill_class import SkillClass

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_FLOOR = 0.0  # raw cross-encoder logit — 0.0 = even odds
DEFAULT_MIN = 1
DEFAULT_CLASSES: tuple[SkillClass, ...] = (
    SkillClass.OPERATION,
    SkillClass.DOCUMENTATION,
)


# ---------------------------------------------------------------------------
# Helpers — render skill + task draft into text passages
# ---------------------------------------------------------------------------


def render_skill(skill: Skill) -> str:
    """Render a skill as a structured text passage for the cross-encoder.

    One field per line so the model can attend to each independently.
    Tags are comma-joined for lexical signal.
    """
    return (
        f"name: {skill.name}\n"
        f"class: {skill.class_}\n"
        f"description: {skill.description}\n"
        f"tags: {', '.join(skill.tags)}\n"
    )


def build_query(
    purpose: str,
    context: str,
    files_to_read: list[str],
    files_to_write: list[str],
) -> str:
    """Build a query string from a TaskDraft's fields."""
    parts = [f"purpose: {purpose}", f"context: {context}"]
    if files_to_read:
        parts.append(f"files to read: {', '.join(files_to_read)}")
    if files_to_write:
        parts.append(f"files to write: {', '.join(files_to_write)}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Reranking
# ---------------------------------------------------------------------------

_ranker_cache: dict[str, object] = {}


def _get_ranker(model_name: str) -> Any:
    """Return a cached FlashRank Reranker instance keyed by *model_name*.

    The ranker is loaded lazily on first call per model and reused across
    drafts for the same model.
    """
    if model_name not in _ranker_cache:
        from rerankers import Reranker  # noqa: PLC0415 — lazy import

        _ranker_cache[model_name] = Reranker(
            model_name=model_name, model_type="flashrank",
        )
    return _ranker_cache[model_name]


def _rank_candidates(
    ranker: Any,
    purpose: str,
    context: str,
    files_to_read: list[str],
    files_to_write: list[str],
    candidates: list[Skill],
) -> tuple[list[str], list[float]]:
    """Rerank all candidate skills against a task draft.

    Returns (skill_names, scores) ordered by relevance descending.
    Scores are raw cross-encoder logits (unbounded upward) obtained by
    inverting FlashRank's sigmoid normalization.
    """
    import numpy as np

    query = build_query(purpose, context, files_to_read, files_to_write)
    skill_texts = [render_skill(s) for s in candidates]
    skill_names = [s.name for s in candidates]

    results = ranker.rank(query=query, docs=skill_texts, doc_ids=skill_names)

    names: list[str] = []
    scores: list[float] = []
    for r in results.results:
        # FlashRank applies sigmoid:  score = 1 / (1 + exp(-logit))
        # Invert:  logit = log(score / (1 - score))
        clamped = float(np.clip(float(r.score), 1e-10, 1 - 1e-10))
        raw_logit = float(np.log(clamped / (1.0 - clamped)))
        names.append(str(r.doc_id))
        scores.append(raw_logit)

    return names, scores


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def _select_skills(
    ranked_names: list[str],
    ranked_scores: list[float],
    floor: float,
    min_skills: int,
) -> tuple[list[str], list[float]]:
    """Select skills from ranked results.

    Takes all above floor, fills to min_skills from below-floor, falls
    back to top rank as last resort.
    """
    above: list[tuple[str, float]] = []
    below: list[tuple[str, float]] = []

    for name, s in zip(ranked_names, ranked_scores, strict=True):
        if s >= floor:
            above.append((name, s))
        else:
            below.append((name, s))

    selected_names: list[str] = [n for n, _ in above]
    selected_scores: list[float] = [s for _, s in above]

    while len(selected_names) < min_skills and below:
        name, s = below.pop(0)
        selected_names.append(name)
        selected_scores.append(s)

    if not selected_names and ranked_names:
        selected_names.append(ranked_names[0])
        selected_scores.append(ranked_scores[0])

    return selected_names, selected_scores


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def assign_skills(
    state_file: str,
    schema_path: str,
    *,
    skills_index: list[dict[str, Any]] | None = None,
    floor: float = DEFAULT_FLOOR,
    min_skills: int = DEFAULT_MIN,
    skill_classes: tuple[SkillClass, ...] = DEFAULT_CLASSES,
    model_name: str = "ms-marco-MiniLM-L-12-v2",
) -> str:
    """Assign skills to each task draft in the state file using FlashRank.

    Args:
        state_file: Path to the ``.tasks/<epoch>-decomposition.json`` file.
        schema_path: Path to the TaskDraft JSON Schema file.
        skills_index: Optional external skill index JSON (auto-discovers if
            ``None``).
        floor: Minimum relevance score for inclusion.
        min_skills: Minimum skills per task (always satisfied).
        skill_classes: SkillClass values to consider as candidates.
        model_name: FlashRank cross-encoder model name.

    Returns:
        The *state_file* path (same as input).
    """
    # --- Load state ---
    raw = Path(state_file).read_text(encoding="utf-8")
    state: dict[str, Any] = json.loads(raw)

    # --- Validate against TaskDraft schema ---
    schema_raw = Path(schema_path).read_text(encoding="utf-8")
    schema: dict[str, Any] = json.loads(schema_raw)
    errors = validate_json_schema(state, schema)
    if errors:
        raise ValueError(
            f"state file failed TaskDraft schema: {errors}"
        )

    drafts: list[dict[str, Any]] = state.get("tasks", [])

    # --- Discover skills ---
    if skills_index is not None:
        all_skills = _parse_skills_from_index(skills_index)
        skills_source = "external"
    else:
        all_skills = _discover_skills()
        skills_source = "auto"

    # --- Filter by class ---
    allowed = set(skill_classes)
    candidates = [s for s in all_skills if s.class_ in allowed]

    if not candidates:
        raise RuntimeError(
            f"No skills found for classes {skill_classes}"
            f" (searched {len(all_skills)} total, source: {skills_source})"
        )

    # --- Rerank and select ---
    ranker = _get_ranker(model_name)
    output_tasks: list[dict[str, Any]] = []
    summary_lines: list[str] = []

    for i, draft in enumerate(drafts):
        purpose: str = draft.get("purpose", "")
        context: str = draft.get("context", "")
        files_to_read: list[str] = draft.get("filesToRead", [])
        files_to_write: list[str] = draft.get("filesToWrite", [])

        ranked_names, ranked_scores = _rank_candidates(
            ranker, purpose, context, files_to_read, files_to_write, candidates,
        )
        names, scores = _select_skills(
            ranked_names, ranked_scores, floor, min_skills,
        )

        task_out: dict[str, Any] = {**draft, "skills": names}
        output_tasks.append(task_out)

        n_summary = ", ".join(
            f"{n}({round(s, 2)})" for n, s in zip(names, scores, strict=True)
        )
        summary_lines.append(f"task_{i + 1}: [{n_summary}]")

    # --- Write ---
    state["tasks"] = output_tasks
    _write_json_atomic(state_file, state)

    # --- Summary ---
    skill_counts = [len(t["skills"]) for t in output_tasks]
    summary: dict[str, object] = {
        "tasks_assigned": len(output_tasks),
        "skills_per_task": {
            "min": min(skill_counts) if skill_counts else 0,
            "max": max(skill_counts) if skill_counts else 0,
            "avg": round(sum(skill_counts) / len(skill_counts), 2)
            if skill_counts
            else 0,
        },
        "skill_class_filter": [c.value for c in skill_classes],
        "skills_source": skills_source,
        "model": model_name,
        "candidates_considered": len(candidates),
        "details": summary_lines,
    }
    print(json.dumps(summary, indent=2))

    return state_file


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_skills_from_index(raw_index: list[dict[str, Any]]) -> list[Skill]:
    """Parse an external skills JSON array into Skill instances."""
    skills: list[Skill] = []
    for entry in raw_index:
        skills.append(
            Skill(
                name=entry.get("name", ""),
                description=entry.get("description", ""),
                tags=entry.get("tags", []),
                class_=entry.get("class", ""),
                version=entry.get("version", ""),
                license=entry.get("license", ""),
                compatibility=entry.get("compatibility", ""),
                metadata=entry.get("metadata", {}),
                location=entry.get("path", ""),
                source=entry.get("source", ""),
                permission=entry.get("permission", ""),
            )
        )
    return skills


def _discover_skills() -> list[Skill]:
    """Discover all skills from standard search roots."""
    index = SkillIndex()
    discover_all_skills(index, verbose=False)
    return index.resolve()


def _write_json_atomic(path: str, data: dict[str, Any]) -> None:
    """Write JSON to *path* atomically via temp file + rename."""
    import contextlib
    import os
    import tempfile

    dst = Path(path)
    parent = dst.parent
    tmp_dir = parent if parent.exists() and parent.is_dir() else None

    fd, tmp_path = tempfile.mkstemp(
        dir=str(tmp_dir) if tmp_dir else None,
        prefix=f".{dst.name}.tmp_",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp_path, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise
