"""Direct-call tests for semantic evaluation and review-acceptance contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.boundary_review_acceptance.core import accept_boundary_review
from lib.schema import core as schema_core
from lib.semantic_selection_evaluation.core import (
    EvaluationError,
    evaluate_fixture,
    load_fixture,
    load_responses,
)

pytestmark = pytest.mark.unit

_ROOT_SCHEMA = {
    "type": "object",
    "required": ["slug", "tasks", "boundaryReview"],
    "properties": {
        "boundaryReview": {
            "type": "object",
            "required": ["taskReviews", "warningDispositions"],
        }
    },
}


def _packet() -> dict[str, object]:
    return {
        "slug": "reviewed-plan",
        "tasks": [
            {
                "taskId": "one",
                "verificationCoverage": {"observable": ["contract"]},
                "dependencies": [],
                "filesToWrite": [],
            }
        ],
        "boundaryReview": {
            "taskReviews": {
                "one": {
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
            },
            "warningDispositions": {},
        },
    }


def _evidence(**updates: object) -> dict[str, object]:
    values: dict[str, object] = {
        "reviewedRequest": "Implement the reviewed plan.",
        "packetSlug": "reviewed-plan",
        "reviewedTaskIds": ["one"],
        "disposition": "accepted",
        "rationale": "The supplied boundaries were reviewed.",
        "deficiencies": [],
    }
    values.update(updates)
    return values


def test_boundary_review_acceptance_binds_request_packet_and_task_ids() -> None:
    """Accept only the structurally valid packet bound by explicit evidence."""
    accepted, diagnostics = accept_boundary_review(
        "Implement the reviewed plan.",
        _packet(),
        _evidence(),
        _ROOT_SCHEMA,
    )
    assert accepted is True
    assert diagnostics == []

    rejected, reasons = accept_boundary_review(
        " ",
        _packet(),
        _evidence(
            reviewedRequest="different request",
            packetSlug="different-slug",
            reviewedTaskIds=["one", "one"],
            disposition="rejected",
            rationale=" ",
            deficiencies=["missing result"],
        ),
        _ROOT_SCHEMA,
    )
    assert rejected is False
    assert any("non-empty string" in reason for reason in reasons)
    assert any("unchanged original request" in reason for reason in reasons)
    assert any("canonical packet slug" in reason for reason in reasons)
    assert any("exactly once" in reason for reason in reasons)
    assert any("disposition" in reason for reason in reasons)
    assert any("rationale" in reason for reason in reasons)
    assert any("deficiencies" in reason for reason in reasons)


@pytest.mark.parametrize("evidence", [None, {"deficiencies": "not-list"}])
def test_boundary_review_rejects_invalid_evidence_and_structure(
    evidence: object,
) -> None:
    """Fail closed for non-object attestations and invalid canonical roots."""
    accepted, diagnostics = accept_boundary_review(
        "Request", _packet(), evidence, _ROOT_SCHEMA
    )
    assert accepted is False
    assert diagnostics

    malformed = {"slug": "broken", "tasks": []}
    accepted, diagnostics = accept_boundary_review(
        "Request", malformed, _evidence(), _ROOT_SCHEMA
    )
    assert accepted is False
    assert diagnostics[0] == "canonical packet failed structural validation"


def test_schema_loaders_read_arbitrary_and_canonical_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Load explicit schemas and preserve the root object contract."""
    schema_path = tmp_path / "schema.json"
    schema_path.write_text('{"type":"object"}', encoding="utf-8")
    assert schema_core.load_schema(schema_path) == {"type": "object"}
    monkeypatch.setattr(schema_core, "_SCHEMA_PATH", schema_path)
    assert schema_core.load_task_packet_schema() == {"type": "object"}

    schema_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a JSON object"):
        schema_core.load_task_packet_schema()


def _selection_fixture(root: Path) -> dict[str, object]:
    skill_path = root / "skills" / "alpha.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text("skill", encoding="utf-8")
    return {
        "inventory": [{"name": "alpha", "path": "skills/alpha.md"}],
        "cases": [
            {
                "id": "select-alpha",
                "mode": "task",
                "expected": {"names": ["alpha"], "paths": ["skills/alpha.md"]},
            }
        ],
    }


def test_semantic_fixture_loaders_reject_incomplete_documents(
    tmp_path: Path,
) -> None:
    """Require canonical arrays and mapping-shaped configured responses."""
    path = tmp_path / "fixture.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(EvaluationError, match="inventory array"):
        load_fixture(path)
    path.write_text('{"inventory":[]}', encoding="utf-8")
    with pytest.raises(EvaluationError, match="cases array"):
        load_fixture(path)
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(EvaluationError, match="responses must be an object"):
        load_responses(path)


@pytest.mark.parametrize(
    ("fixture", "message"),
    [
        ({"inventory": "bad", "cases": []}, "must be arrays"),
        ({"inventory": ["bad"], "cases": []}, "string name"),
        ({"inventory": [{"name": "alpha"}], "cases": []}, "inventory path"),
        ({"inventory": [], "cases": ["bad"]}, "string id"),
        (
            {"inventory": [], "cases": [{"id": "case"}]},
            "no expected selection",
        ),
        (
            {"inventory": [], "cases": [{"id": "case", "expected": {}}]},
            "must be arrays",
        ),
    ],
)
def test_semantic_evaluator_rejects_malformed_fixture_contracts(
    tmp_path: Path, fixture: dict[str, object], message: str
) -> None:
    """Return specific diagnostics for malformed inventory and expected data."""
    valid = _selection_fixture(tmp_path)
    with pytest.raises(EvaluationError, match=message):
        evaluate_fixture(fixture, root=tmp_path)
    assert valid["cases"]


def test_semantic_evaluator_reports_expected_selection_contract_errors(
    tmp_path: Path,
) -> None:
    """Reject absent names, mismatched paths, and task over-selection."""
    base = _selection_fixture(tmp_path)
    base["cases"] = [
        {
            "id": "duplicate",
            "mode": "task",
            "expected": {
                "names": ["alpha", "alpha"],
                "paths": ["skills/alpha.md", "skills/alpha.md"],
            },
        },
        {
            "id": "bad-path",
            "mode": "global",
            "expected": {"names": ["alpha"], "paths": ["elsewhere.md"]},
        },
        {
            "id": "too-many",
            "mode": "task",
            "expected": {
                "names": ["alpha", "b", "c", "d"],
                "paths": ["skills/alpha.md", "b.md", "c.md", "d.md"],
            },
        },
    ]
    result = evaluate_fixture(base, root=tmp_path)
    assert result["passed"] is False
    assert result["cases"]["duplicate"]["error"] == (
        "selection contains duplicate skill names"
    )
    assert result["cases"]["bad-path"]["error"] == (
        "expected path does not match inventory"
    )
    assert result["cases"]["too-many"]["error"] == (
        "task selection exceeds three skills"
    )


@pytest.mark.parametrize(
    ("response", "message"),
    [
        ("not-json", "malformed selection output"),
        (
            {"skills": "not-list"},
            "selection output must be an array of skill names",
        ),
        (["alpha", "alpha"], "selection contains duplicate skill names"),
        (["missing"], "selection contains unsupported skill name"),
        (["alpha", "b", "c", "d"], "task selection exceeds three skills"),
    ],
)
def test_semantic_evaluator_validates_configured_response_shapes(
    tmp_path: Path, response: object, message: str
) -> None:
    """Validate response JSON, object wrappers, duplicates, and skill limits."""
    fixture = _selection_fixture(tmp_path)
    result = evaluate_fixture(
        fixture,
        root=tmp_path,
        mode="configured-llm",
        responses={"select-alpha": response},
    )
    assert result["passed"] is False
    assert result["cases"]["select-alpha"]["error"] == message


def test_semantic_evaluator_accepts_json_text_and_reports_missing_responses(
    tmp_path: Path,
) -> None:
    """Parse valid JSON model output and report absent response entries."""
    fixture = _selection_fixture(tmp_path)
    result = evaluate_fixture(
        fixture,
        root=tmp_path,
        mode="configured-llm",
        responses={"select-alpha": json.dumps({"skills": ["alpha"]})},
        provider="local",
        model="model-x",
        host="http://model",
    )
    assert result["passed"] is True
    assert result["cases"]["select-alpha"]["resolved_paths"] == [
        str(tmp_path / "skills" / "alpha.md")
    ]
    assert result["configuration"] == {
        "provider": "local",
        "model": "model-x",
        "host": "http://model",
    }

    missing = evaluate_fixture(
        fixture, root=tmp_path, mode="configured-llm", responses={}
    )
    assert missing["cases"]["select-alpha"]["error"] == (
        "missing configured-LLM response"
    )


def test_semantic_evaluator_rejects_unknown_modes_and_duplicate_inventory(
    tmp_path: Path,
) -> None:
    """Keep the evaluator closed for unsupported modes and duplicate names."""
    fixture = _selection_fixture(tmp_path)
    with pytest.raises(EvaluationError, match="mode must be"):
        evaluate_fixture(fixture, root=tmp_path, mode="unknown")
    inventory = fixture["inventory"]
    assert isinstance(inventory, list)
    inventory.append({"name": "alpha", "path": "skills/alpha.md"})
    with pytest.raises(EvaluationError, match="duplicate inventory name"):
        evaluate_fixture(fixture, root=tmp_path)
