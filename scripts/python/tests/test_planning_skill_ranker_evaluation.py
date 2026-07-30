"""Benchmark harness for the passive planning-context selector.

The benchmark deliberately consumes captured selector outputs.  It does not
turn task-assignment results into planning evidence, and it discovers the
planning inventory at test time so adding a planning reference requires
coverage in this labeled fixture.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from lib.collect_skills.discovery import discover_all_skills
from lib.collect_skills.models import SkillIndex
from lib.generate_task_json.ranker_manifest import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "planning_skill_ranker" / "cases.json"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT


@dataclass(frozen=True)
class Metrics:
    exact_set_accuracy: float
    per_skill_recall: float
    false_positive_rate: float
    multi_reference_accuracy: float
    empty_result_accuracy: float

    def report(self) -> str:
        return (
            f"exact_set_accuracy={self.exact_set_accuracy:.3f} "
            f"per_skill_recall={self.per_skill_recall:.3f} "
            f"false_positive_rate={self.false_positive_rate:.3f} "
            f"multi_reference_accuracy={self.multi_reference_accuracy:.3f} "
            f"empty_result_accuracy={self.empty_result_accuracy:.3f}"
        )


def _load_fixture() -> list[dict[str, Any]]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert value["schema_version"] == 1
    cases = value["cases"]
    assert isinstance(cases, list) and cases
    return cases


def _planning_names() -> tuple[str, ...]:
    index = SkillIndex()
    discover_all_skills(index, project_root=PROJECT_ROOT, config_dir=CONFIG_DIR)
    return tuple(skill.name for skill in index.filter_by_classes(("planning",)))


def _validate_fixture(cases: list[dict[str, Any]], names: tuple[str, ...]) -> None:
    assert names, "the dynamically discovered planning inventory is empty"
    by_id = {case["id"]: case for case in cases}
    assert len(by_id) == len(cases), "fixture case ids must be unique"
    for case in cases:
        assert isinstance(case["input"], str) and case["input"].strip()
        expected = set(case["expected"])
        assert expected <= set(names), (
            f"unknown expected planning skill in {case['id']}"
        )
        if case["family"] == "multi-match":
            assert len(expected) > 1, (
                f"multi-match case is not multi-reference: {case['id']}"
            )
        if case["family"] == "adjacent-near-miss":
            target = case.get("target")
            assert target in names and target not in expected, (
                f"near-miss coverage is invalid for {target!r}: {case['id']}"
            )
    for name in names:
        positives = [case for case in cases if name in case["expected"]]
        near_misses = [
            case
            for case in cases
            if case["family"] == "adjacent-near-miss" and case.get("target") == name
        ]
        assert positives, f"planning skill {name!r} lacks positive fixture coverage"
        assert near_misses, f"planning skill {name!r} lacks near-miss fixture coverage"


def _metrics(cases: list[dict[str, Any]], outputs: dict[str, list[str]]) -> Metrics:
    expected = [set(case["expected"]) for case in cases]
    predicted = [set(outputs[case["id"]]) for case in cases]
    assert len(expected) == len(predicted)
    pairs = zip(predicted, expected, strict=True)
    exact = sum(actual == wanted for actual, wanted in pairs) / len(cases)
    positives = sum(len(wanted) for wanted in expected)
    pairs = zip(predicted, expected, strict=True)
    recall = sum(len(actual & wanted) for actual, wanted in pairs) / positives
    negatives = sum(len(wanted) == 0 for wanted in expected)
    pairs = zip(predicted, expected, strict=True)
    false_positive = sum(bool(actual - wanted) for actual, wanted in pairs) / max(
        negatives, 1
    )
    pairs = zip(predicted, expected, strict=True)
    multi = [(actual, wanted) for actual, wanted in pairs if len(wanted) > 1]
    pairs = zip(predicted, expected, strict=True)
    empty = [(actual, wanted) for actual, wanted in pairs if not wanted]
    return Metrics(
        exact,
        recall,
        false_positive,
        sum(actual == wanted for actual, wanted in multi) / max(len(multi), 1),
        sum(not actual for actual, _ in empty) / max(len(empty), 1),
    )


def _captured_outputs() -> dict[str, dict[str, list[str]]]:
    path = os.environ.get("PLANNING_SKILL_RANKER_RESPONSES")
    if not path:
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    assert isinstance(value, dict) and value, (
        "captured responses must be a profile mapping"
    )
    return value


def test_fixture_covers_dynamic_planning_inventory() -> None:
    cases = _load_fixture()
    _validate_fixture(cases, _planning_names())


def test_supported_q8_and_q4_share_planning_contract() -> None:
    q8 = load_manifest(profile="q8").data
    q4 = load_manifest(profile="q4").data
    for key in ("model", "assets", "runtime", "prompt", "policy"):
        assert q8[key] == q4[key], f"Q8/Q4 planning contract differs for {key}"


def test_captured_planning_profiles_report_metrics() -> None:
    cases = _load_fixture()
    names = _planning_names()
    _validate_fixture(cases, names)
    captures = _captured_outputs()
    if not captures:
        pytest.skip(
            "set PLANNING_SKILL_RANKER_RESPONSES to run captured model evaluation"
        )
    case_ids = {case["id"] for case in cases}
    for profile, outputs in captures.items():
        assert profile in {"q8", "q4"}, (
            f"unsupported planning ranker profile: {profile}"
        )
        assert set(outputs) == case_ids, (
            f"{profile} capture does not cover every fixture case"
        )
        for _case_id, selected in outputs.items():
            assert isinstance(selected, list) and all(
                name in names for name in selected
            )
        metrics = _metrics(cases, outputs)
        print(f"planning profile={profile} {metrics.report()}")


def test_metrics_distinguish_false_positives_from_missed_positives() -> None:
    cases = [
        {"id": "positive", "expected": ["one"]},
        {"id": "negative", "expected": []},
    ]
    metrics = _metrics(cases, {"positive": [], "negative": ["one"]})
    assert metrics.per_skill_recall == 0
    assert metrics.false_positive_rate == 1
