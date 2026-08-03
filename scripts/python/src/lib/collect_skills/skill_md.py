"""Read and normalize a skill's SKILL.md frontmatter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata

from .models import Skill


def extract_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter, returning ``None`` for an absent block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None
    try:
        end = next(
            index
            for index in range(1, len(lines))
            if lines[index].rstrip() == "---"
        )
    except StopIteration:
        return None
    value = yaml.safe_load("\n".join(lines[1:end]))
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    return dict(value)


def parse_skill_md(path: Path, source: str) -> Skill | None:
    """Return a collector record, or ``None`` for any malformed profile.

    Failing closed here prevents partially populated records from reaching
    discovery or inventory validation.
    """
    try:
        raw = extract_frontmatter(path)
        if raw is None:
            return None
        metadata = normalize_skill_metadata(raw)
    except (OSError, ValueError, yaml.YAMLError, SkillMetadataError):
        return None
    return Skill(
        name=metadata.name,
        description=metadata.description,
        selection=metadata.selection,
        class_=metadata.skill_class,
        path=str(path.resolve()),
        source=source,
        **metadata.optional,
    )


# Clear aliases for callers that use parser terminology.
parse_skill = parse_skill_md
load_skill_md = parse_skill_md
