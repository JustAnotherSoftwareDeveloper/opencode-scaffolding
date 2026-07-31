"""Directory traversal, walkup, and SKILL.md discovery with symlink handling."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from lib.collect_skills.models import Skill, SkillIndex
from lib.collect_skills.parser import (
    extract_frontmatter,
    load_repository_registry,
    parse_routing_signature,
    validate_skill_frontmatter,
)
from lib.shared.skill_routing import RegistryResolution

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _should_exclude_dir(dir_name: str) -> bool:
    """Return *True* if *dir_name* should be skipped during traversal.

    Skips:
    * ``node_modules``
    * ``__pycache__``
    * Any name starting with ``.`` or ``_``
    """
    return dir_name in ("node_modules", "__pycache__") or dir_name.startswith(
        (".", "_")
    )


# ---------------------------------------------------------------------------
# Git-root walkup
# ---------------------------------------------------------------------------


def find_git_root(path: Path) -> Path | None:
    """Walk up from *path* looking for a ``.git/`` directory.

    Returns the **parent** of the ``.git/`` directory (i.e. the work-tree
    root), or *None* if no ``.git/`` is found before the filesystem root.
    """
    current = path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
        # Stop at filesystem root to avoid infinite loop.
        if parent == parent.parent:
            break
    return None


# ---------------------------------------------------------------------------
# Standard search roots
# ---------------------------------------------------------------------------


def get_standard_search_roots(
    project_root: Path, config_dir: Path
) -> list[tuple[Path, str]]:
    """Build project and global search root paths.

    Returns ``(search_root, source_label)`` tuples for directories that
    actually exist on disk.

    **Project paths** (source ``"project"``):
    * ``<project_root>/.opencode/skills/``
    * ``<project_root>/.claude/skills/``
    * ``<project_root>/.agents/skills/``

    **Global paths** (source ``"global"``):
    * ``<config_dir>/skills/``
    * ``<config_dir.parent>/.claude/skills/``
    * ``<config_dir.parent>/.agents/skills/``
    """
    roots: list[tuple[Path, str]] = []

    # -- Project search roots -----------------------------------------------
    project_subdirs = [
        project_root / ".opencode" / "skills",
        project_root / ".claude" / "skills",
        project_root / ".agents" / "skills",
    ]
    for subdir in project_subdirs:
        if subdir.is_dir():
            roots.append((subdir, "project"))

    # -- Global search roots ------------------------------------------------
    global_subdirs = [
        config_dir / "skills",
        config_dir.parent / ".claude" / "skills",
        config_dir.parent / ".agents" / "skills",
    ]
    for subdir in global_subdirs:
        if subdir.is_dir():
            roots.append((subdir, "global"))

    return roots


# ---------------------------------------------------------------------------
# Per-root discovery
# ---------------------------------------------------------------------------


def discover_skills_from_root(
    root: Path,
    source: str,
    index: SkillIndex,
    verbose: bool = False,
    registry: RegistryResolution | None = None,
) -> None:
    """Walk a single *root* directory and add discovered skills to *index*.

    For each immediate subdirectory of *root*:
    1. Skip if :func:`_should_exclude_dir` returns ``True``.
    2. Skip if ``SKILL.md`` does not exist inside the subdirectory.
    3. If the subdirectory is a symlink, resolve its real path and detect
       loops via a visited-real-paths set.  Already-visited real paths are
       skipped silently.
    4. Parse and validate the skill using :mod:`lib.collect_skills.parser`.
    5. Create a :class:`Skill` instance and add it to *index*.

    Edge cases handled:
    * Non-existent roots are skipped (warning if *verbose*).
    * Broken symlinks are caught and skipped (warning if verbose).
    * Permission errors on directories or files are caught and skipped.
    * Malformed YAML / missing frontmatter / validation errors are caught
      and the skill is skipped.
    """

    if not root.exists():
        if verbose:
            print(
                f"[collect-skills] Warning: search root does not exist: {root}",
                file=sys.stderr,
            )
        return

    if registry is None:
        registry = load_repository_registry(find_git_root(root) or root)

    if not root.is_dir():
        if verbose:
            print(
                f"[collect-skills] Warning: search root is not a directory: {root}",
                file=sys.stderr,
            )
        return

    # Track resolved real paths to detect symlink loops.
    visited_real: set[Path] = set()

    try:
        entries = sorted(root.iterdir(), key=lambda p: p.name)
    except PermissionError:
        if verbose:
            print(
                f"[collect-skills] Warning: permission denied reading "
                f"directory: {root}",
                file=sys.stderr,
            )
        return
    except OSError as exc:
        if verbose:
            print(
                f"[collect-skills] Warning: cannot list directory {root}: {exc}",
                file=sys.stderr,
            )
        return

    for entry in entries:
        if not entry.is_dir() and not entry.is_symlink():
            continue

        dir_name = entry.name

        if _should_exclude_dir(dir_name):
            continue

        # --- Resolve the actual directory path (follow symlinks) -----------
        try:
            if entry.is_symlink():
                real = entry.resolve()
                if real in visited_real:
                    continue  # symlink loop detected
                visited_real.add(real)
                if not real.is_dir():
                    continue  # broken symlink or not a directory
                skill_dir = real
                # Use the real directory name for validation so that the
                # frontmatter ``name`` field matches the real directory,
                # not the symlink alias.
                dir_name = skill_dir.name
            else:
                skill_dir = entry
        except (PermissionError, OSError, RuntimeError):
            if verbose:
                print(
                    f"[collect-skills] Warning: cannot access {entry}",
                    file=sys.stderr,
                )
            continue

        # --- Look for SKILL.md ---------------------------------------------
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            continue

        if not skill_file.is_file():
            continue

        # --- Parse frontmatter ---------------------------------------------
        try:
            frontmatter = extract_frontmatter(skill_file)
        except FileNotFoundError:
            if verbose:
                print(
                    f"[collect-skills] Warning: SKILL.md vanished: {skill_file}",
                    file=sys.stderr,
                )
            continue
        except PermissionError:
            if verbose:
                print(
                    f"[collect-skills] Warning: permission denied reading: "
                    f"{skill_file}",
                    file=sys.stderr,
                )
            continue
        except Exception as exc:
            if verbose:
                print(
                    f"[collect-skills] Warning: error reading {skill_file}: {exc}",
                    file=sys.stderr,
                )
            continue

        if frontmatter is None:
            if verbose:
                print(
                    f"[collect-skills] Warning: no frontmatter in "
                    f"{skill_file}, skipping",
                    file=sys.stderr,
                )
            continue

        # --- Validate ------------------------------------------------------
        errors = validate_skill_frontmatter(
            frontmatter, dir_name, skill_file, registry=registry
        )
        if errors:
            if verbose:
                for err in errors:
                    print(
                        f"[collect-skills] Warning: {err}",
                        file=sys.stderr,
                    )
            continue

        # --- Build Skill instance ------------------------------------------
        name: str = frontmatter.get("name", dir_name)
        description: str = frontmatter.get("description", "")
        class_: str = frontmatter.get("class", "")
        version: str = frontmatter.get("version", "")
        license_: str = frontmatter.get("license", "")
        compatibility: str = frontmatter.get("compatibility", "")
        metadata: dict[str, Any] = frontmatter.get("metadata", {})
        permission: str = frontmatter.get("permission", "")
        signature = parse_routing_signature(frontmatter, registry)

        # Discovered location overrides any frontmatter `location` key.
        location: str = str(skill_file.resolve())

        skill = Skill(
            name=name,
            description=description,
            schema_version=signature.schema_version.value,
            cues=signature.cues,
            relationships=signature.relationships,
            class_=class_,
            version=version,
            license=license_,
            compatibility=compatibility,
            metadata=metadata,
            location=location,
            source=source,
            permission=permission,
        )

        index.add(skill)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def discover_all_skills(
    index: SkillIndex,
    verbose: bool = False,
    project_root: Path | None = None,
    config_dir: Path | None = None,
    extra_paths: list[Path] | None = None,
    include_archive: bool = False,
) -> None:
    """Orchestrate discovery across all configured search roots.

    Discovers skills from:
    1. Standard search roots (project + global).
    2. Extra paths (*extra_paths*) with source ``"extra"``.
    3. Archive paths (if *include_archive* is true) with source ``"archive"``.

    Each root is passed to :func:`discover_skills_from_root`.
    """
    if project_root is None:
        project_root = Path.cwd()
    if config_dir is None:
        config_dir = Path.home() / ".config" / "opencode"
    if extra_paths is None:
        extra_paths = []

    registry = load_repository_registry(project_root)

    # --- 1. Standard search roots ------------------------------------------
    standard_roots = get_standard_search_roots(project_root, config_dir)
    for root, source in standard_roots:
        if verbose:
            print(
                f"[collect-skills] Scanning {source} root: {root}",
                file=sys.stderr,
            )
        discover_skills_from_root(
            root, source, index, verbose=verbose, registry=registry
        )

    # --- 2. Extra paths ----------------------------------------------------
    for extra_root in extra_paths:
        extra_path = (
            Path(extra_root) if not isinstance(extra_root, Path) else extra_root
        )
        if verbose:
            print(
                f"[collect-skills] Scanning extra root: {extra_path}",
                file=sys.stderr,
            )
        discover_skills_from_root(
            extra_path, "extra", index, verbose=verbose, registry=registry
        )

    # --- 3. Archive paths (optional) ---------------------------------------
    if include_archive:
        archive_project_paths = [
            project_root / ".opencode" / "archive" / "skills",
            project_root / ".claude" / "archive" / "skills",
            project_root / ".agents" / "archive" / "skills",
        ]
        archive_global_paths = [
            config_dir / "archive" / "skills",
            config_dir.parent / ".claude" / "archive" / "skills",
            config_dir.parent / ".agents" / "archive" / "skills",
        ]
        all_archive_paths = archive_project_paths + archive_global_paths
        for archive_root in all_archive_paths:
            if archive_root.is_dir():
                if verbose:
                    print(
                        f"[collect-skills] Scanning archive root: {archive_root}",
                        file=sys.stderr,
                    )
                discover_skills_from_root(
                    archive_root,
                    "archive",
                    index,
                    verbose=verbose,
                    registry=registry,
                )
