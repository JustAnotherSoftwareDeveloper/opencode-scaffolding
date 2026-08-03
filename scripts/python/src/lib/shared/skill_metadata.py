"""The hard-cut, readable metadata contract for skills."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

SkillRole = Literal["owner", "support", "reference"]
SkillClass = Literal[
    "operation", "delegated", "inline", "planning", "documentation"
]
TAG_GROUPS = ("actions", "inputs", "outputs", "topics", "environments", "constraints")
OPTIONAL_FIELDS = ("version", "license", "compatibility", "metadata", "permission")
_NAME = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_ROOT = {"name", "description", "selection", "class", *OPTIONAL_FIELDS}
_SELECTION = {"role", "tags", "use_when", "not_for", "supports"}
_OBSOLETE = {
    "schema_version",
    "cues",
    "relationships",
    "facets",
    "routing",
    "location",
    "score",
    "rank",
    "threshold",
}


class SkillMetadataError(ValueError):
    """Raised when a skill profile violates the direct-selection contract."""


@dataclass(frozen=True)
class SelectionTags:
    actions: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    topics: tuple[str, ...] = ()
    environments: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, list[str]]:
        return {
            group: list(getattr(self, group))
            for group in TAG_GROUPS
            if getattr(self, group)
        }


@dataclass(frozen=True)
class SelectionProfile:
    role: SkillRole
    tags: SelectionTags
    use_when: tuple[str, ...] = ()
    not_for: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"role": self.role, "tags": self.tags.to_dict()}
        for key, value in (
            ("use_when", self.use_when),
            ("not_for", self.not_for),
            ("supports", self.supports),
        ):
            if value:
                result[key] = list(value)
        return result


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    selection: SelectionProfile
    skill_class: SkillClass
    optional: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        result = {
            "name": self.name,
            "description": self.description,
            "selection": self.selection.to_dict(),
            "class": self.skill_class,
        }
        result.update(self.optional)
        return result


def _text(value: Any, field: str, max_length: int = 128) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise SkillMetadataError(f"{field} must be a trimmed single-line string")
    if len(value) > max_length:
        raise SkillMetadataError(f"{field} exceeds {max_length} characters")
    return value


def _items(value: Any, field: str, *, names: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise SkillMetadataError(f"{field} must be a non-empty string array")
    if len(value) > 32:
        raise SkillMetadataError(f"{field} exceeds 32 entries")
    result = tuple(_text(item, field) for item in value)
    if len(set(result)) != len(result):
        raise SkillMetadataError(f"{field} must be unique")
    if names and any(not _NAME.fullmatch(item) for item in result):
        raise SkillMetadataError(f"{field} must contain canonical skill names")
    return result


def normalize_skill_metadata(data: Mapping[str, Any]) -> SkillMetadata:
    """Validate and normalize a profile, preserving authored array order."""
    if not isinstance(data, Mapping):
        raise SkillMetadataError("skill metadata must be an object")
    obsolete = set(data) & _OBSOLETE
    if obsolete:
        raise SkillMetadataError(
            f"obsolete metadata fields: {', '.join(sorted(obsolete))}"
        )
    unknown = set(data) - _ROOT
    if unknown:
        raise SkillMetadataError(
            f"unknown metadata fields: {', '.join(sorted(unknown))}"
        )
    name = _text(data.get("name"), "name")
    if not _NAME.fullmatch(name):
        raise SkillMetadataError("name must be a canonical skill name")
    description = _text(data.get("description"), "description", 1024)
    skill_class = data.get("class")
    if skill_class not in (
        "operation",
        "delegated",
        "inline",
        "planning",
        "documentation",
    ):
        raise SkillMetadataError("class must be a canonical skill class")
    raw_selection = data.get("selection")
    if not isinstance(raw_selection, Mapping):
        raise SkillMetadataError("selection is required and must be an object")
    unknown = set(raw_selection) - _SELECTION
    if unknown:
        raise SkillMetadataError(
            f"unknown selection fields: {', '.join(sorted(unknown))}"
        )
    role = raw_selection.get("role")
    if role not in ("owner", "support", "reference"):
        raise SkillMetadataError("selection.role must be owner, support, or reference")
    raw_tags = raw_selection.get("tags")
    if not isinstance(raw_tags, Mapping) or not raw_tags:
        raise SkillMetadataError("selection.tags must contain at least one tag group")
    unknown = set(raw_tags) - set(TAG_GROUPS)
    if unknown:
        raise SkillMetadataError(f"unknown tag groups: {', '.join(sorted(unknown))}")
    tags = SelectionTags(
        **{group: _items(raw_tags[group], f"tags.{group}") for group in raw_tags}
    )
    conditions = {
        key: _items(raw_selection[key], f"selection.{key}")
        for key in ("use_when", "not_for")
        if key in raw_selection
    }
    supports = (
        _items(raw_selection["supports"], "selection.supports", names=True)
        if "supports" in raw_selection
        else ()
    )
    if name in supports:
        raise SkillMetadataError("selection.supports cannot contain the skill itself")
    optional: dict[str, Any] = {}
    for key in OPTIONAL_FIELDS:
        if key in data:
            value = data[key]
            if key == "metadata":
                if not isinstance(value, Mapping):
                    raise SkillMetadataError("metadata must be an object")
                optional[key] = dict(value)
            else:
                optional[key] = _text(value, key, 256)
    return SkillMetadata(
        name,
        description,
        SelectionProfile(
            role,
            tags,
            conditions.get("use_when", ()),
            conditions.get("not_for", ()),
            supports,
        ),
        skill_class,
        optional,
    )


def load_skill_metadata_schema(path: Path | None = None) -> dict[str, Any]:
    """Load the published machine-readable schema."""
    schema = path or Path(__file__).with_name("skill-selection.schema.json")
    return json.loads(schema.read_text(encoding="utf-8"))
