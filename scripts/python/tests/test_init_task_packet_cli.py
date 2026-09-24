"""CLI tests for init-task-packet."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.init_task_packet import main


def _packet(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "summary": "Test packet for init",
        "slug": "test-packet-for-init",
        "boundaryReview": {
            "requestResultInventory": {
                "init": {
                    "result": "A packet file.",
                    "kind": "immediate",
                    "disposition": "represented-by-task",
                }
            },
            "taskReviews": {
                "init": {
                    "immediateResult": "A packet file.",
                    "predecessorOutputs": [],
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
            },
            "warningDispositions": {},
        },
        "tasks": [
            {
                "taskId": "init",
                "purpose": "Init a packet.",
                "context": "x" * 200,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["demo"],
                "executionInstructions": [{"step": 1, "action": "Run it."}],
                "expectedOutput": "A packet file.",
                "verificationCoverage": {"observable": ["Packet file exists."]},
                "dependencies": [],
                "antiPatternSignals": ["none"],
                "purposeOutputAlignment": {
                    "status": "aligned",
                    "evidence": "Initialization publishes the packet file.",
                },
            }
        ],
    }
    data.update(overrides)
    return data


def test_publishes_and_prints_path(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet()),
    )
    assert result.exit_code == 0, result.output
    path = Path(result.output.strip())
    assert path.is_file()
    assert path.suffix == ".json"
    assert path.parent == tmp_path


def test_rejects_invalid_json(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input="{not json",
    )
    assert result.exit_code == 1


def test_rejects_non_object(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input="[]",
    )
    assert result.exit_code == 1


def test_rejects_missing_summary(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps({"tasks": []}),
    )
    assert result.exit_code == 1
    assert "summary" in result.output


def test_rejects_empty_summary(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps({"summary": "   ", "tasks": []}),
    )
    assert result.exit_code == 1


def test_rejects_existing_destination(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("cli.init_task_packet.time.time_ns", lambda: 1_000_000_000)
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet()),
    )
    assert result.exit_code == 0
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet()),
    )
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_preserves_supplied_slug(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet(slug="deploy-api-gateway")),
    )
    assert result.exit_code == 0
    path = Path(result.output.strip())
    assert "deploy-api-gateway" in path.name
    assert path.suffix == ".json"
    assert json.loads(path.read_text(encoding="utf-8"))["slug"] == "deploy-api-gateway"


def test_accepts_non_ascii_summary_without_deriving_a_slug(tmp_path: Path) -> None:
    """Summary text is opaque; publication uses the supplied ASCII identity."""
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(
            _packet(summary="公開用の計画 — naïve café", slug="published-plan")
        ),
    )

    assert result.exit_code == 0, result.output
    path = Path(result.output.strip())
    assert path.name.endswith("-published-plan.json")
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["summary"] == "公開用の計画 — naïve café"
    assert persisted["slug"] == "published-plan"


@pytest.mark.parametrize(
    "slug",
    [None, "", "Uppercase", "unicode-ß", "repeated--separator", "a" * 81],
)
def test_rejects_missing_or_malformed_supplied_slug(
    tmp_path: Path, slug: object
) -> None:
    packet = _packet()
    if slug is None:
        packet.pop("slug")
    else:
        packet["slug"] = slug

    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(packet),
    )

    assert result.exit_code == 1
    assert "slug" in result.output
    assert list(tmp_path.iterdir()) == []


def test_help_works() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "init-task-packet" in result.output
