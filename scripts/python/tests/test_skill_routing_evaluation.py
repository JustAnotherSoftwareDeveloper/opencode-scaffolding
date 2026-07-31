"""Adjudicated cross-domain evidence for the routing-signature contract."""

# The fixture assertions intentionally keep long evidence strings readable.
# ruff: noqa: E501

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from lib.collect_skills.models import Skill
from lib.generate_task_json.core import _select_skills
from lib.generate_task_json.qwen_prompt import SKILL_RENDER_VERSION, render_skill
from lib.generate_task_json.ranker import ScoreResult, SkillCandidate, SkillRanker
from lib.shared.skill_routing import (
    RoutingContractError,
    load_builtin_registry,
    normalize_routing_signature,
    resolve_registry_overlay,
)

FIXTURE = Path(__file__).parent / "fixtures" / "skill_routing" / "evaluation.json"


def _data() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _skills(data: dict[str, Any]) -> tuple[Skill, ...]:
    registry = resolve_registry_overlay(data["registry"], load_builtin_registry())
    result = []
    for item in data["skills"]:
        signature = normalize_routing_signature(item, registry)
        result.append(
            Skill(
                item["name"],
                item["description"],
                signature.schema_version.value,
                signature.cues,
                signature.relationships,
                item["class"],
            )
        )
    return tuple(result)


def _task(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "purpose": case["input"],
        "context": "",
        "expectedOutput": "a routing decision",
        "executionInstructions": [],
        "verification": [],
    }


def _metrics(
    cases: list[dict[str, Any]], outputs: dict[str, list[str]]
) -> dict[str, float]:
    expected = [set(case["expected"]) for case in cases]
    predicted = [set(outputs[case["id"]]) for case in cases]
    positives = sum(map(len, expected))
    return {
        "precision": sum(
            (len(a & e) / len(a)) if a else float(not e)
            for a, e in zip(predicted, expected, strict=True)
        )
        / len(cases),
        "recall": sum(len(a & e) for a, e in zip(predicted, expected, strict=True))
        / max(positives, 1),
        "exact_set_accuracy": sum(
            a == e for a, e in zip(predicted, expected, strict=True)
        )
        / len(cases),
    }


def test_fixture_inventory_and_case_families_are_adjudicated() -> None:
    data = _data()
    assert data["render_version"] == SKILL_RENDER_VERSION
    assert {item["domain"] for item in data["skills"]} >= {
        "business",
        "agriculture",
        "healthcare",
        "arts",
    }
    assert set(data["case_families"]) == {case["family"] for case in data["cases"]} | {
        "namespace-failure"
    }
    assert len({case["id"] for case in data["cases"]}) == len(data["cases"])
    assert (
        len(
            next(case for case in data["cases"] if case["id"] == "multi-domain")[
                "expected"
            ]
        )
        == 3
    )


def test_repository_local_facet_reaches_deterministic_and_qwen_renderers() -> None:
    data = _data()
    skill = next(
        item for item in _skills(data) if item.name == "orchard-harvest-window"
    )
    assert any(cue.facet == "orchard:crop-stage" for cue in skill.cues)
    deterministic_text = " ".join(cue.value for cue in skill.cues)
    assert "postharvest" in deterministic_text
    candidate = SkillCandidate(
        "orchard-harvest-window",
        skill.description,
        skill.cues,
        skill.relationships,
        skill.class_,
        "project",
        FIXTURE.resolve(),
    )
    rendered = render_skill(candidate)
    assert "facet=orchard:crop-stage" in rendered
    assert "value=postharvest" in rendered


def test_namespace_failures_are_actionable() -> None:
    registry = load_builtin_registry()
    for item in _data()["invalid_metadata"]:
        if item["id"] == "builtin-redefinition":
            with pytest.raises(RoutingContractError, match=item["reason"]):
                resolve_registry_overlay(
                    {
                        "namespace": "repo",
                        "facets": [{"name": "operation", "meaning": "wrong"}],
                    },
                    registry,
                )
        else:
            cue = {"facet": item["facet"], "value": "x"}
            with pytest.raises(RoutingContractError, match=item["reason"]):
                normalize_routing_signature(
                    {
                        "schema_version": "1.0",
                        "cues": [cue],
                        "relationships": [{"role": "owner"}],
                    },
                    registry,
                )


def test_deterministic_path_records_metrics_without_policy_changes() -> None:
    data = _data()
    skills = _skills(data)
    outputs = {
        case["id"]: _select_skills(_task(case), list(skills)) for case in data["cases"]
    }
    metrics = _metrics(data["cases"], outputs)
    assert metrics["exact_set_accuracy"] >= 0.40
    assert metrics["recall"] >= 0.70


class _CapturedQwen:
    def __init__(self, expected: set[str]) -> None:
        self.expected = expected
        self.last_token_counts = (211,)
        self.last_request_seconds = (0.001,)
        self.last_prompt_hashes = ("capture",)

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
        del query
        return [
            ScoreResult(
                0.99
                if any(f"Skill name: {name}" in document for name in self.expected)
                else 0.01,
                ("no",),
            )
            for document in documents
        ]

    def diagnostic_identity(self) -> dict[str, str]:
        return {
            "model": "captured-qwen",
            "render": SKILL_RENDER_VERSION,
            "prompt": "qwen3-reranker-4b-classifier-v1",
        }


def test_qwen_diagnostic_collection_uses_new_render_and_records_clipping() -> None:
    data = _data()
    skills = tuple(
        SkillCandidate(
            item.name,
            item.description,
            item.cues,
            item.relationships,
            item.class_,
            "project",
            FIXTURE.resolve(),
        )
        for item in _skills(data)
    )
    outputs = {}
    for case in data["cases"]:
        scorer = _CapturedQwen(set(case["expected"]))
        result = SkillRanker(scorer).rank(_task(case), skills, minimum_cardinality=0)
        outputs[case["id"]] = list(result.names)
        assert result.diagnostics.clipped_labels == ("no",) * len(skills)
        assert scorer.diagnostic_identity()["render"] == data["render_version"]
        assert result.diagnostics.token_counts == (211,)
    assert _metrics(data["cases"], outputs) == {
        "precision": 1.0,
        "recall": 1.0,
        "exact_set_accuracy": 1.0,
    }
