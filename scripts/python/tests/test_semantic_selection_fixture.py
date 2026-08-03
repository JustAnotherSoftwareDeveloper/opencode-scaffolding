"""Schema and frozen-inventory checks for semantic selection evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "test-data" / "semantic-selection-cases.json"
SKILLS_ROOT = ROOT.parents[1] / "skills"
RANKING_FIELDS = {"rank", "ranking", "score", "scores", "threshold", "confidence"}


def _data() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _inventory(data: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {item["name"]: item for item in data["inventory"]}


def test_fixture_has_deterministic_schema_and_no_ranking_fields() -> None:
    data = _data()
    assert data["schema_version"] == 1
    assert isinstance(data["inventory"], list) and data["inventory"]
    assert isinstance(data["cases"], list) and data["cases"]
    assert len({item["name"] for item in data["inventory"]}) == len(data["inventory"])
    assert len({case["id"] for case in data["cases"]}) == len(data["cases"])
    assert not RANKING_FIELDS.intersection(_all_keys(data))


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_all_keys(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in value)) if value else set()
    return set()


def test_frozen_inventory_records_resolve_to_matching_skill_files() -> None:
    data = _data()
    for item in data["inventory"]:
        path = ROOT.parents[1] / item["path"]
        assert path == SKILLS_ROOT / item["name"] / "SKILL.md"
        assert path.is_file(), item["name"]
        frontmatter = yaml.safe_load(
            path.read_text(encoding="utf-8").split("---", 2)[1]
        )
        assert frontmatter["name"] == item["name"]
        assert frontmatter["class"] == item["class"]


@pytest.mark.parametrize("section", ["cases"])
def test_expected_names_and_paths_resolve_against_frozen_inventory(
    section: str,
) -> None:
    data = _data()
    inventory = _inventory(data)
    for case in data[section]:
        names = case["expected"]["names"]
        paths = case["expected"]["paths"]
        assert len(names) == len(paths)
        assert len(names) == len(set(names))
        for name, path in zip(names, paths, strict=True):
            assert name in inventory, case["id"]
            assert inventory[name]["path"] == path, case["id"]


def test_supported_task_cases_obey_one_to_three_cardinality() -> None:
    for case in _data()["cases"]:
        if case["mode"] == "task":
            assert len(case["expected"]["names"]) <= 3


def test_invalid_contract_cases_are_explicitly_invalid() -> None:
    data = _data()
    inventory = _inventory(data)
    assert {case["id"] for case in data["invalid_contract_cases"]} == {
        "unknown-expected-name",
        "expected-path-mismatch",
        "too-many-task-skills",
    }
    assert "missing-skill" not in inventory
    mismatch = next(
        case
        for case in data["invalid_contract_cases"]
        if case["id"] == "expected-path-mismatch"
    )
    assert (
        inventory[mismatch["expected"]["names"][0]]["path"]
        != mismatch["expected"]["paths"][0]
    )
    oversized = next(
        case
        for case in data["invalid_contract_cases"]
        if case["id"] == "too-many-task-skills"
    )
    assert len(oversized["expected"]["names"]) == 4
