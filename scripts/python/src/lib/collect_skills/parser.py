"""SKILL.md frontmatter extraction and validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from lib.shared.git import find_git_root
from lib.shared.skill_class import SkillClass
from lib.shared.skill_routing import (
    MAX_SKILL_DESCRIPTION_LENGTH,
    MAX_SKILL_NAME_LENGTH,
    RegistryResolution,
    RoutingContractError,
    RoutingSignature,
    load_builtin_registry,
    normalize_routing_signature,
    resolve_registry_overlay,
)

# Matches kebab-case: lowercase letters and digits, hyphen-separated.
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_VALID_CLASSES = {item.value for item in SkillClass}


def extract_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """Parse the YAML frontmatter block from a SKILL.md file.

    Reads *file_path*, looks for the first two lines consisting of exactly
    ``---`` (with optional trailing whitespace), extracts the content between
    them, and parses it as YAML.

    Returns
    -------
    dict[str, Any] | None
        The parsed frontmatter dictionary, or *None* if no ``---`` delimiters
        are found.

    Raises
    ------
    FileNotFoundError
        *file_path* does not exist.
    PermissionError
        *file_path* cannot be read.
    yaml.YAMLError
        The extracted YAML is malformed.
    ValueError
        The parsed YAML value is not a ``dict``.
    """
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Locate the first --- delimiter.
    start_idx: int | None = None
    for i, line in enumerate(lines):
        if line.rstrip() == "---":
            start_idx = i
            break

    if start_idx is None:
        return None

    # Locate the second --- delimiter after start_idx.
    end_idx: int | None = None
    for i in range(start_idx + 1, len(lines)):
        if lines[i].rstrip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None

    # Extract the raw YAML content between the delimiters.
    yaml_lines = lines[start_idx + 1 : end_idx]
    yaml_text = "\n".join(yaml_lines)

    parsed = yaml.safe_load(yaml_text)

    if parsed is None:
        # An empty frontmatter block (e.g. ``---\n---``) yields None.
        return {}

    if not isinstance(parsed, dict):
        raise ValueError(
            f"Frontmatter in {file_path} must be a mapping "
            f"(got {type(parsed).__name__})"
        )

    return dict(parsed)


def validate_skill_frontmatter(
    frontmatter: dict[str, Any],
    dir_name: str,
    file_path: Path,
    registry: RegistryResolution | None = None,
) -> list[str]:
    """Validate a parsed skill frontmatter dictionary.

    Parameters
    ----------
    frontmatter:
        The dictionary returned by :func:`extract_frontmatter`.
    dir_name:
        The name of the directory containing the skill (used to verify the
        ``name`` field matches).
    file_path:
        Path to the SKILL.md file (included in error messages for traceability).

    Returns
    -------
    list[str]
        A list of human-readable error messages.  An empty list means the
        frontmatter is valid.
    """
    errors: list[str] = []

    # --- name ----------------------------------------------------------------
    name = frontmatter.get("name")

    if name is None:
        errors.append(f"{file_path}: missing 'name' field")
    elif not isinstance(name, str) or not name.strip():
        errors.append(f"{file_path}: 'name' must be a non-empty string")
    else:
        name_val: str = name.strip()

        if len(name_val) > MAX_SKILL_NAME_LENGTH or not SKILL_NAME_RE.match(name_val):
            errors.append(
                f"{file_path}: 'name' ({name_val!r}) must match "
                f"{SKILL_NAME_RE.pattern!r}"
            )

        if name_val != dir_name:
            errors.append(
                f"{file_path}: 'name' ({name_val!r}) must match "
                f"directory name ({dir_name!r})"
            )

    # --- description ---------------------------------------------------------
    description = frontmatter.get("description")

    if description is None:
        errors.append(f"{file_path}: missing 'description' field")
    elif not isinstance(description, str) or not description.strip():
        errors.append(f"{file_path}: 'description' must be a non-empty string")
    elif (
        description != description.strip()
        or "\n" in description
        or "\r" in description
    ):
        errors.append(f"{file_path}: 'description' must be trimmed and single-line")
    elif len(description) > MAX_SKILL_DESCRIPTION_LENGTH:
        errors.append(
            f"{file_path}: 'description' must be at most "
            f"{MAX_SKILL_DESCRIPTION_LENGTH} characters"
        )

    class_value = frontmatter.get("class")
    if class_value is None:
        errors.append(f"{file_path}: missing 'class' field")
    elif not isinstance(class_value, str) or class_value not in _VALID_CLASSES:
        errors.append(
            f"{file_path}: 'class' must be one of: {', '.join(sorted(_VALID_CLASSES))}"
        )
    elif isinstance(description, str):
        expected_prefix = (
            "Use as planning reference"
            if class_value == SkillClass.PLANNING.value
            else "Use when"
        )
        if not description.startswith(expected_prefix):
            errors.append(
                f"{file_path}: 'description' for class {class_value!r} "
                f"must start with {expected_prefix!r}"
            )

    try:
        normalize_routing_signature(frontmatter, registry)
    except RoutingContractError as exc:
        errors.append(f"{file_path}: routing metadata is invalid: {exc}")

    return errors


def parse_routing_signature(
    frontmatter: dict[str, Any], registry: RegistryResolution | None = None
) -> RoutingSignature:
    """Normalize the exact routing contract used by authoring and discovery."""
    return normalize_routing_signature(frontmatter, registry)


def load_repository_registry(context: Path | None = None) -> RegistryResolution:
    """Load the built-in registry plus one repository-owned overlay.

    The conventional repository files are checked in order.  Missing files are
    normal; malformed or colliding declarations are deliberately propagated so
    discovery cannot silently accept a different vocabulary.
    """
    registry = load_builtin_registry()
    if context is None:
        return registry
    root = context if context.is_dir() else context.parent
    git_root = find_git_root(root)
    candidate_roots: list[Path] = [root]
    if git_root is not None:
        candidate_roots = []
        for candidate_root in (root, *root.parents):
            candidate_roots.append(candidate_root)
            if candidate_root == git_root:
                break
    for candidate_root in candidate_roots:
        candidates = (
            candidate_root / "skill-facets.json",
            candidate_root / ".skill-facets.json",
            candidate_root / ".opencode" / "skill-facets.json",
            candidate_root / ".opencode" / "facets.json",
        )
        existing = [path for path in candidates if path.is_file()]
        if len(existing) > 1:
            names = ", ".join(str(path) for path in existing)
            raise RoutingContractError(
                f"multiple facet registries declared at the same scope: {names}"
            )
        if existing:
            data = json.loads(existing[0].read_text(encoding="utf-8"))
            return resolve_registry_overlay(data, registry)
    return registry
