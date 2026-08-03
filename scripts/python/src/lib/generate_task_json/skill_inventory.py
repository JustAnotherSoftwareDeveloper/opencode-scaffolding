"""Fail-closed validation and freezing of collector skill snapshots."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, overload

from lib.shared.skill_class import SkillClass
from lib.shared.skill_metadata import (
    OPTIONAL_FIELDS,
    SelectionProfile,
    normalize_skill_metadata,
)

REQUIRED_FIELDS = frozenset(
    {"name", "description", "selection", "class", "path", "source"}
)
ALLOWED_SOURCES = frozenset({"project", "global"})
ALLOWED_CLASSES = frozenset(
    {SkillClass.OPERATION.value, SkillClass.DOCUMENTATION.value}
)
_OPTIONAL_FIELDS = frozenset(OPTIONAL_FIELDS)


class SkillInventoryError(ValueError):
    """Raised when a collector snapshot is not safe to pass to a generator."""


@dataclass(frozen=True, slots=True)
class FrozenSkillRecord:
    """One immutable, normalized collector record."""

    name: str
    description: str
    selection: SelectionProfile
    skill_class: str
    path: Path
    source: str
    optional: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "selection": self.selection.to_dict(),
            "class": self.skill_class,
            "path": str(self.path),
            "source": self.source,
        }
        result.update(self.optional)
        return result


@dataclass(frozen=True, slots=True)
class FrozenSkillInventory(Sequence[FrozenSkillRecord]):
    """An immutable snapshot, retaining collector order and record values."""

    records: tuple[FrozenSkillRecord, ...]

    def __len__(self) -> int:
        return len(self.records)

    @overload
    def __getitem__(self, index: int) -> FrozenSkillRecord: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[FrozenSkillRecord, ...]: ...

    def __getitem__(
        self, index: int | slice
    ) -> FrozenSkillRecord | tuple[FrozenSkillRecord, ...]:
        return self.records[index]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(record.name for record in self.records)


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def validate_skill_inventory(
    inventory: object,
    *,
    project_root: Path | None = None,
    global_root: Path | None = None,
    source_roots: Mapping[str, Sequence[Path | str]] | None = None,
) -> FrozenSkillInventory:
    """Validate and freeze exactly one non-empty collector snapshot.

    This function performs no discovery, scoring, repair, or support-target
    lookup.  ``supports`` is checked by the shared metadata validator only.
    """
    if not isinstance(inventory, list) or not inventory:
        raise SkillInventoryError("skill inventory must be a non-empty array")

    roots: dict[str, tuple[Path, ...]] = {
        "global": (global_root or Path.home() / ".config" / "opencode",),
        "project": (project_root,) if project_root is not None else (),
    }
    if source_roots is not None:
        roots = {
            source: tuple(Path(root).resolve() for root in values)
            for source, values in source_roots.items()
        }
    normalized: list[FrozenSkillRecord] = []
    seen: set[str] = set()
    for index, raw in enumerate(inventory):
        if not isinstance(raw, Mapping):
            raise SkillInventoryError(f"inventory record {index} must be an object")
        keys = set(raw)
        if not keys >= REQUIRED_FIELDS:
            missing = sorted(REQUIRED_FIELDS - keys)
            raise SkillInventoryError(
                f"inventory record {index} missing fields: {missing}"
            )
        allowed = REQUIRED_FIELDS | _OPTIONAL_FIELDS
        extra = keys - allowed
        if extra:
            raise SkillInventoryError(
                f"inventory record {index} has unknown fields: {sorted(extra)}"
            )

        profile_data = {key: raw[key] for key in keys if key not in {"path", "source"}}
        try:
            profile = normalize_skill_metadata(profile_data)
        except ValueError as exc:
            raise SkillInventoryError(f"inventory record {index}: {exc}") from exc
        if profile.name in seen:
            raise SkillInventoryError(f"duplicate skill name: {profile.name}")
        seen.add(profile.name)

        source = raw["source"]
        if not isinstance(source, str) or source not in ALLOWED_SOURCES:
            raise SkillInventoryError(f"inventory record {index} has invalid source")
        if profile.skill_class not in ALLOWED_CLASSES:
            raise SkillInventoryError(f"inventory record {index} has invalid class")
        raw_path = raw["path"]
        if (
            not isinstance(raw_path, str)
            or not raw_path
            or not Path(raw_path).is_absolute()
        ):
            raise SkillInventoryError(f"inventory record {index} path must be absolute")
        path = Path(raw_path)
        try:
            resolved = path.resolve(strict=True)
        except OSError as exc:
            raise SkillInventoryError(
                f"inventory record {index} path does not exist"
            ) from exc
        if resolved.name != "SKILL.md" or not resolved.is_file():
            raise SkillInventoryError(
                f"inventory record {index} path must be an existing SKILL.md"
            )
        if not any(_inside(resolved, root) for root in roots.get(source, ())):
            raise SkillInventoryError(
                f"inventory record {index} path is outside its source root"
            )

        normalized.append(
            FrozenSkillRecord(
                profile.name,
                profile.description,
                profile.selection,
                profile.skill_class,
                resolved,
                source,
                MappingProxyType(
                    {key: _freeze(value) for key, value in profile.optional.items()}
                ),
            )
        )
    return FrozenSkillInventory(tuple(normalized))


# Short alias for callers that name the boundary after its input.
freeze_skill_inventory = validate_skill_inventory
