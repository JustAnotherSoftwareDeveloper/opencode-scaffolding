"""SKILL.md frontmatter extraction and validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from lib.shared.skill_class import SkillClass
from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata

# Matches kebab-case: lowercase letters and digits, hyphen-separated.
SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
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

    # Frontmatter is valid only when it starts the file.  Keeping this rule
    # identical to the authoring and validator readers prevents body content
    # that happens to contain a delimiter from becoming metadata.
    if not lines or lines[0].rstrip() != "---":
        return None
    start_idx = 0

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
    registry: object | None = None,
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
    del registry
    errors: list[str] = []

    # --- name ----------------------------------------------------------------
    name = frontmatter.get("name")

    if name is None:
        errors.append(f"{file_path}: missing 'name' field")
    elif not isinstance(name, str) or not name.strip():
        errors.append(f"{file_path}: 'name' must be a non-empty string")
    else:
        name_val: str = name.strip()

        if not SKILL_NAME_RE.fullmatch(name_val):
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
        normalize_skill_metadata(frontmatter)
    except SkillMetadataError as exc:
        errors.append(f"{file_path}: selection metadata is invalid: {exc}")

    return errors
