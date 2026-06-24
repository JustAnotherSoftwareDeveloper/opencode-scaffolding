#!/usr/bin/env python3
"""Validate execution-focused plan workspaces."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import click
import yaml


NAME_RE = re.compile(r"^[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
VALID_STATUSES = {"draft", "approved", "superseded"}
REQUIRED_FILES = [
    "INDEX.md",
    "metadata.md",
    "source.md",
    "execution-overview.md",
    "constraints.md",
    "file-impact.md",
    "implementation-notes.md",
    "validation.md",
    "rollback-recovery.md",
    "handoff.md",
]
REJECTED_FILES = [
    "problem-opportunity.md",
    "alternatives-considered.md",
    "risks-and-unknowns.md",
]

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class CheckResult:
    ok: bool
    messages: list[str]


def _repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_frontmatter(markdown_file: Path) -> tuple[dict[str, object], str]:
    """Parse YAML frontmatter from a markdown file."""
    text = markdown_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter block")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("unterminated YAML frontmatter block") from exc
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, body


def validate_path_shape(entry_path: Path) -> CheckResult:
    """Validate that entry path matches .plans/<id>/INDEX.md pattern."""
    messages: list[str] = []

    if not entry_path.name == "INDEX.md":
        return CheckResult(False, [f"entry file must be INDEX.md, got {entry_path.name}"])

    parts = entry_path.parts
    if len(parts) < 3 or parts[-2] != ".plans" or not parts[-1] == "INDEX.md":
        messages.append(f"path shape must end with .plans/<id>/INDEX.md")

    # Check that path starts with .plans (relative to repo root for consistency)
    if ".plans" not in parts:
        return CheckResult(False, [f"entry path should be under .plans directory"])

    workspace_root = entry_path.parent

    return CheckResult(True, [str(workspace_root)])


def validate_required_files(workspace_root: Path) -> CheckResult:
    """Validate that all required files exist under workspace root."""
    messages: list[str] = []
    ok = True

    for filename in REQUIRED_FILES:
        file_path = workspace_root / filename
        if not file_path.exists():
            messages.append(f"missing required file: {filename}")
            ok = False

    return CheckResult(ok, messages)


def validate_rejected_files(workspace_root: Path) -> CheckResult:
    """Check that proposal-specific files are not present."""
    messages: list[str] = []
    found: list[str] = []

    for filename in REJECTED_FILES:
        file_path = workspace_root / filename
        if file_path.exists():
            found.append(filename)
            messages.append(f"proposal-specific file not allowed in plan workspace: {filename}")

    return CheckResult(len(found) == 0, messages)


def validate_tasks_directory(workspace_root: Path) -> CheckResult:
    """Validate tasks/ directory exists and contains valid task files."""
    messages: list[str] = []
    tasks_dir = workspace_root / "tasks"

    if not tasks_dir.exists():
        return CheckResult(False, ["missing required directory: tasks/"])

    if not tasks_dir.is_dir():
        return CheckResult(False, ["tasks must be a directory"])

    task_files = list(tasks_dir.glob("*.md"))
    if not task_files:
        return CheckResult(False, ["tasks/ must contain at least one markdown file"])

    invalid_names: list[str] = []
    for task_file in task_files:
        if not NAME_RE.match(task_file.name):
            invalid_names.append(f"{task_file.name} (must match pattern XX-description.md)")

    if invalid_names:
        messages.append("invalid task file names:")
        for name in invalid_names:
            messages.append(f"  - {name}")
        return CheckResult(False, messages)

    return CheckResult(True, [f"tasks/ directory valid with {len(task_files)} tasks"])


def validate_index_toc(workspace_root: Path) -> CheckResult:
    """Validate INDEX.md is TOC-only (no frontmatter)."""
    index_file = workspace_root / "INDEX.md"

    if not index_file.exists():
        return CheckResult(False, ["INDEX.md not found"])

    messages: list[str] = []
    try:
        data, body = parse_frontmatter(index_file)
        return CheckResult(False, [f"INDEX.md must be TOC-only without YAML frontmatter (found {len(data)} fields)"])
    except ValueError:
        # Expected - no frontmatter is OK
        pass

    # Additional check: INDEX should have some content
    text = index_file.read_text(encoding="utf-8")
    if not text.strip():
        return CheckResult(False, ["INDEX.md must not be empty"])

    return CheckResult(True, ["INDEX.md valid (TOC-only)"])


def validate_metadata_frontmatter(workspace_root: Path) -> CheckResult:
    """Validate metadata.md has required YAML frontmatter fields."""
    messages: list[str] = []
    metadata_file = workspace_root / "metadata.md"

    if not metadata_file.exists():
        return CheckResult(False, ["metadata.md not found"])

    try:
        data, body = parse_frontmatter(metadata_file)
    except Exception as exc:
        return CheckResult(False, [f"metadata.md frontmatter error: {exc}"])

    required_fields = ["id", "title", "status", "created_at", "updated_at", "proposal"]
    for field in required_fields:
        if field not in data:
            messages.append(f"missing metadata field: {field}")

    status = data.get("status")
    if status is not None and status not in VALID_STATUSES:
        messages.append(f"metadata.status must be one of {VALID_STATUSES}, got '{status}'")

    return CheckResult(len(messages) == 0, messages or [f"metadata.md valid"])


def validate_plan(plan_path: Path) -> CheckResult:
    """Run all validations on a plan workspace."""
    path_result = validate_path_shape(plan_path)
    if not path_result.ok:
        return path_result

    # Extract the messages (workspace root or error) from first result
    workspace_root = Path(path_result.messages[0]) if path_result.messages else plan_path.parent

    all_messages: list[str] = []
    ok = True

    validators = [
        ("required files", validate_required_files),
        ("rejected files", validate_rejected_files),
        ("tasks directory", lambda p: validate_tasks_directory(p)),
        ("INDEX.md TOC", lambda p: validate_index_toc(p)),
        ("metadata frontmatter", lambda p: validate_metadata_frontmatter(p)),
    ]

    for name, validator in validators:
        result = validator(workspace_root)
        all_messages.extend(result.messages)
        ok = ok and result.ok

    return CheckResult(ok, ["=== Plan Workspace Validation ==="] + all_messages if not ok else ["✓ Plan workspace is valid"])


@click.command(name="validate-plan")
@click.argument(
    "entry_path",
    type=click.Path(exists=True, readable=True),
)
def cli(entry_path: str) -> None:
    """Validate an execution-focused plan workspace.

    ENTRY_PATH is the path to INDEX.md
    (e.g., .plans/1780663143-upgrade-plan-workspace-validation/INDEX.md).
    """
    path = Path(entry_path)

    if not path.exists():
        click.echo(f"Error: file not found: {path}", err=True)
        raise SystemExit(1)

    result = validate_plan(path)

    for message in result.messages:
        click.echo(message)

    raise SystemExit(0 if result.ok else 1)


if __name__ == "__main__":
    cli()