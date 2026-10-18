"""Read and normalize a skill's SKILL.md frontmatter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from lib.skill_metadata import SkillMetadataError, normalize_skill_metadata

from .models import Skill
from .parser import extract_frontmatter as _extract_frontmatter


def extract_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter, returning ``None`` for an absent block."""
    try:
        return _extract_frontmatter(path)
    except UnicodeDecodeError:
        raise
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter must be a mapping") from exc


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
