"""Fail-closed discovery of the repository's winning skill inventory."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from lib.collect_skills.models import Skill, SkillIndex
from lib.collect_skills.parser import extract_frontmatter
from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata


def _should_exclude_dir(dir_name: str) -> bool:
    return dir_name in ("node_modules", "__pycache__") or dir_name.startswith(
        (".", "_")
    )


def find_git_root(path: Path) -> Path | None:
    current = path.resolve()
    for parent in (current, *current.parents):
        if (parent / ".git").is_dir():
            return parent
        if parent == parent.parent:
            break
    return None


def get_standard_search_roots(
    project_root: Path, config_dir: Path
) -> list[tuple[Path, str]]:
    roots: list[tuple[Path, str]] = []
    candidates = [
        *(
            project_root / part / "skills"
            for part in (".opencode", ".claude", ".agents")
        ),
        (config_dir / "skills"),
        (config_dir.parent / ".claude" / "skills"),
        (config_dir.parent / ".agents" / "skills"),
    ]
    for position, root in enumerate(candidates):
        if root.is_dir():
            roots.append((root, "project" if position < 3 else "global"))
    return roots


def _error(index: SkillIndex, message: str, verbose: bool) -> None:
    errors = getattr(index, "_discovery_errors", None)
    if errors is None:
        errors = []
        index._discovery_errors = errors  # type: ignore[attr-defined]
    errors.append(message)
    if verbose:
        print(f"[collect-skills] Error: {message}", file=sys.stderr)


def _within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def discover_skills_from_root(
    root: Path,
    source: str,
    index: SkillIndex,
    verbose: bool = False,
    registry: Any = None,  # retained for callers during the parser migration
) -> None:
    """Collect every valid entry under *root*, aggregating all failures."""
    del registry
    if source == "builtin":
        _error(index, "built-in skill sources are no longer supported", verbose)
        return
    if not root.exists():
        if verbose:
            print(
                f"[collect-skills] Warning: search root does not exist: {root}",
                file=sys.stderr,
            )
        return
    if not root.is_dir():
        _error(index, f"search root is not a directory: {root}", verbose)
        return
    root = root.resolve()
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        _error(index, f"cannot read search root {root}: {exc}", verbose)
        return

    visited: set[Path] = set()
    for entry in entries:
        if _should_exclude_dir(entry.name) or (
            not entry.is_dir() and not entry.is_symlink()
        ):
            continue
        try:
            skill_dir = entry.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            _error(index, f"cannot resolve {entry}: {exc}", verbose)
            continue
        if not _within(skill_dir, root):
            _error(index, f"skill path escapes search root: {entry}", verbose)
            continue
        if skill_dir in visited:
            continue
        visited.add(skill_dir)
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            if skill_file.is_symlink():
                _error(
                    index,
                    f"skill file is an invalid symlink: {skill_file}",
                    verbose,
                )
            continue
        if not _within(skill_file, root):
            _error(index, f"skill file escapes search root: {skill_file}", verbose)
            continue
        try:
            frontmatter = extract_frontmatter(skill_file)
            if frontmatter is None:
                raise ValueError("missing frontmatter")
            metadata = normalize_skill_metadata(frontmatter)
        except (OSError, ValueError, SkillMetadataError, yaml.YAMLError) as exc:
            _error(index, f"{skill_file}: invalid skill metadata: {exc}", verbose)
            continue
        optional = dict(metadata.optional)
        skill = Skill(
                name=metadata.name,
                description=metadata.description,
                selection=metadata.selection,
                class_=metadata.skill_class,
                path=str(skill_file.resolve()),
                source=source,
                version=str(optional.pop("version", "")),
                license=str(optional.pop("license", "")),
                compatibility=str(optional.pop("compatibility", "")),
                metadata=optional.pop("metadata", {}),
                permission=str(optional.pop("permission", "")),
            )
        index.add(skill)
        candidates = getattr(index, "_discovery_candidates", None)
        if candidates is None:
            candidates = {}
            index._discovery_candidates = candidates  # type: ignore[attr-defined]
        candidates.setdefault(skill.name, []).append(skill)


def _finalize(index: SkillIndex) -> None:
    """Finalize discovery-owned candidates without widening the model API."""
    errors: list[str] = getattr(index, "_discovery_errors", [])
    candidates: dict[str, list[Skill]] = getattr(index, "_discovery_candidates", {})
    for name, values in candidates.items():
        ranked = sorted(
            values,
            key=lambda item: index._source_priority(item.source, item.path),  # noqa: SLF001
            reverse=True,
        )
        if len(ranked) > 1 and index._source_priority(  # noqa: SLF001
            ranked[0].source, ranked[0].path
        ) == index._source_priority(ranked[1].source, ranked[1].path):  # noqa: SLF001
            errors.append(
                f"conflicting equal-precedence skills named {name!r}: "
                f"{ranked[0].path} and {ranked[1].path}"
            )
    winners = {skill.name: skill for skill in index.resolve()}
    for skill in winners.values():
        if skill.selection:
            for target in skill.selection.supports:
                if target not in winners:
                    errors.append(
                        f"skill {skill.name!r} supports unresolved skill {target!r}"
                    )
    if errors:
        raise ValueError("; ".join(errors))


def discover_all_skills(
    index: SkillIndex,
    verbose: bool = False,
    project_root: Path | None = None,
    config_dir: Path | None = None,
    extra_paths: list[Path] | None = None,
    include_archive: bool = False,
) -> None:
    """Discover, finalize, and validate the full inventory before filtering."""
    project_root = project_root or Path.cwd()
    config_dir = config_dir or Path.home() / ".config" / "opencode"
    extra_paths = extra_paths or []
    for root, source in get_standard_search_roots(project_root, config_dir):
        discover_skills_from_root(root, source, index, verbose=verbose)
    for root in extra_paths:
        discover_skills_from_root(Path(root), "extra", index, verbose=verbose)
    if include_archive:
        archive_roots = [
            *(
                project_root / part / "archive" / "skills"
                for part in (".opencode", ".claude", ".agents")
            ),
            config_dir / "archive" / "skills",
            config_dir.parent / ".claude" / "archive" / "skills",
            config_dir.parent / ".agents" / "archive" / "skills",
        ]
        for root in archive_roots:
            if root.is_dir():
                discover_skills_from_root(root, "archive", index, verbose=verbose)
    _finalize(index)
