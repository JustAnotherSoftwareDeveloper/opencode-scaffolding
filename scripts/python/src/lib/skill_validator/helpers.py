"""Constants and helper utilities for skill validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CLASSES = frozenset(
    {
        "operation",
        "delegated",
        "inline",
        "planning",
        "documentation",
    }
)

PLANNING_DESCRIPTION_PREFIX = "Use as planning reference"
DEFAULT_DESCRIPTION_PREFIX = "Use when"

PASSIVE_VOICE_PATTERNS = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+\w+ed\b"
    r"|\bshould\b"
    r"|\bmay\b"
    r"|\bcould\b"
    r"|\bmight\b"
    r"|\b(must\s+be\s+\w+ed)\b"
    r"|\b(is\s+used)\b"
    r"|\b(will\s+be)\b",
    re.IGNORECASE,
)

PLACEHOLDER_PATTERN = re.compile(r"<<[^>]+>>")

RELATIVE_LINK_PATTERN = re.compile(r"\]\(\./.*?\.md(?:\#.*?)?\)")

SENTENCE_END_PATTERN = re.compile(r"[.!?][\s'\u2019\u201d]")


def _is_in_skip_directory(
    file_path: Path, skill_dir: Path, dirs: frozenset[str]
) -> bool:
    """Check if a file resides within one of the given subdirectories of skill_dir."""
    try:
        rel = file_path.relative_to(skill_dir)
    except ValueError:
        return False
    return len(rel.parts) > 1 and rel.parts[0] in dirs


def _read_skill_md(skill_dir: Path) -> str | None:
    """Return the content of SKILL.md, or None if missing."""
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Parse YAML frontmatter from SKILL.md content.

    Returns the parsed dict or None on failure.
    """
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None
    try:
        return dict(yaml.safe_load(m.group(1)) or {})
    except yaml.YAMLError:
        return None
