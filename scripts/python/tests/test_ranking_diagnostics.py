"""Offline tests for canonical, private, bounded diagnostic publication."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from lib.generate_task_json.ranking_diagnostics import (
    AtomicDiagnosticSink,
    CompositeDiagnosticSink,
    DiagnosticPayload,
    NullDiagnosticSink,
    PlanningSelectionDiagnosticRecord,
    RankingDiagnosticBundle,
    RankingDiagnosticRecord,
    canonical_hash,
    canonical_json,
    publish_diagnostics,
)


def record(**overrides: object) -> RankingDiagnosticRecord:
    values: Any = {
        name: name + "-hash"
        for name in (
            "model",
            "runtime",
            "tokenizer",
            "prompt",
            "render",
            "policy",
            "inventory",
            "task",
        )
    }
    values.update({key + "_hash": value for key, value in list(values.items())})
    values.update(overrides)
    non_hash: Any = {
        key: value for key, value in overrides.items() if not key.endswith("_hash")
    }
    return RankingDiagnosticRecord(
        model_hash=values["model_hash"],
        runtime_hash=values["runtime_hash"],
        tokenizer_hash=values["tokenizer_hash"],
        prompt_hash=values["prompt_hash"],
        render_hash=values["render_hash"],
        policy_hash=values["policy_hash"],
        inventory_hash=values["inventory_hash"],
        task_hash=values["task_hash"],
        **non_hash,
    )


def planning_record(**overrides: object) -> PlanningSelectionDiagnosticRecord:
    values: Any = {
        name: name + "-hash"
        for name in (
            "model_hash",
            "runtime_hash",
            "tokenizer_hash",
            "prompt_hash",
            "renderer_hash",
            "policy_hash",
            "metadata_snapshot_hash",
            "query_hash",
        )
    }
    values.update(overrides)
    return PlanningSelectionDiagnosticRecord(**values)


def test_hash_is_canonical_and_private_payload_is_redacted() -> None:
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})
    payload = canonical_json(
        {
            "task": "secret",
            "context": "secret",
            "path": Path("/private"),
            "ok": "visible",
        }
    )
    assert (
        b"secret" not in payload
        and b"/private" not in payload
        and b"visible" in payload
    )
    assert (
        json.loads(record(extra={"task": "secret", "resolved_path": "/x"}).serialize())[
            "extra"
        ]
        == {}
    )


def test_planning_record_contains_complete_identity_and_selection_evidence() -> None:
    item = planning_record(
        candidate_scores=(("planner-a", 0.875), ("planner-b", 0.125)),
        selected_names=("planner-a",),
        latency_ms=12.5,
    )
    payload = json.loads(item.serialize())

    assert {
        "model_hash",
        "runtime_hash",
        "tokenizer_hash",
        "prompt_hash",
        "renderer_hash",
        "policy_hash",
        "metadata_snapshot_hash",
        "query_hash",
    } <= payload.keys()
    assert payload["candidate_scores"] == [["planner-a", 0.875], ["planner-b", 0.125]]
    assert payload["selected_names"] == ["planner-a"]
    assert payload["latency_ms"] == 12.5


def test_planning_identity_hashes_are_deterministic() -> None:
    identity = {"query": "choose a planner", "metadata": {"b": 2, "a": 1}}
    assert canonical_hash(identity) == canonical_hash(
        {"metadata": {"a": 1, "b": 2}, "query": "choose a planner"}
    )
    assert canonical_hash(identity) == canonical_hash(identity)


def test_planning_serialization_contains_no_raw_source_or_path_content() -> None:
    raw_values = {
        "query": "RAW_PLANNING_QUERY",
        "prompt": "RAW_PLANNING_PROMPT",
        "body": "RAW_PLANNER_BODY",
        "path": "/private/raw/planner.py",
        "filesToRead": "RAW_READ_PATH",
        "filesToWrite": "RAW_WRITE_PATH",
    }
    payload = planning_record(extra=raw_values).serialize()

    for value in raw_values.values():
        assert value.encode() not in payload
    assert b"extra" in payload


def test_planning_atomic_sink_preserves_existing_file_and_cleans_failed_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "planning" / "diagnostic.json"
    sink = AtomicDiagnosticSink(destination)
    sink.publish(planning_record(selected_names=("first",)))
    original = destination.read_bytes()

    with pytest.raises(RuntimeError, match="already exists"):
        sink.publish(planning_record(selected_names=("replacement",)))
    assert destination.read_bytes() == original
    assert list(destination.parent.glob(".*")) == []

    failed = AtomicDiagnosticSink(tmp_path / "failed-planning.json")
    monkeypatch.setattr(
        "lib.generate_task_json.ranking_diagnostics.os.link",
        lambda *_: (_ for _ in ()).throw(OSError("planning boom")),
    )
    with pytest.raises(RuntimeError, match="publication failed"):
        failed.publish(planning_record())
    assert not failed.path.exists()
    assert list(failed.path.parent.glob(".*")) == []


def test_task_record_schema_and_publication_remain_unchanged() -> None:
    payload = json.loads(
        record(
            candidate_scores=(("task-owner", 0.9),), selected_names=("task-owner",)
        ).serialize()
    )
    assert payload["task_hash"] == "task-hash"
    assert payload["candidate_scores"] == [["task-owner", 0.9]]
    assert payload["selected_names"] == ["task-owner"]
    assert "query_hash" not in payload


@pytest.mark.parametrize("field", ["model_hash", "runtime_hash", "task_hash"])
def test_identity_and_schema_bounds(field: str) -> None:
    with pytest.raises(ValueError):
        record(**{field: ""})
    with pytest.raises(ValueError):
        record(token_counts=(-1,))
    with pytest.raises(ValueError):
        record(candidate_scores=(("x", 1.1),))
    with pytest.raises(ValueError):
        record(latencies_ms=(float("inf"),))
    with pytest.raises(ValueError):
        record(assignment_mode="invalid")


def test_bounded_depth_nonfinite_and_size() -> None:
    assert b"nonfinite" in canonical_json({"value": float("nan")})
    assert b"depth-limited" in canonical_json(
        {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": 1}}}}}}}}}
    )
    with pytest.raises(ValueError):
        canonical_json({"value": "x"}, max_bytes=0)
    with pytest.raises(ValueError):
        canonical_json({"value": "x" * 100}, max_bytes=10)


def test_atomic_sink_creates_once_and_removes_temporary_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "nested" / "diagnostic.json"
    sink = AtomicDiagnosticSink(destination)
    sink.publish(record(selected_names=("owner",)))
    assert destination.exists()
    original = destination.read_bytes()
    with pytest.raises(RuntimeError, match="already exists"):
        sink.publish(record(selected_names=("new",)))
    assert destination.read_bytes() == original
    assert list(destination.parent.glob(".*")) == []

    second = AtomicDiagnosticSink(tmp_path / "second.json")
    monkeypatch.setattr(
        "lib.generate_task_json.ranking_diagnostics.os.link",
        lambda *_: (_ for _ in ()).throw(OSError("boom")),
    )
    with pytest.raises(RuntimeError, match="publication failed"):
        second.publish(record())
    assert not second.path.exists()


def test_bundle_serializes_every_record() -> None:
    payload = json.loads(
        RankingDiagnosticBundle(
            (record(selected_names=("one",)), record(selected_names=("two",)))
        ).serialize()
    )
    assert payload["schema_version"] == "ranking-diagnostics-bundle-v1"
    assert [item["selected_names"] for item in payload["records"]] == [
        ["one"],
        ["two"],
    ]


def test_sinks_are_fail_closed() -> None:
    item = record()
    NullDiagnosticSink().publish(item)
    with pytest.raises(RuntimeError):
        CompositeDiagnosticSink([]).publish(item)
    with pytest.raises(RuntimeError):
        publish_diagnostics(item, None)

    class Failing:
        def publish(self, record: DiagnosticPayload) -> None:
            _ = record
            raise RuntimeError("failed")

    with pytest.raises(RuntimeError):
        CompositeDiagnosticSink([NullDiagnosticSink(), Failing()]).publish(item)
