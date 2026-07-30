"""Offline unit tests for dynamic planning-class selection."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

import lib.select_planning_skills.core as core
from lib.generate_task_json.ranker import (
    ScoreResult,
    SkillCandidate,
    SkillRankingInputError,
)
from lib.select_planning_skills.policy import PlanningSelectionPolicy


def policy(
    *, threshold: float = 0.5, minimum: int = 0, maximum: int = 3
) -> PlanningSelectionPolicy:
    return PlanningSelectionPolicy(threshold, minimum, maximum)


def write_skill(
    root: Path, name: str, skill_class: str = "planning", body: str = "body"
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        f"---\nname: {name}\n"
        f"description: {name} description\n"
        "tags: [planning, context, reference, selection]\n"
        f"class: {skill_class}\n---\n{body}\n",
        encoding="utf-8",
    )
    return skill_file


class InjectedScorer:
    def __init__(self, scores: Sequence[float] | Exception) -> None:
        self.scores = scores
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
        self.calls.append((query, tuple(documents)))
        if isinstance(self.scores, Exception):
            raise self.scores
        return [ScoreResult(score) for score in self.scores]


def select(
    project: Path,
    config: Path,
    scorer: InjectedScorer,
    selection_policy: PlanningSelectionPolicy | None = None,
    **kwargs: Any,
) -> tuple[str, ...]:
    return core.select_planning_skills(
        "Plan the requested change.",
        scorer,
        project_root=project,
        config_dir=config,
        policy=selection_policy or policy(),
        **kwargs,
    )


def test_project_precedes_global_and_nonplanning_skills_are_filtered(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    write_skill(project / ".opencode" / "skills", "shared", body="project body")
    write_skill(config / "skills", "shared", body="global body")
    write_skill(project / ".opencode" / "skills", "generic-analysis", "operation")
    write_skill(project / ".opencode" / "skills", "proposal", "operation")
    write_skill(project / ".opencode" / "skills", "plan", "operation")
    write_skill(
        project / ".opencode" / "skills", "operation-counterexample", "operation"
    )

    scorer = InjectedScorer([0.9])
    assert select(project, config, scorer) == ("shared",)
    assert len(scorer.calls) == 1
    assert "shared description" in scorer.calls[0][1][0]
    assert "global body" not in scorer.calls[0][1][0]


def test_current_planning_skills_are_selected_but_policy_skills_are_not(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    root = project / ".opencode" / "skills"
    write_skill(root, "skill-architect")
    write_skill(root, "planning-pipeline-architecture")
    for name in ("generic-analysis", "proposal", "plan"):
        write_skill(root, name, "operation")
    scorer = InjectedScorer([0.9, 0.8])
    assert select(project, tmp_path / "config", scorer) == (
        "planning-pipeline-architecture",
        "skill-architect",
    )


def test_additions_and_removals_are_snapshotted_afresh_each_call(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    root = project / ".opencode" / "skills"
    write_skill(root, "first")
    scorer = InjectedScorer([0.9])
    assert select(project, config, scorer) == ("first",)
    (root / "first" / "SKILL.md").unlink()
    write_skill(root, "second")
    scorer = InjectedScorer([0.9])
    assert select(project, config, scorer) == ("second",)


def test_discovery_is_called_once_per_selector_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    write_skill(project / ".opencode" / "skills", "one")
    original = core.discover_all_skills
    calls = 0

    def discover(*_args: Any, **_kwargs: Any) -> None:
        nonlocal calls
        calls += 1
        original(*_args, **_kwargs)

    monkeypatch.setattr(core, "discover_all_skills", discover)
    assert select(project, config, InjectedScorer([0.8])) == ("one",)
    assert calls == 1


def test_candidate_body_is_never_sent_to_scorer(tmp_path: Path) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    write_skill(
        project / ".opencode" / "skills", "context-skill", body="SECRET-CANDIDATE-BODY"
    )
    scorer = InjectedScorer([0.8])
    select(project, config, scorer)
    assert "SECRET-CANDIDATE-BODY" not in scorer.calls[0][1][0]


@pytest.mark.parametrize(
    ("scores", "minimum", "expected"),
    [
        ([0.2], 0, ()),
        ([0.8], 1, ("one",)),
        ([0.9, 0.8, 0.7, 0.6], 0, ("four", "one", "three")),
    ],
)
def test_zero_one_and_multiple_policy_results(
    tmp_path: Path, scores: list[float], minimum: int, expected: tuple[str, ...]
) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    for name in ("one", "two", "three", "four")[: len(scores)]:
        write_skill(project / ".opencode" / "skills", name)
    assert (
        select(
            project,
            config,
            InjectedScorer(scores),
            selection_policy=policy(minimum=minimum),
        )
        == expected
    )


def test_minimum_one_fails_when_no_result_qualifies(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write_skill(project / ".opencode" / "skills", "one")
    with pytest.raises(SkillRankingInputError, match="minimum"):
        select(project, tmp_path / "config", InjectedScorer([0.1]), policy(minimum=1))


def test_deterministic_score_ties_use_discovery_order(tmp_path: Path) -> None:
    project = tmp_path / "project"
    root = project / ".opencode" / "skills"
    write_skill(root, "alpha")
    write_skill(root, "beta")
    assert select(project, tmp_path / "config", InjectedScorer([0.8, 0.8])) == (
        "alpha",
        "beta",
    )


def test_duplicate_reconciliation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = make_candidate(tmp_path, "duplicate", 0)

    def snapshot(*_args: object, **_kwargs: object) -> tuple[SkillCandidate, ...]:
        return candidate, candidate

    monkeypatch.setattr(core, "_candidate_snapshot", snapshot)
    with pytest.raises(RuntimeError, match="reconciliation"):
        select(tmp_path, tmp_path / "config", InjectedScorer([0.9, 0.8]))


def test_unknown_reconciliation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class ChangingName:
        original_index = 0
        path = tmp_path / "candidate" / "SKILL.md"
        description = "description"
        tags = ("planning",)
        skill_class = "planning"
        source = "project"
        _calls = 0

        @property
        def name(self) -> str:
            self._calls += 1
            return "known" if self._calls <= 3 else "unknown"

    candidate = ChangingName()

    def snapshot(*_args: object, **_kwargs: object) -> tuple[ChangingName, ...]:
        return (candidate,)

    monkeypatch.setattr(core, "_candidate_snapshot", snapshot)
    with pytest.raises(RuntimeError, match="reconciliation"):
        select(tmp_path, tmp_path / "config", InjectedScorer([0.9]))


def make_candidate(tmp_path: Path, name: str, index: int) -> SkillCandidate:
    path = write_skill(tmp_path, name)
    return SkillCandidate.from_metadata(
        {
            "name": name,
            "description": "description",
            "tags": ["planning", "context", "reference", "selection"],
            "class": "planning",
            "source": "project",
            "path": str(path),
        },
        original_index=index,
        approved_roots=[tmp_path],
        allowed_classes=("planning",),
    )


def test_discovery_preflight_and_scoring_failures_are_wrapped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    write_skill(project / ".opencode" / "skills", "one")

    def broken_discovery(*_args: object, **_kwargs: object) -> None:
        raise OSError("scan")

    monkeypatch.setattr(core, "discover_all_skills", broken_discovery)
    with pytest.raises(OSError, match="scan"):
        select(project, tmp_path / "config", InjectedScorer([0.8]))

    monkeypatch.undo()

    def broken_preflight(_prompt: str) -> None:
        raise ValueError("preflight")

    with pytest.raises(ValueError, match="preflight"):
        select(
            project,
            tmp_path / "config",
            InjectedScorer([0.8]),
            preflight=broken_preflight,
        )
    with pytest.raises(RuntimeError, match="scoring"):
        select(project, tmp_path / "config", InjectedScorer(RuntimeError("offline")))


def test_empty_inventory_and_invalid_preflight_type(tmp_path: Path) -> None:
    with pytest.raises(SkillRankingInputError, match="no planning candidates"):
        select(
            tmp_path / "project",
            tmp_path / "config",
            InjectedScorer([]),
            policy(minimum=1),
        )
    project = tmp_path / "project"
    write_skill(project / ".opencode" / "skills", "one")
    with pytest.raises(TypeError, match="callable"):
        select(project, tmp_path / "config", InjectedScorer([0.8]), preflight="bad")
