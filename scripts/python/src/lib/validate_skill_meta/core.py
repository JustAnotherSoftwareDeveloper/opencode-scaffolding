"""Core validation logic for skill SKILL.md YAML frontmatter.

Used by:
  cli.validate_skill_meta  (validate-skill-meta CLI entry point)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict

import yaml


class ValidationResult(TypedDict):
    """Result of a frontmatter validation.

    Attributes:
        valid: *True* when no validation errors were found.
        errors: Human-readable error messages.
    """

    valid: bool
    errors: list[str]


_VALID_CLASSES: set[str] = {
    "operation",
    "delegated",
    "inline",
    "orchestrated",
    "planning",
    "documentation",
}
_TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_FILLER_TAGS = {
    "common",
    "default",
    "general",
    "helper",
    "misc",
    "skill",
    "tool",
    "utility",
}


def _extract_frontmatter(text: str) -> str | None:
    """Extract YAML frontmatter block between leading ``---`` delimiters.

    Returns the raw frontmatter string (without delimiters) or *None* if the
    file does not start with a valid frontmatter block.
    """
    if not text.startswith("---"):
        return None

    # Find closing delimiter after the opening one
    rest = text[3:]
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return None

    # Return everything between the two --- markers
    return rest[:end_idx]


def validate_frontmatter(data: object) -> list[str]:
    """Validate parsed frontmatter fields and return a list of error messages.

    Returns an empty list if all fields are valid.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        errors.append("Frontmatter is not a valid YAML mapping")
        return errors

    # Validate name
    name = data.get("name")
    if name is None:
        errors.append("Missing required frontmatter field: 'name'")
    elif not isinstance(name, str) or not name.strip():
        errors.append("Field 'name' must be a non-empty string")

    # Validate description
    description = data.get("description")
    if description is None:
        errors.append("Missing required frontmatter field: 'description'")
    elif not isinstance(description, str):
        errors.append("Field 'description' must be a string")
    elif not description.startswith("Use when"):
        errors.append("Field 'description' must start with 'Use when'")

    # Validate tags
    tags = data.get("tags")
    if tags is None:
        errors.append("Missing required frontmatter field: 'tags'")
    elif not isinstance(tags, list):
        errors.append("Field 'tags' must be a list")
    elif not 4 <= len(tags) <= 7:
        errors.append("Field 'tags' must contain 4–7 values")
    else:
        normalized_tags: set[str] = set()
        for tag in tags:
            if not isinstance(tag, str):
                errors.append("Field 'tags' values must be strings")
                continue
            tag_value = tag.strip()
            if not _TAG_RE.fullmatch(tag_value):
                errors.append("Field 'tags' values must be lowercase kebab-case")
            if tag_value in _FILLER_TAGS:
                errors.append("Field 'tags' values must not be filler terms")
            if tag_value in normalized_tags:
                errors.append("Field 'tags' values must be unique")
            normalized_tags.add(tag_value)
        if isinstance(name, str) and name.strip() in normalized_tags:
            errors.append("Field 'tags' must not repeat the skill name")

    # Validate class
    class_val = data.get("class")
    if class_val is None:
        errors.append("Missing required frontmatter field: 'class'")
    elif not isinstance(class_val, str):
        errors.append("Field 'class' must be a string")
    elif class_val not in _VALID_CLASSES:
        sorted_classes = sorted(_VALID_CLASSES)
        errors.append(f"Field 'class' must be one of: {', '.join(sorted_classes)}")

    return errors


def validate_skill_file(path: Path) -> ValidationResult:
    """Read and validate a SKILL.md file's frontmatter.

    Returns a dict with keys:
      - ``valid`` (bool): *True* when no validation errors were found.
      - ``errors`` (list[str]): Human-readable error messages.
    """
    errors: list[str] = []

    if not path.is_file():
        return {"valid": False, "errors": [f"File not found: {path}"]}

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return {"valid": False, "errors": [f"Cannot read file: {exc}"]}

    frontmatter = _extract_frontmatter(text)
    if frontmatter is None:
        return {
            "valid": False,
            "errors": [
                "File must start with '---' frontmatter delimiters "
                "followed by '---' on a later line"
            ],
        }

    try:
        parsed = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        return {"valid": False, "errors": [f"Frontmatter YAML parse error: {exc}"]}

    errors = validate_frontmatter(parsed)
    return {"valid": len(errors) == 0, "errors": errors}
