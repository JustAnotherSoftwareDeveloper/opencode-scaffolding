"""Tests for canonical semantic-selection release gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.semantic_selection_evaluation.core import (
    EvaluationError,
    evaluate_fixture,
    load_fixture,
)

ROOT = Path(__file__).parents[3]
FIXTURE = Path(__file__).parents[1] / "test-data/semantic-selection-cases.json"


def test_deterministic_covers_every_canonical_case() -> None:
    result = evaluate_fixture(load_fixture(FIXTURE), root=ROOT)
    assert result["passed"] is True
    assert result["fixture_cases"] == 10
    assert len(result["cases"]) == 10
    assert all("score" not in case for case in result["cases"].values())


def test_deterministic_resolves_paths_and_allows_uncapped_planning() -> None:
    result = evaluate_fixture(load_fixture(FIXTURE), root=ROOT)
    assert result["cases"]["planning-lifecycle-reference"]["resolved_paths"] == [
        str(ROOT / "skills/planning-pipeline-architecture/SKILL.md")
    ]
    assert result["cases"]["three-skill-task-cardinality"]["passed"] is True


def test_invalid_contracts_are_reported_without_fallback() -> None:
    fixture = load_fixture(FIXTURE)
    for invalid in fixture["invalid_contract_cases"]:
        case = dict(invalid)
        case["mode"] = invalid.get("mode", "task")
        case["request"] = "invalid contract"
        fixture["cases"] = [case]
        result = evaluate_fixture(fixture, root=ROOT)
        assert result["passed"] is False
        assert result["cases"][case["id"]]["error"] == invalid["error"]


def test_configured_llm_preserves_settings_and_rejects_malformed_output() -> None:
    fixture = load_fixture(FIXTURE)
    responses = {case["id"]: case["expected"]["names"] for case in fixture["cases"]}
    responses["python-script-task"] = "not json"
    result = evaluate_fixture(
        fixture,
        root=ROOT,
        mode="configured-llm",
        responses=responses,
        provider="generic",
        model="configured-model",
        host="configured-host",
    )
    assert result["configuration"] == {
        "provider": "generic",
        "model": "configured-model",
        "host": "configured-host",
    }
    assert result["passed"] is False
    assert result["cases"]["python-script-task"]["error"] == (
        "malformed selection output"
    )


def test_unknown_name_and_path_fail_closed() -> None:
    fixture = load_fixture(FIXTURE)
    fixture["cases"] = [
        {
            "id": "bad",
            "mode": "task",
            "expected": {"names": ["missing"], "paths": ["skills/missing/SKILL.md"]},
        }
    ]
    result = evaluate_fixture(fixture, root=ROOT)
    assert result["passed"] is False
    assert result["cases"]["bad"]["error"] == "expected skill is absent from inventory"


def test_configured_llm_rejects_unsupported_response_name() -> None:
    fixture = load_fixture(FIXTURE)
    responses = {case["id"]: case["expected"]["names"] for case in fixture["cases"]}
    responses["python-script-task"] = ["invented"]
    result = evaluate_fixture(
        fixture, root=ROOT, mode="configured-llm", responses=responses
    )
    assert result["cases"]["python-script-task"]["error"] == (
        "selection contains unsupported skill name"
    )


def test_missing_inventory_file_blocks_evaluation(tmp_path: Path) -> None:
    fixture = {
        "inventory": [{"name": "x", "path": "missing", "class": "inline"}],
        "cases": [],
    }
    with pytest.raises(EvaluationError, match="does not resolve"):
        evaluate_fixture(fixture, root=tmp_path)
