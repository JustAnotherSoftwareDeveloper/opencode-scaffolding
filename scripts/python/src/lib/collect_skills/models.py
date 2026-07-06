"""Skill data model, index, and flat JSON serialization."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Source precedence
# ---------------------------------------------------------------------------

SourcePriority: dict[str, int] = {
    "project": 5,
    "extra": 4,
    "global": 3,
    "archive": 2,
    "builtin": 1,
}

# Directory-name ordering within the same source label.
_LOCATION_PRIORITY: dict[str, int] = {
    ".opencode/skills/": 3,
    ".claude/skills/": 2,
    ".agents/skills/": 1,
}

# ---------------------------------------------------------------------------
# Skill dataclass
# ---------------------------------------------------------------------------


@dataclass
class Skill:
    """A single discovered skill with all parsed frontmatter fields.

    Fields mirror the on-disk frontmatter keys except:
    * ``class_`` stores the ``class`` key (Python keyword avoidance).
    * ``location`` always holds the discovered path.
    * No ``raw_frontmatter`` or ``frontmatter`` key is kept.
    """

    name: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    class_: str = ""
    version: str = ""
    license: str = ""
    compatibility: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    location: str = ""
    source: str = ""
    permission: str = ""

    # -- internal (not serialised) ----------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a flat dict suitable for JSON output.

        * ``class_`` is renamed to ``class``.
        * ``raw_frontmatter`` / ``frontmatter`` are intentionally absent.
        * ``location`` is always the discovered path.
        """
        d: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "class": self.class_,  # rename for JSON output
            "version": self.version,
            "license": self.license,
            "compatibility": self.compatibility,
            "metadata": self.metadata,
            "path": self.location,
            "source": self.source,
            "permission": self.permission,
        }
        return d


# ---------------------------------------------------------------------------
# SkillIndex – precedence-based dedup and serialisation
# ---------------------------------------------------------------------------


class SkillIndex:
    """Collects skills with source-precedence deduplication.

    Precedence (highest wins):
      ``project`` > ``extra`` > ``global`` > ``archive`` > ``builtin``

    Within the same source label, skills under
    ``.opencode/skills/`` > ``.claude/skills/`` > ``.agents/skills/``.
    """

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._warnings: list[str] = []

    # -- public helpers ---------------------------------------------------

    @staticmethod
    def _source_priority(source: str, location: str = "") -> tuple[int, int]:
        """Return a *source*, *location* priority tuple (larger = higher)."""
        src = SourcePriority.get(source, 0)

        # Find the best-matching location key (longest match wins).
        loc = 0
        if location:
            for key, val in _LOCATION_PRIORITY.items():
                if key in location and val > loc:
                    loc = val

        return src, loc

    # -- add / resolve ----------------------------------------------------

    def add(self, skill: Skill) -> None:
        """Insert *skill*, respecting precedence-based deduplication.

        If a skill with the same ``name`` does not exist it is inserted.
        If it exists the higher-precedence entry wins (the lower one is
        discarded).  A warning is recorded whenever a same-name entry is
        shadowed.
        """
        name = skill.name
        if name not in self._skills:
            self._skills[name] = skill
            return

        existing = self._skills[name]
        new_prio = self._source_priority(skill.source, skill.location)
        old_prio = self._source_priority(existing.source, existing.location)

        if new_prio > old_prio:
            self._warnings.append(
                f"Shadowing '{name}': {existing.source}/{existing.location} "
                f"replaced by {skill.source}/{skill.location}"
            )
            self._skills[name] = skill
        elif new_prio < old_prio:
            self._warnings.append(
                f"Shadowing '{name}': {skill.source}/{skill.location} "
                f"hidden by {existing.source}/{existing.location}"
            )
            # Keep the existing (higher-precedence) entry.
        else:
            # Equal priority – keep the existing entry silently.
            pass

    def resolve(self) -> list[Skill]:
        """Return all winning skills sorted alphabetically by name."""
        return sorted(self._skills.values(), key=lambda s: s.name)

    # -- filtering -------------------------------------------------------

    def filter_by_class(self, class_filter: str) -> list[Skill]:
        """Return resolved skills whose ``class_`` matches *class_filter*.

        Args:
            class_filter: A SkillClass value (e.g. ``"operation"``, ``"planning"``).

        Returns:
            List of matching Skill instances sorted alphabetically by name.
        """
        resolved = self.resolve()
        return sorted(
            [s for s in resolved if s.class_ == class_filter],
            key=lambda s: s.name,
        )

    # -- serialisation ----------------------------------------------------

    def to_json(self) -> str:
        """Serialise resolved skills as a bare JSON array.

        Each element is the flat dict produced by ``Skill.to_dict()``.
        """
        resolved = self.resolve()
        return json.dumps([s.to_dict() for s in resolved])

    @property
    def warnings(self) -> list[str]:
        """Read-only access to accumulated dedup warnings."""
        return list(self._warnings)
