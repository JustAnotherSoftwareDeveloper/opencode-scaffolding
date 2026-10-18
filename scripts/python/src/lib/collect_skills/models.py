"""The collector's normalized skill record and deterministic index."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from lib.skill_metadata import SelectionProfile

SOURCE_PRIORITY: dict[str, int] = {
    "project": 5,
    "extra": 4,
    "global": 3,
    "archive": 2,
}
_LOCATION_PRIORITY = {
    ".opencode/skills/": 3,
    ".claude/skills/": 2,
    ".agents/skills/": 1,
}


@dataclass
class Skill:
    """A normalized collector record.

    ``path`` and ``source`` are collector-owned values, never frontmatter
    values.  The legacy constructor fields are retained only so callers from
    the discovery migration can be upgraded independently; they are never
    projected into JSON.
    """

    name: str
    description: str = ""
    selection: SelectionProfile | None = None
    class_: str = ""
    path: str = ""
    source: str = ""
    version: str = ""
    license: str = ""
    compatibility: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    permission: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Project exactly six required keys plus authored optionals."""
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "selection": self.selection.to_dict() if self.selection else {},
            "class": self.class_,
            "path": self.path,
            "source": self.source,
        }
        for key in ("version", "license", "compatibility", "permission"):
            value = getattr(self, key)
            if value:
                result[key] = value
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class SkillIndex:
    """A deterministic, precedence-aware collection of skill records."""

    def __init__(self) -> None:
        """Initialize empty skill and warning collections."""
        self._skills: dict[str, Skill] = {}
        self._warnings: list[str] = []

    @staticmethod
    def _source_priority(source: str, location: str = "") -> tuple[int, int]:
        source_rank = SOURCE_PRIORITY.get(source, 0)
        location_rank = max(
            (
                rank
                for marker, rank in _LOCATION_PRIORITY.items()
                if marker in location
            ),
            default=0,
        )
        return source_rank, location_rank

    def add(self, skill: Skill) -> None:
        """Add *skill*, retaining the higher-precedence record on conflicts."""
        existing = self._skills.get(skill.name)
        if existing is None:
            self._skills[skill.name] = skill
            return
        new_rank = self._source_priority(skill.source, skill.path)
        old_rank = self._source_priority(existing.source, existing.path)
        if new_rank > old_rank:
            self._warnings.append(
                f"Shadowing '{skill.name}': {existing.source}/{existing.path} "
                f"replaced by {skill.source}/{skill.path}"
            )
            self._skills[skill.name] = skill
        elif new_rank < old_rank:
            self._warnings.append(
                f"Shadowing '{skill.name}': {skill.source}/{skill.path} "
                f"hidden by {existing.source}/{existing.path}"
            )

    def resolve(self) -> list[Skill]:
        """Return the winning skill records sorted by skill name."""
        return sorted(self._skills.values(), key=lambda skill: skill.name)

    def filter_by_classes(self, class_filters: tuple[str, ...]) -> list[Skill]:
        """Return winning records whose class appears in *class_filters*."""
        allowed = set(class_filters)
        return [skill for skill in self.resolve() if skill.class_ in allowed]

    def to_json(self) -> str:
        """Serialize the resolved skill records as JSON."""
        return json.dumps([skill.to_dict() for skill in self.resolve()])

    @property
    def warnings(self) -> list[str]:
        """Return a copy of precedence warnings collected during insertion."""
        return list(self._warnings)
