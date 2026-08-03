"""Package marker for the collect_skills module."""

from __future__ import annotations

from lib.shared.skill_metadata import (
    SelectionProfile,
    SelectionTags,
    normalize_skill_metadata,
)

from .models import Skill, SkillIndex
from .parser import extract_frontmatter, validate_skill_frontmatter

__all__ = [
    "SelectionProfile",
    "SelectionTags",
    "Skill",
    "SkillIndex",
    "extract_frontmatter",
    "normalize_skill_metadata",
    "validate_skill_frontmatter",
]
