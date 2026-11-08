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
    r"|\b(?:you|we)\s+(?:may|could|might)\b"
    r"|\b(must\s+be\s+\w+ed)\b"
    r"|\b(is\s+used)\b"
    r"|\b(will\s+be)\b",
    re.IGNORECASE,
)

# Conditional clauses qualify a directive rather than replacing its main clause.
# Non-finite passive complements ("to be reviewed") likewise do not make the
# finite clause passive. Neither rule exempts a finite passive main clause.
CONDITIONAL_CLAUSE_PATTERN = re.compile(
    r"\b(?:when|if|unless|where)\b.*$", re.IGNORECASE
)
CONDITIONAL_START_PATTERN = re.compile(
    r"^\s*(?:when|if|unless|where)\b", re.IGNORECASE
)
CONDITIONAL_END_PATTERN = re.compile(
    r"\b(?:when|if|unless|where)\s*$", re.IGNORECASE
)
NONFINITE_PASSIVE_PATTERN = re.compile(r"\bto\s+be\s+\w+ed\b", re.IGNORECASE)
# A demonstrative copula plus a participial noun phrase commonly states a fact
# ("These are proposed alternatives"), rather than assigning an action.
DESCRIPTIVE_COPULA_PATTERN = re.compile(
    r"\b(?:this|these|that|those)\s+(?:is|are|was|were)\s+\w+ed\s+(?=\w+)",
    re.IGNORECASE,
)

PLACEHOLDER_PATTERN = re.compile(r"<<[^>]+>>")

RELATIVE_LINK_PATTERN = re.compile(r"\]\(\./.*?\.md(?:\#.*?)?\)")


def _is_in_skip_directory(
    file_path: Path, skill_dir: Path, dirs: frozenset[str]
) -> bool:
    """Check whether a file resides in a named subdirectory of *skill_dir*."""
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
