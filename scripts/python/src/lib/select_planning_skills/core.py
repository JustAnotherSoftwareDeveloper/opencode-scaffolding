"""Dynamic, planning-only skill selection.

The selector deliberately owns the metadata snapshot for one call.  It never
opens a candidate's ``SKILL.md`` body and never retains the discovered index.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from lib.collect_skills.discovery import discover_all_skills
from lib.collect_skills.models import SkillIndex
from lib.generate_task_json.qwen_prompt import QwenPlanningPromptRenderer
from lib.generate_task_json.ranker import (
    PairScorer,
    ScoreResult,
    SkillCandidate,
    SkillRankingInputError,
)
from lib.select_planning_skills.policy import (
    PlanningSelectionPolicy,
    stable_order_key,
)
from lib.select_planning_skills.prompt import PLANNING_INSTRUCTION


def _approved_roots(
    project_root: Path, config_dir: Path, extra_paths: Sequence[Path]
) -> dict[str, tuple[Path, ...]]:
    """Return roots matching the collector's source labels."""
    project = tuple(
        root
        for root in (
            project_root / ".opencode" / "skills",
            project_root / ".claude" / "skills",
            project_root / ".agents" / "skills",
        )
    )
    global_ = tuple(
        root
        for root in (
            config_dir / "skills",
            config_dir.parent / ".claude" / "skills",
            config_dir.parent / ".agents" / "skills",
        )
    )
    return {"project": project, "global": global_, "extra": tuple(extra_paths)}


def _candidate_snapshot(
    index: SkillIndex,
    *,
    project_root: Path,
    config_dir: Path,
    extra_paths: Sequence[Path],
) -> tuple[SkillCandidate, ...]:
    roots = _approved_roots(project_root, config_dir, extra_paths)
    records = index.filter_by_classes(("planning",))
    return tuple(
        SkillCandidate.from_metadata(
            record.to_dict(),
            original_index=position,
            approved_sources=("project", "global", "extra"),
            approved_source_roots=roots,
            allowed_classes=("planning",),
        )
        for position, record in enumerate(records)
    )


def select_planning_skills(
    description: str,
    scorer: PairScorer,
    *,
    project_root: Path | None = None,
    config_dir: Path | None = None,
    extra_paths: Sequence[Path] = (),
    policy: PlanningSelectionPolicy,
    token_budget: Any | None = None,
    preflight: Any | None = None,
) -> tuple[str, ...]:
    """Discover, score, and return canonical planning skill names.

    ``scorer`` is an already verified pair scorer.  A caller may provide a
    ``preflight`` callable for an additional transport-specific check; the
    renderer always performs token preflight when ``token_budget`` is given.
    """
    if not isinstance(description, str) or not description.strip():
        raise SkillRankingInputError("planning description must be a non-empty string")
    if not isinstance(policy, PlanningSelectionPolicy):
        raise TypeError("policy must be a PlanningSelectionPolicy")
    root = project_root or Path.cwd()
    config = config_dir or Path.home() / ".config" / "opencode"
    extras = tuple(Path(item) for item in extra_paths)

    index = SkillIndex()
    discover_all_skills(
        index,
        project_root=root,
        config_dir=config,
        extra_paths=list(extras),
    )
    candidates = _candidate_snapshot(
        index, project_root=root, config_dir=config, extra_paths=extras
    )
    if not candidates:
        if policy.minimum_cardinality:
            raise SkillRankingInputError("no planning candidates are available")
        return ()

    renderer = QwenPlanningPromptRenderer(
        token_budget, instruction=PLANNING_INSTRUCTION
    )
    query = renderer.render(description, candidates[0]).task
    documents: list[str] = []
    for candidate in candidates:
        rendered = renderer.render(description, candidate)
        documents.append(rendered.skill)
        if preflight is not None:
            if not callable(preflight):
                raise TypeError("preflight must be callable")
            preflight(rendered.prompt)

    try:
        results = scorer.score(query, tuple(documents))
    except Exception as exc:
        raise RuntimeError("planning pair scoring failed") from exc
    if not isinstance(results, list) or len(results) != len(candidates):
        raise RuntimeError("scorer returned the wrong number of planning scores")

    scored: list[tuple[SkillCandidate, ScoreResult]] = []
    for candidate, result in zip(candidates, results, strict=True):
        if (
            not isinstance(result, ScoreResult)
            or not math.isfinite(result.score)
            or not 0 <= result.score <= 1
        ):
            raise RuntimeError("scorer returned an invalid planning score")
        scored.append((candidate, result))
    ordered = sorted(
        scored,
        key=lambda item: stable_order_key(item[1].score, item[0].original_index),
    )
    selected = [
        item[0].name
        for item in ordered
        if item[1].score >= policy.absolute_inclusion_threshold
    ][: policy.max_cardinality]
    if len(selected) < policy.minimum_cardinality:
        raise SkillRankingInputError("planning policy minimum was not satisfied")
    names = tuple(selected)
    canonical = {candidate.name for candidate in candidates}
    if len(names) != len(set(names)) or not set(names) <= canonical:
        raise RuntimeError("planning selection reconciliation failed")
    return names


__all__ = ["select_planning_skills"]
