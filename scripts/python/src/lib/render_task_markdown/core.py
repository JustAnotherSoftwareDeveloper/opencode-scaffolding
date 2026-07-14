"""Render a validated BreakdownTasksOutput document as Markdown."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path
from typing import Any

from lib.schema import load_schema
from lib.shared.schema import validate_json_schema

OPENCODE_CONFIG_DIR = Path.home() / ".config" / "opencode"
OUTPUT_SCHEMA_PATH = (
    OPENCODE_CONFIG_DIR
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)


class RenderValidationError(ValueError):
    """Raised when renderer input or output paths are invalid."""


def render_task_markdown(
    data: dict[str, Any],
    output_file: Path,
) -> Path:
    """Validate *data* and atomically write its Markdown representation."""
    errors = validate_json_schema(data, load_schema(OUTPUT_SCHEMA_PATH))
    if errors:
        raise RenderValidationError(
            f"input failed BreakdownTasksOutput schema: {errors}"
        )
    if output_file.suffix != ".md":
        raise RenderValidationError("output file must use a .md suffix")
    _write_text_new(output_file, _render(data))
    return output_file


def _render(data: dict[str, Any]) -> str:
    """Return the deterministic Markdown content for one task packet."""
    lines = [
        "# Task Plan",
        "",
        "## Summary",
        "",
        data["summary"],
    ]
    for index, task in enumerate(data["tasks"], start=1):
        lines.extend(
            [
                "",
                f"## Task {index}: {_inline_text(task['purpose'])}",
                "",
                "### Context",
                "",
                task["context"],
            ]
        )
        for heading, key in (
            ("Files To Read", "filesToRead"),
            ("Files To Write", "filesToWrite"),
            ("Skills", "skills"),
        ):
            lines.extend(["", f"### {heading}", ""])
            lines.extend([f"- `{item}`" for item in task[key]] or ["- None."])
        lines.extend(["", "### Execution Instructions", ""])
        for step in task["executionInstructions"]:
            lines.append(f"{step['step']}. {_inline_text(step['action'])}")
            if "verification" in step:
                lines.append(f"   Verification: {_inline_text(step['verification'])}")
        if "verification" in task:
            lines.extend(["", "### Verification", ""])
            lines.extend(f"- {item}" for item in task["verification"])
        lines.extend(["", "### Expected Output", "", task["expectedOutput"]])
    return "\n".join(lines) + "\n"


def _inline_text(value: str) -> str:
    """Render one user-controlled value without introducing Markdown lines."""
    return value.replace("\\", "\\\\").replace("\r", " ").replace("\n", " ")


def _write_text_new(path: Path, text: str) -> None:
    """Atomically create *path* without replacing an existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Output file already exists: {path}")
    descriptor, temporary_path = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.tmp_"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output_file:
            output_file.write(text)
        os.link(temporary_path, path)
        os.unlink(temporary_path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary_path)
        raise
