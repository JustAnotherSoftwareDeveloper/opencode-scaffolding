"""Tests for the task-packet Markdown renderer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from lib.render_task_markdown import core
from lib.render_task_markdown.core import RenderValidationError, render_task_markdown

VALID_CONTEXT = "x" * 200


def _packet() -> dict:
    return {
        "summary": "Render a plan.",
        "tasks": [
            {
                "purpose": "Render Markdown.",
                "context": VALID_CONTEXT,
                "filesToRead": ["memo/memo.md"],
                "filesToWrite": ["tasks.md"],
                "skills": ["documentation"],
                "executionInstructions": [{"step": 1, "action": "Render the task."}],
                "expectedOutput": "Markdown task plan.",
            }
        ],
    }


def test_render_task_markdown_writes_packet_content(tmp_path: Path) -> None:
    output = render_task_markdown(
        _packet(),
        tmp_path / "tasks.md",
    )
    content = output.read_text()
    assert output == tmp_path / "tasks.md"
    assert "## Task 1: Render Markdown." in content
    assert content.startswith("# Task Plan\n")


def test_render_task_markdown_renders_verification_and_normalizes_input(
    tmp_path: Path,
) -> None:
    packet = _packet()
    packet["tasks"][0]["purpose"] = "Render\nMarkdown"
    packet["tasks"][0]["verification"] = ["Check output."]
    packet["tasks"][0]["executionInstructions"][0]["verification"] = "Check step."
    output = render_task_markdown(
        packet,
        tmp_path / "tasks.md",
    )
    content = output.read_text()
    assert "## Task 1: Render Markdown" in content
    assert "Verification: Check step." in content
    assert "### Verification" in content


def test_render_task_markdown_rejects_invalid_packet(tmp_path: Path) -> None:
    with pytest.raises(RenderValidationError, match="schema"):
        render_task_markdown(
            {"summary": "bad", "tasks": []},
            tmp_path / "tasks.md",
        )


def test_render_task_markdown_rejects_non_markdown_output(tmp_path: Path) -> None:
    with pytest.raises(RenderValidationError, match=".md suffix"):
        render_task_markdown(
            _packet(),
            tmp_path / "tasks.txt",
        )


def test_render_task_markdown_does_not_replace_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "tasks.md"
    output.write_text("preserve\n")
    with pytest.raises(FileExistsError, match="already exists"):
        render_task_markdown(
            _packet(),
            output,
        )
    assert output.read_text() == "preserve\n"


def test_write_text_new_cleans_up_after_link_failure(tmp_path: Path) -> None:
    output = tmp_path / "tasks.md"
    with (
        patch("lib.render_task_markdown.core.os.link", side_effect=OSError("boom")),
        pytest.raises(OSError, match="boom"),
    ):
        core._write_text_new(output, "content\n")
    assert list(tmp_path.glob(".tasks.md.tmp_*")) == []
