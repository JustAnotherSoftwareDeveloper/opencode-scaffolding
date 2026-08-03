"""Validate deterministic and configured-LLM selection evaluations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


class EvaluationError(ValueError):
    """Raised when an evaluation contract cannot be evaluated."""


def load_fixture(path: Path) -> dict[str, Any]:
    """Load and minimally validate the canonical fixture."""
    value = _load_json(path, "fixture")
    if not isinstance(value, dict) or not isinstance(value.get("inventory"), list):
        raise EvaluationError("fixture must be an object with an inventory array")
    if not isinstance(value.get("cases"), list):
        raise EvaluationError("fixture must contain a cases array")
    return value


def load_responses(path: Path) -> dict[str, Any]:
    """Load model responses keyed by canonical case id."""
    value = _load_json(path, "responses")
    if not isinstance(value, dict):
        raise EvaluationError("responses must be an object keyed by case id")
    return value


def evaluate_fixture(
    fixture: dict[str, Any],
    *,
    root: Path,
    mode: str = "deterministic",
    responses: dict[str, Any] | None = None,
    provider: str | None = None,
    model: str | None = None,
    host: str | None = None,
) -> dict[str, Any]:
    """Return machine-readable release-gate results without scores or fallback."""
    if mode not in {"deterministic", "configured-llm"}:
        raise EvaluationError("mode must be deterministic or configured-llm")
    inventory = fixture.get("inventory")
    cases = fixture.get("cases")
    if not isinstance(inventory, list) or not isinstance(cases, list):
        raise EvaluationError("fixture inventory and cases must be arrays")
    records: dict[str, dict[str, Any]] = {}
    inventory_by_name: dict[str, dict[str, Any]] = {}
    for item in inventory:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise EvaluationError("inventory entries must contain a string name")
        name = item["name"]
        if name in inventory_by_name:
            raise EvaluationError(f"duplicate inventory name: {name}")
        inventory_by_name[name] = item
        _resolve_inventory_path(item, root)

    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise EvaluationError("each case must contain a string id")
        case_id = case["id"]
        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise EvaluationError(f"case {case_id} has no expected selection")
        expected_names = expected.get("names")
        expected_paths = expected.get("paths")
        if not _valid_string_array(expected_names) or not _valid_string_array(
            expected_paths
        ):
            raise EvaluationError(
                f"case {case_id} expected names and paths must be arrays"
            )
        expected_names = cast(list[str], expected_names)
        expected_paths = cast(list[str], expected_paths)
        if len(expected_names) != len(expected_paths):
            raise EvaluationError(
                f"case {case_id} expected names and paths differ in length"
            )
        contract_error = _validate_selection_contract(
            case, expected_names, expected_paths, inventory_by_name
        )
        actual: Any = expected_names if mode == "deterministic" else None
        if mode == "configured-llm":
            if responses is None or case_id not in responses:
                actual = None
                contract_error = contract_error or "missing configured-LLM response"
            else:
                actual = responses[case_id]
        selected, output_error = _parse_selection(actual)
        response_error = _validate_response_selection(selected, case, inventory_by_name)
        error = contract_error or output_error or response_error
        passed = error is None and selected == expected_names
        records[case_id] = {
            "id": case_id,
            "kind": case.get("kind"),
            "mode": case.get("mode"),
            "passed": passed,
            "expected": {"names": expected_names, "paths": expected_paths},
            "selected": selected,
            "resolved_paths": [
                str(_resolve_inventory_path(inventory_by_name[name], root))
                for name in selected or []
                if name in inventory_by_name
            ],
            "error": error,
        }
    return {
        "evaluator": "semantic-selection-evaluation",
        "mode": mode,
        "configuration": {"provider": provider, "model": model, "host": host},
        "fixture_cases": len(cases),
        "passed": all(item["passed"] for item in records.values()),
        "cases": records,
    }


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot load {label}: {exc}") from exc


def _valid_string_array(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _resolve_inventory_path(item: dict[str, Any], root: Path) -> Path:
    path = item.get("path")
    if not isinstance(path, str) or not path:
        raise EvaluationError("inventory path must be a non-empty string")
    resolved = (root / path).resolve()
    if not resolved.is_file():
        raise EvaluationError(f"inventory path does not resolve to a file: {path}")
    return resolved


def _validate_selection_contract(
    case: dict[str, Any],
    names: list[str],
    paths: list[str],
    inventory: dict[str, dict[str, Any]],
) -> str | None:
    mode = case.get("mode")
    if mode == "task" and len(names) > 3:
        return "task selection exceeds three skills"
    if len(names) != len(set(names)):
        return "selection contains duplicate skill names"
    for name, path in zip(names, paths, strict=True):
        if name not in inventory:
            return "expected skill is absent from inventory"
        if inventory[name].get("path") != path:
            return "expected path does not match inventory"
    return None


def _parse_selection(value: Any) -> tuple[list[str] | None, str | None]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None, "malformed selection output"
    if isinstance(value, dict):
        value = value.get("skills")
    if not _valid_string_array(value):
        return None, "selection output must be an array of skill names"
    return value, None


def _validate_response_selection(
    selected: list[str] | None,
    case: dict[str, Any],
    inventory: dict[str, dict[str, Any]],
) -> str | None:
    if selected is None:
        return None
    if case.get("mode") == "task" and len(selected) > 3:
        return "task selection exceeds three skills"
    if len(selected) != len(set(selected)):
        return "selection contains duplicate skill names"
    if any(name not in inventory for name in selected):
        return "selection contains unsupported skill name"
    return None
