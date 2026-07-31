"""Offline contract tests for the deterministic ranker and prompt renderer."""

# Exact prompt fixtures intentionally remain byte-oriented.
# ruff: noqa: E501

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from pathlib import Path

import pytest

from lib.generate_task_json.qwen_prompt import (
    ASSISTANT_SUFFIX,
    INSTRUCTION,
    PLANNING_INSTRUCTION,
    PLANNING_PROMPT_VERSION,
    PLANNING_RENDER_VERSION,
    SYSTEM_PREFIX,
    QwenPlanningPromptRenderer,
    QwenPromptRenderer,
    QwenTokenBudget,
    compose_qwen_prompt,
    render_planning_request,
)
from lib.generate_task_json.qwen_prompt import (
    render_skill as render_prompt_skill,
)
from lib.generate_task_json.qwen_prompt import (
    render_task as render_prompt_task,
)
from lib.generate_task_json.ranker import (
    RankingPolicy,
    ScoreResult,
    SkillCandidate,
    SkillRanker,
    SkillRankingConfigurationError,
    SkillRankingInputError,
    SkillRankingRuntimeError,
    render_skill,
    render_task,
)
from lib.shared.skill_class import SkillClass
from lib.shared.skill_routing import RoutingCue, RoutingRelationship

ROOT = Path(__file__).parents[1]
TOKENIZER = ROOT / "src/lib/generate_task_json/assets/tokenizer.json"


def task() -> dict:
    return {
        "purpose": "Write deterministic tests.",
        "context": "The backend must be offline and reproducible.",
        "filesToRead": ["src/ranker.py"],
        "filesToWrite": ["tests/test_ranker.py"],
        "executionInstructions": [
            {"step": 1, "action": "Implement tests.", "verification": "pytest passes"},
            {"step": 2, "action": "Review the fixture."},
        ],
        "expectedOutput": "A complete deterministic test suite.",
        "verification": ["Focused tests pass", "No network is used"],
    }


def candidate(
    tmp_path: Path, name: str = "python-tests", index: int = 0
) -> SkillCandidate:
    path = tmp_path / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\nname: skill\n---\n", encoding="utf-8")
    return SkillCandidate.from_metadata(
        {
            "name": name,
            "description": "Write deterministic Python tests",
            "schema_version": "1.0",
            "cues": [
                {"facet": "operation", "value": "write-tests", "primary": True},
                {"facet": "subject", "value": "python", "aliases": ["py"]},
            ],
            "relationships": [{"role": "owner"}],
            "class": "operation",
            "source": "project",
            "path": str(path),
        },
        original_index=index,
        approved_roots=[tmp_path],
    )


class FakeScorer:
    def __init__(self, scores: list[float], clipped: tuple[str, ...] = ()) -> None:
        self.scores = scores
        self.clipped = clipped
        self.query = ""
        self.documents: tuple[str, ...] = ()

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
        self.query, self.documents = query, tuple(documents)
        return [ScoreResult(score, self.clipped) for score in self.scores]


def test_rendering_is_complete_and_semantic_only(tmp_path: Path) -> None:
    skill = candidate(tmp_path)
    rendered = render_task(task())
    assert rendered == render_prompt_task(task())
    assert "src/ranker.py" in rendered and "pytest passes" in rendered
    semantic = render_skill(skill)
    assert all(
        value in semantic
        for value in (
            "python-tests",
            "deterministic",
            "python",
            "operation",
            "write-tests",
            "py",
        )
    )
    assert "Routing relationships:\n- role=owner" in semantic
    assert "Routing cues:" in semantic
    assert str(skill.path) not in semantic and skill.source not in semantic


def test_prompt_is_exact_and_excludes_trust_metadata(tmp_path: Path) -> None:
    skill = candidate(tmp_path)
    query = render_prompt_task(task())
    document = render_prompt_skill(skill)
    expected = (
        SYSTEM_PREFIX
        + f"<Instruct>: {INSTRUCTION}\n<Query>: {query}\n<Document>: {document}"
        + ASSISTANT_SUFFIX
    )
    assert compose_qwen_prompt(query, document) == expected
    result = QwenPromptRenderer().render(task(), skill)
    assert result.prompt == expected
    assert str(skill.path) not in result.prompt


def test_planning_request_preserves_complete_description_text() -> None:
    description = "  Plan this change.\n\nInclude every constraint and\tindentation.  "

    assert render_planning_request(description) == f"Planning request: {description}"


@pytest.mark.parametrize("bad", ["", "   ", "\n\t", None, 42])
def test_planning_request_rejects_empty_and_malformed_input(bad: object) -> None:
    with pytest.raises(SkillRankingInputError, match="non-empty string"):
        render_planning_request(bad)  # type: ignore[arg-type]


def test_planning_renderer_includes_metadata_and_excludes_source_and_path(
    tmp_path: Path,
) -> None:
    skill = candidate(tmp_path, "planning-reference")
    result = QwenPlanningPromptRenderer().render(
        "Create an implementation plan.", skill
    )

    assert result.task == "Planning request: Create an implementation plan."
    assert result.skill == (
        "Skill name: planning-reference\n"
        "Description: Write deterministic Python tests\n"
        "Routing relationships:\n- role=owner\n"
        "Routing cues:\n- facet=operation; value=write-tests; primary=true\n- facet=subject; value=python; aliases=py\n"
        "Class: operation"
    )
    assert skill.source not in result.skill
    assert str(skill.path) not in result.skill
    assert PLANNING_INSTRUCTION in result.prompt


def test_planning_renderer_reports_planning_version_identities(tmp_path: Path) -> None:
    result = QwenPlanningPromptRenderer().render(
        "Plan the work.", candidate(tmp_path, "planning-reference")
    )

    assert result.task_render_version == PLANNING_RENDER_VERSION
    assert result.prompt_version == PLANNING_PROMPT_VERSION
    assert result.skill_render_version == "task-skill-routing-signature-v2"


def test_existing_task_rendering_remains_byte_identical() -> None:
    expected = (
        "Purpose: Write deterministic tests.\n"
        "Context: The backend must be offline and reproducible.\n"
        "Files to read: src/ranker.py\n"
        "Files to write: tests/test_ranker.py\n"
        "Execution instructions:\n"
        "1. Implement tests. (Verification: pytest passes)\n"
        "2. Review the fixture.\n"
        "Expected output: A complete deterministic test suite.\n"
        "Verification: Focused tests pass; No network is used"
    )

    assert render_prompt_task(task()) == expected


def test_pinned_tokenizer_accepts_limit_and_rejects_overflow() -> None:
    budget = QwenTokenBudget(TOKENIZER)
    prompts = {
        count: _complete_prompt_with_exact_tokens(budget, count)
        for count in (4757, 8192, 8193)
    }
    assert budget.preflight(prompts[4757]).token_count == 4757
    assert budget.preflight(prompts[8192]).token_count == 8192
    with pytest.raises(SkillRankingInputError, match="exceeds 8192"):
        budget.preflight(prompts[8193])


def _complete_prompt_with_exact_tokens(
    budget: QwenTokenBudget,
    target: int,
) -> str:
    low = 0
    high = target * 2
    while low <= high:
        middle = (low + high) // 2
        value = task()
        value["filesToRead"] = [" x" * middle]
        prompt = (
            QwenPromptRenderer()
            .render(
                value,
                {
                    "name": "python-tests",
                    "description": "Write deterministic Python tests",
                    "cues": (
                        RoutingCue("operation", "write-tests", primary=True),
                        RoutingCue("subject", "python", ("py",)),
                    ),
                    "relationships": (RoutingRelationship("owner"),),
                    "skill_class": "operation",
                },
            )
            .prompt
        )
        count = budget.count(prompt)
        if count == target:
            return prompt
        if count < target:
            low = middle + 1
        else:
            high = middle - 1
    raise AssertionError(f"cannot construct a {target}-token fixture")


@pytest.mark.parametrize("bad", [[], (), "skills"])
def test_inventory_rejects_empty_or_non_sequence(bad: object) -> None:
    with pytest.raises(SkillRankingInputError, match="non-empty"):
        SkillRanker(FakeScorer([0])).rank(task(), bad)  # type: ignore[arg-type]


def test_inventory_rejects_duplicates_and_bounds(tmp_path: Path) -> None:
    one = candidate(tmp_path)
    with pytest.raises(SkillRankingInputError, match="duplicate"):
        SkillRanker(FakeScorer([0.5, 0.5])).rank(task(), [one, one])
    with pytest.raises(SkillRankingInputError, match="candidate limit"):
        SkillRanker(FakeScorer([0.5]), max_candidates=1).rank(
            task(), [one, candidate(tmp_path, "second", 1)]
        )


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", "Not Canonical"),
        ("name", " valid-name"),
        ("description", ""),
        ("cues", []),
        ("class", "planning"),
        ("source", "unknown"),
    ],
)
def test_candidate_authorization_and_bounds(
    tmp_path: Path, field: str, value: object
) -> None:
    path = tmp_path / "skill" / "SKILL.md"
    path.parent.mkdir()
    path.write_text("skill", encoding="utf-8")
    metadata = {
        "name": "valid-name",
        "description": "desc",
        "cues": [{"facet": "operation", "value": "write-tests", "primary": True}],
        "relationships": [{"role": "owner"}],
        "class": "operation",
        "source": "project",
        "path": str(path),
    }
    metadata[field] = value
    with pytest.raises(SkillRankingInputError):
        SkillCandidate.from_metadata(metadata, approved_roots=[tmp_path])
    outside = tmp_path.parent / "outside-skill.md"
    outside.write_text("skill", encoding="utf-8")
    metadata["name"] = "valid-name"
    metadata["description"] = "desc"
    metadata["cues"] = [{"facet": "operation", "value": "write-tests", "primary": True}]
    metadata["class"] = "operation"
    metadata["source"] = "project"
    metadata["path"] = str(outside)
    with pytest.raises(SkillRankingInputError, match="outside"):
        SkillCandidate.from_metadata(metadata, approved_roots=[tmp_path])


def test_candidate_source_must_match_its_authorized_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    global_root = tmp_path / "global"
    path = project_root / "skill" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("skill", encoding="utf-8")
    metadata = {
        "name": "valid-name",
        "description": "desc",
        "cues": [{"facet": "operation", "value": "write-tests", "primary": True}],
        "relationships": [{"role": "owner"}],
        "class": "operation",
        "source": "global",
        "path": str(path),
    }
    with pytest.raises(SkillRankingInputError, match="outside"):
        SkillCandidate.from_metadata(
            metadata,
            approved_source_roots={
                "project": (project_root,),
                "global": (global_root,),
            },
        )


def test_old_flat_candidate_metadata_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "skill" / "SKILL.md"
    path.parent.mkdir()
    path.write_text("skill", encoding="utf-8")
    with pytest.raises(SkillRankingInputError, match="structured cues"):
        SkillCandidate.from_metadata(
            {
                "name": "legacy",
                "description": "legacy metadata",
                "tags": ["operation"],
                "class": "operation",
                "source": "project",
                "path": str(path),
            },
            approved_roots=[tmp_path],
        )


@pytest.mark.parametrize(
    "skill_class", [SkillClass.OPERATION.value, SkillClass.DOCUMENTATION.value]
)
def test_candidate_default_classes_remain_authorized(
    tmp_path: Path, skill_class: str
) -> None:
    path = tmp_path / "skill" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("skill", encoding="utf-8")

    candidate = SkillCandidate.from_metadata(
        {
            "name": "valid-name",
            "description": "desc",
            "schema_version": "1.0",
            "cues": [{"facet": "operation", "value": "write-tests", "primary": True}],
            "relationships": [{"role": "owner"}],
            "class": skill_class,
            "source": "project",
            "path": str(path),
        },
        approved_roots=[tmp_path],
    )

    assert candidate.skill_class == skill_class
    assert candidate.cues[0].value == "write-tests"


def test_candidate_planning_class_requires_explicit_authorization(
    tmp_path: Path,
) -> None:
    path = tmp_path / "planning" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("skill", encoding="utf-8")
    metadata = {
        "name": "planning-reference",
        "description": "planning context",
        "schema_version": "1.0",
        "cues": [{"facet": "operation", "value": "plan", "primary": True}],
        "relationships": [{"role": "owner"}],
        "class": SkillClass.PLANNING.value,
        "source": "project",
        "path": str(path),
    }

    with pytest.raises(SkillRankingInputError, match="unsupported skill class"):
        SkillCandidate.from_metadata(metadata, approved_roots=[tmp_path])

    candidate = SkillCandidate.from_metadata(
        metadata,
        approved_roots=[tmp_path],
        allowed_classes=(SkillClass.PLANNING.value,),
    )
    assert candidate.skill_class == SkillClass.PLANNING.value
    assert candidate.cues[0].value == "plan"


def test_candidate_resolves_repository_local_facets_after_path_authorization(
    tmp_path: Path,
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "skill-facets.json").write_text(
        json.dumps(
            {
                "namespace": "repo",
                "facets": [
                    {
                        "name": "audience",
                        "meaning": "Audience that changes ownership",
                        "values": [{"value": "operators", "aliases": ["ops team"]}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    path = tmp_path / "skill" / "SKILL.md"
    path.parent.mkdir()
    path.write_text("skill", encoding="utf-8")
    candidate = SkillCandidate.from_metadata(
        {
            "name": "local-routing",
            "description": "Use when routing operations work",
            "schema_version": "1.0",
            "cues": [
                {"facet": "operation", "value": "route", "primary": True},
                {"facet": "repo:audience", "value": "operators"},
            ],
            "relationships": [{"role": "owner"}],
            "class": "operation",
            "source": "project",
            "path": str(path),
        },
        approved_roots=[tmp_path],
    )
    local = next(cue for cue in candidate.cues if cue.facet == "repo:audience")
    assert local.aliases == ("ops team",)


@pytest.mark.parametrize(
    "skill_class",
    [item.value for item in SkillClass if item is not SkillClass.PLANNING],
)
def test_planning_only_candidates_reject_nonplanning_classes(
    tmp_path: Path, skill_class: str
) -> None:
    path = tmp_path / "skill" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("skill", encoding="utf-8")

    with pytest.raises(SkillRankingInputError, match="unsupported skill class"):
        SkillCandidate.from_metadata(
            {
                "name": "valid-name",
                "description": "desc",
                "cues": [{"facet": "operation", "value": "plan", "primary": True}],
                "relationships": [{"role": "owner"}],
                "class": skill_class,
                "source": "project",
                "path": str(path),
            },
            approved_roots=[tmp_path],
            allowed_classes=(SkillClass.PLANNING.value,),
        )


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", "Not Canonical"),
        ("cues", []),
        ("source", "unknown"),
    ],
)
def test_planning_class_authorization_preserves_candidate_controls(
    tmp_path: Path, field: str, value: object
) -> None:
    path = tmp_path / "planning" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("skill", encoding="utf-8")
    metadata = {
        "name": "planning-reference",
        "description": "planning context",
        "cues": [{"facet": "operation", "value": "plan", "primary": True}],
        "relationships": [{"role": "owner"}],
        "class": SkillClass.PLANNING.value,
        "source": "project",
        "path": str(path),
    }
    metadata[field] = value

    with pytest.raises(SkillRankingInputError):
        SkillCandidate.from_metadata(
            metadata,
            approved_roots=[tmp_path],
            allowed_classes=(SkillClass.PLANNING.value,),
        )

    outside = tmp_path.parent / "outside-skill.md"
    outside.write_text("skill", encoding="utf-8")
    metadata.update(
        name="planning-reference",
        cues=[{"facet": "operation", "value": "plan", "primary": True}],
        source="project",
        path=str(outside),
    )
    with pytest.raises(SkillRankingInputError, match="outside"):
        SkillCandidate.from_metadata(
            metadata,
            approved_roots=[tmp_path],
            allowed_classes=(SkillClass.PLANNING.value,),
        )


def test_selection_ties_threshold_clipping_and_low_confidence(tmp_path: Path) -> None:
    skills = [
        candidate(tmp_path, name, index)
        for index, name in enumerate(("first", "second", "third", "fourth"))
    ]
    scorer = FakeScorer([0.8, 0.8, 0.79, 0.1], ("yes",))
    result = SkillRanker(scorer).rank(task(), skills)
    assert result.names == ("first", "second")
    assert result.diagnostics.candidate_scores[0] == ("first", 0.8)
    assert result.diagnostics.clipped_labels == ("yes",) * 4
    low = SkillRanker(FakeScorer([0.2, 0.1])).rank(task(), skills[:2])
    assert low.names == ("first",) and low.diagnostics.forced_low_confidence


def test_legacy_selection_still_forces_one_qualifying_candidate(
    tmp_path: Path,
) -> None:
    skills = [candidate(tmp_path, "first", 0), candidate(tmp_path, "second", 1)]

    result = SkillRanker(FakeScorer([0.2, 0.1])).rank(task(), skills)

    assert result.names == ("first",)
    assert result.diagnostics.forced_low_confidence


def test_optional_selection_can_return_empty_below_absolute_threshold(
    tmp_path: Path,
) -> None:
    skills = [candidate(tmp_path, "first", 0), candidate(tmp_path, "second", 1)]

    result = SkillRanker(FakeScorer([0.79, 0.78])).rank(
        task(),
        skills,
        minimum_cardinality=0,
        absolute_inclusion_threshold=0.8,
    )

    assert result.names == ()
    assert result.diagnostics.selected_names == ()


def test_optional_selection_uses_absolute_threshold_for_each_candidate(
    tmp_path: Path,
) -> None:
    skills = [
        candidate(tmp_path, "first", 0),
        candidate(tmp_path, "second", 1),
        candidate(tmp_path, "third", 2),
    ]

    result = SkillRanker(FakeScorer([0.91, 0.8, 0.79])).rank(
        task(),
        skills,
        minimum_cardinality=0,
        absolute_inclusion_threshold=0.8,
    )

    assert result.names == ("first", "second")


def test_optional_selection_omits_task_owner_file_blocking(tmp_path: Path) -> None:
    skills = [
        candidate(tmp_path, "proposal", 0),
        candidate(tmp_path, "skill-authoring-guide", 1),
    ]
    value = task()
    value["filesToWrite"] = ["skills/proposal/SKILL.md"]

    result = SkillRanker(FakeScorer([0.99, 0.9])).rank(
        value,
        skills,
        minimum_cardinality=0,
        absolute_inclusion_threshold=0.8,
        selection_blocking=False,
    )

    assert result.names == ("proposal", "skill-authoring-guide")


def test_optional_selection_preserves_original_order_for_score_ties(
    tmp_path: Path,
) -> None:
    skills = [
        candidate(tmp_path, "later", 8),
        candidate(tmp_path, "earlier", 3),
    ]

    result = SkillRanker(FakeScorer([0.9, 0.9])).rank(
        task(),
        skills,
        minimum_cardinality=0,
        absolute_inclusion_threshold=0.9,
        selection_blocking=False,
    )

    assert result.names == ("earlier", "later")


def test_selection_blocks_circular_owner_and_update_factory(tmp_path: Path) -> None:
    skills = [
        candidate(tmp_path, "proposal", 0),
        candidate(tmp_path, "skill-factory", 1),
        candidate(tmp_path, "skill-authoring-guide", 2),
    ]
    value = task()
    value["filesToWrite"] = ["skills/proposal/SKILL.md"]
    result = SkillRanker(FakeScorer([0.99, 0.98, 0.9])).rank(value, skills)
    assert result.names == ("skill-authoring-guide",)
    assert len(result.diagnostics.candidate_scores) == 3


def test_selection_keeps_factory_for_new_skill(tmp_path: Path) -> None:
    skills = [
        candidate(tmp_path, "skill-factory", 0),
        candidate(tmp_path, "skill-authoring-guide", 1),
    ]
    value = task()
    value["filesToWrite"] = ["skills/new-skill/SKILL.md"]
    result = SkillRanker(FakeScorer([0.99, 0.9])).rank(value, skills)
    assert result.names == ("skill-factory", "skill-authoring-guide")


def test_selection_blocks_factory_for_existing_noncandidate_skill(
    tmp_path: Path,
) -> None:
    skills = [
        candidate(tmp_path, "skill-factory", 0),
        candidate(tmp_path, "skill-authoring-guide", 1),
    ]
    value = task()
    value["filesToRead"] = ["skills/delegated-owner/SKILL.md"]
    value["filesToWrite"] = ["skills/delegated-owner/SKILL.md"]
    result = SkillRanker(FakeScorer([0.99, 0.9])).rank(value, skills)
    assert result.names == ("skill-authoring-guide",)


@pytest.mark.parametrize("scores", [[0.5], [math.nan], [math.inf]])
def test_score_count_and_finiteness_failures(
    tmp_path: Path, scores: list[float]
) -> None:
    skills = [candidate(tmp_path), candidate(tmp_path, "second", 1)]
    with pytest.raises(SkillRankingRuntimeError):
        SkillRanker(FakeScorer(scores)).rank(task(), skills)


def test_policy_and_scorer_errors_are_distinct(tmp_path: Path) -> None:
    with pytest.raises(SkillRankingConfigurationError):
        RankingPolicy(additional_skill_threshold=math.nan)

    class Broken:
        def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
            del query, documents
            raise RuntimeError("offline failure")

    with pytest.raises(SkillRankingRuntimeError):
        SkillRanker(Broken()).rank(task(), [candidate(tmp_path)])
