"""SKILL.md frontmatter extraction and validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# Matches kebab-case: lowercase letters and digits, hyphen-separated.
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FILLER_TAGS = {
    "common",
    "default",
    "general",
    "helper",
    "misc",
    "skill",
    "tool",
    "utility",
}


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

        if not SKILL_NAME_RE.match(name_val):
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

    # --- tags ----------------------------------------------------------------
    tags = frontmatter.get("tags")

    if tags is None:
        errors.append(f"{file_path}: missing 'tags' field")
    elif not isinstance(tags, list):
        errors.append(f"{file_path}: 'tags' must be a list")
    elif not 4 <= len(tags) <= 7:
        errors.append(f"{file_path}: 'tags' must contain 4–7 values")
    else:
        normalized_tags: set[str] = set()
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                errors.append(f"{file_path}: 'tags' element {i} must be a string")
                continue

            tag_value = tag.strip()
            if not TAG_RE.fullmatch(tag_value):
                errors.append(
                    f"{file_path}: 'tags' element {i} must be lowercase kebab-case"
                )
            if tag_value in FILLER_TAGS:
                errors.append(f"{file_path}: 'tags' element {i} is a filler value")
            if tag_value in normalized_tags:
                errors.append(f"{file_path}: 'tags' contains duplicate {tag_value!r}")
            normalized_tags.add(tag_value)

        if isinstance(name, str) and name.strip() in normalized_tags:
            errors.append(f"{file_path}: 'tags' must not repeat the skill name")

    return errors
