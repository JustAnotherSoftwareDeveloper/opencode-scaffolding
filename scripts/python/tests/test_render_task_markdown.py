"""Tests for the task-packet Markdown renderer."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from lib.render_task_markdown import core
from lib.render_task_markdown.core import (
    RenderValidationError,
    render_task_markdown,
)
from lib.shared import schema as shared_schema

pytestmark = pytest.mark.unit

VALID_CONTEXT = "x" * 200


def _packet() -> dict:
    return {
        "summary": "Render a plan.",
        "slug": "render-a-plan",
        "boundaryReview": {
            "requestResultInventory": {
                "render": {
                    "result": "Markdown task plan.",
                    "kind": "immediate",
                    "disposition": "represented-by-task",
                }
            },
            "taskReviews": {
                "render": {
                    "immediateResult": "Markdown task plan.",
                    "predecessorOutputs": [],
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
            },
            "warningDispositions": {},
        },
        "tasks": [
            {
                "taskId": "render",
                "purpose": "Render Markdown.",
                "context": VALID_CONTEXT,
                "filesToRead": ["memo/memo.md"],
                "filesToWrite": ["tasks.md"],
                "skills": ["documentation"],
                "executionInstructions": [
                    {"step": 1, "action": "Render the task."}
                ],
                "expectedOutput": "Markdown task plan.",
                "verificationCoverage": {
                    "observable": ["Markdown output exists."]
                },
                "dependencies": [],
                "antiPatternSignals": ["none"],
                "purposeOutputAlignment": {
                    "status": "aligned",
                    "evidence": "Rendering produces the Markdown task plan.",
                },
            }
        ],
    }


def test_render_task_markdown_renders_valid_full_schema_packet(
    tmp_path: Path,
) -> None:
    """Verify a valid packet passes full validation and renders."""
    assert shared_schema._HAS_JSONSCHEMA
    packet = _packet()
    output = render_task_markdown(
        packet,
        tmp_path / "tasks.md",
    )
    content = output.read_text()
    assert output == tmp_path / "tasks.md"
    assert "## Task 1\n\nPurpose: Render Markdown." in content
    assert content.startswith("# Task Plan\n")
    assert packet["slug"] == "render-a-plan"
    assert "render-a-plan" not in content


def test_render_task_markdown_uses_unique_headings_and_preserves_task_content(
    tmp_path: Path,
) -> None:
    """Verify headings are unique and rendered task content stays intact."""
    packet = _packet()
    second_task = deepcopy(packet["tasks"][0])
    second_task.update(
        {
            "taskId": "review",
            "purpose": "Review the rendered plan.",
            "context": "y" * 200,
            "filesToRead": ["review/source.md"],
            "filesToWrite": ["review/result.md"],
            "skills": ["reviewer"],
            "executionInstructions": [
                {"step": 1, "action": "Review the output."}
            ],
            "verification": ["Confirm the review."],
            "expectedOutput": "A reviewed plan.",
        }
    )
    packet["summary"] = "Render and review a plan."
    packet["tasks"].append(second_task)

    output = render_task_markdown(packet, tmp_path / "tasks.md")

    content = output.read_text()
    headings = [line for line in content.splitlines() if line.startswith("#")]
    assert len(headings) == len(set(headings))
    assert all(
        not heading.endswith((".", "!", "?", ":", ";")) for heading in headings
    )
    assert "Purpose: Render Markdown." in content
    assert "Purpose: Review the rendered plan." in content
    assert content.index("Purpose: Render Markdown.") < content.index(
        "Purpose: Review the rendered plan."
    )
    for expected in (
        "Render and review a plan.",
        VALID_CONTEXT,
        "`memo/memo.md`",
        "`tasks.md`",
        "`documentation`",
        "1. Render the task.",
        "Markdown task plan.",
        "y" * 200,
        "`review/source.md`",
        "`review/result.md`",
        "`reviewer`",
        "1. Review the output.",
        "Confirm the review.",
        "A reviewed plan.",
    ):
        assert expected in content
    assert content.index("### Task 1 Expected Output") < content.index(
        "## Task 2"
    )


def test_render_task_markdown_preserves_purpose_and_renders_verification(
    tmp_path: Path,
) -> None:
    """Verify purpose text and verification content are rendered as provided."""
    packet = _packet()
    packet["tasks"][0]["purpose"] = "Render\nMarkdown"
    packet["tasks"][0]["verification"] = ["Check output."]
    packet["tasks"][0]["executionInstructions"][0]["verification"] = (
        "Check step."
    )
    output = render_task_markdown(
        packet,
        tmp_path / "tasks.md",
    )
    content = output.read_text()
    assert "Purpose: Render\nMarkdown" in content
    assert "Verification: Check step." in content
    assert "### Task 1 Verification" in content


def test_render_task_markdown_rejects_invalid_packet(tmp_path: Path) -> None:
    """Verify invalid packets are rejected without creating output."""
    with pytest.raises(RenderValidationError, match="schema"):
        render_task_markdown(
            {"summary": "bad", "tasks": []},
            tmp_path / "tasks.md",
        )
    assert not (tmp_path / "tasks.md").exists()


def test_render_task_markdown_fails_closed_without_jsonschema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reject a packet before writing when full validation is unavailable."""
    monkeypatch.setattr("lib.shared.schema._HAS_JSONSCHEMA", False)
    packet = _packet()
    output = tmp_path / "tasks.md"

    with pytest.raises(
        RenderValidationError, match="jsonschema is unavailable"
    ):
        render_task_markdown(packet, output)

    assert not output.exists()


def test_render_task_markdown_rejects_malformed_nested_packet_with_jsonschema(
    tmp_path: Path,
) -> None:
    """Reject invalid nested schema data when full validation is available."""
    assert shared_schema._HAS_JSONSCHEMA
    packet = _packet()
    packet["boundaryReview"]["taskReviews"]["render"][
        "acceptanceDisposition"
    ] = "not-accepted"
    output = tmp_path / "tasks.md"

    with pytest.raises(RenderValidationError, match="schema"):
        render_task_markdown(packet, output)

    assert not output.exists()


def test_render_task_markdown_rejects_non_markdown_output(
    tmp_path: Path,
) -> None:
    """Verify the renderer rejects output paths without a Markdown suffix."""
    with pytest.raises(RenderValidationError, match=".md suffix"):
        render_task_markdown(
            _packet(),
            tmp_path / "tasks.txt",
        )


def test_render_task_markdown_does_not_replace_existing_output(
    tmp_path: Path,
) -> None:
    """Verify rendering preserves an existing output unless overwrite is set."""
    output = tmp_path / "tasks.md"
    output.write_text("preserve\n")
    with pytest.raises(FileExistsError, match="already exists"):
        render_task_markdown(
            _packet(),
            output,
        )
    assert output.read_text() == "preserve\n"


def test_render_task_markdown_replaces_existing_output_only_when_requested(
    tmp_path: Path,
) -> None:
    """Verify existing Markdown is replaced only when overwrite is requested."""
    output = tmp_path / "tasks.md"
    output.write_text("stale\n")

    render_task_markdown(_packet(), output, overwrite=True)

    assert output.read_text().startswith("# Task Plan\n")


def test_write_text_new_cleans_up_after_link_failure(tmp_path: Path) -> None:
    """Verify failed atomic publication removes its temporary file."""
    output = tmp_path / "tasks.md"
    with (
        patch(
            "lib.render_task_markdown.core.os.link", side_effect=OSError("boom")
        ),
        pytest.raises(OSError, match="boom"),
    ):
        core._write_text_new(output, "content\n")
    assert list(tmp_path.glob(".tasks.md.tmp_*")) == []
