"""CLI tests for init-task-packet."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.init_task_packet import main
from lib.task_packet import initialization as task_packet_initialization

pytestmark = pytest.mark.integration


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
    """Verify packet publication writes and prints the output path."""
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
    """Verify invalid JSON is rejected before packet publication."""
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input="{not json",
    )
    assert result.exit_code == 2
    assert "Error:" in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert list(tmp_path.iterdir()) == []


def test_rejects_non_object(tmp_path: Path) -> None:
    """Verify non-object JSON input is rejected."""
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input="[]",
    )
    assert result.exit_code == 2
    assert "Error:" in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert list(tmp_path.iterdir()) == []


def test_rejects_missing_summary(tmp_path: Path) -> None:
    """Verify packets without a summary are rejected."""
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps({"tasks": []}),
    )
    assert result.exit_code == 2
    assert "summary" in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert list(tmp_path.iterdir()) == []


def test_rejects_empty_summary(tmp_path: Path) -> None:
    """Verify packets with a blank summary are rejected."""
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps({"summary": "   ", "tasks": []}),
    )
    assert result.exit_code == 2
    assert "Error:" in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert list(tmp_path.iterdir()) == []


def test_rejects_existing_destination(tmp_path: Path, monkeypatch) -> None:
    """Verify publication rejects an existing destination file."""
    monkeypatch.setattr(
        task_packet_initialization.time, "time_ns", lambda: 1_000_000_000
    )
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
    assert result.exit_code == 3
    assert "already exists" in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert len(list(tmp_path.glob("*.json"))) == 1
    assert list(tmp_path.glob(".*.tmp")) == []


def test_preserves_supplied_slug(tmp_path: Path) -> None:
    """Verify packet publication preserves the supplied slug."""
    result = CliRunner().invoke(
        main,
        ["--output-dir", str(tmp_path)],
        input=json.dumps(_packet(slug="deploy-api-gateway")),
    )
    assert result.exit_code == 0
    path = Path(result.output.strip())
    assert "deploy-api-gateway" in path.name
    assert path.suffix == ".json"
    assert (
        json.loads(path.read_text(encoding="utf-8"))["slug"]
        == "deploy-api-gateway"
    )


def test_accepts_non_ascii_summary_without_deriving_a_slug(
    tmp_path: Path,
) -> None:
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
    """Verify missing and malformed supplied slugs are rejected."""
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

    assert result.exit_code == 2
    assert "slug" in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "failure", ["stdin", "schema", "mkdir", "collision", "write"]
)
def test_environment_failures_return_code_three_without_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    """Report environment failures without leaking output or partial files."""
    output_dir = tmp_path / "output"
    expected_message = {
        "stdin": "reading stdin",
        "schema": "failed to load canonical",
        "mkdir": "Not a directory",
        "collision": "already exists",
        "write": "disk full",
    }[failure]
    blocked_parent: Path | None = None

    if failure == "stdin":
        monkeypatch.setattr(
            "cli.init_task_packet.click.get_text_stream",
            lambda _: (_ for _ in ()).throw(OSError("closed stdin")),
        )
    else:
        if failure == "schema":
            monkeypatch.setattr(
                task_packet_initialization,
                "load_task_packet_schema",
                lambda: (_ for _ in ()).throw(OSError("schema unavailable")),
            )
        elif failure == "mkdir":
            blocked_parent = tmp_path / "not-a-directory"
            blocked_parent.write_text("not a directory", encoding="utf-8")
            output_dir = blocked_parent / "output"
        elif failure == "collision":
            output_dir.mkdir()
            monkeypatch.setattr(
                task_packet_initialization.time,
                "time_ns",
                lambda: 1_000_000_000,
            )
            (output_dir / "1000-test-packet-for-init.json").write_text(
                "keep existing content", encoding="utf-8"
            )
        elif failure == "write":
            monkeypatch.setattr(
                task_packet_initialization.os,
                "fsync",
                lambda *_: (_ for _ in ()).throw(OSError("disk full")),
            )

    result = CliRunner().invoke(
        main,
        ["--output-dir", str(output_dir)],
        input=json.dumps(_packet()),
    )

    assert result.exit_code == 3
    assert expected_message in result.stderr
    assert result.stdout == ""
    assert "Traceback" not in result.output
    assert list(tmp_path.rglob(".*.tmp")) == []
    if failure in {"stdin", "schema"}:
        assert not output_dir.exists()
    elif failure == "mkdir":
        assert blocked_parent is not None
        assert not output_dir.exists()
        assert blocked_parent.is_file()
        assert blocked_parent.read_text(encoding="utf-8") == "not a directory"
    elif failure == "collision":
        assert (output_dir / "1000-test-packet-for-init.json").read_text(
            encoding="utf-8"
        ) == "keep existing content"
        assert len(list(output_dir.iterdir())) == 1
    else:
        assert output_dir.is_dir()
        assert list(output_dir.iterdir()) == []


def test_help_works() -> None:
    """Verify the CLI help option succeeds and names the command."""
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "init-task-packet" in result.output
