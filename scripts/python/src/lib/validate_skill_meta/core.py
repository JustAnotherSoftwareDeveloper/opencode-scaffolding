"""Core validation logic for skill SKILL.md YAML frontmatter.

Used by:
  cli.validate_skill_meta  (validate-skill-meta CLI entry point)
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import yaml

from lib.collect_skills.parser import SKILL_NAME_RE, load_repository_registry
from lib.shared.skill_routing import (
    MAX_SKILL_DESCRIPTION_LENGTH,
    MAX_SKILL_NAME_LENGTH,
    RoutingContractError,
    normalize_routing_signature,
)


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


# ---------------------------------------------------------------------------
# Frontmatter validation
# ---------------------------------------------------------------------------


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


def validate_frontmatter(data: object, registry=None) -> list[str]:
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
    elif name != name.strip():
        errors.append("Field 'name' must be trimmed")
    elif len(name) > MAX_SKILL_NAME_LENGTH or not SKILL_NAME_RE.fullmatch(name):
        errors.append("Field 'name' has invalid syntax")

    # Validate description. Planning references use a distinct, class-specific
    # prefix so selectors can distinguish passive context from executable work.
    description = data.get("description")
    class_val = data.get("class")
    if description is None:
        errors.append("Missing required frontmatter field: 'description'")
    elif not isinstance(description, str):
        errors.append("Field 'description' must be a string")
    elif (
        description != description.strip()
        or "\n" in description
        or "\r" in description
    ):
        errors.append("Field 'description' must be trimmed and single-line")
    elif len(description) > MAX_SKILL_DESCRIPTION_LENGTH:
        errors.append(
            f"Field 'description' must be at most "
            f"{MAX_SKILL_DESCRIPTION_LENGTH} characters"
        )
    elif class_val == "planning":
        if not description.startswith("Use as planning reference"):
            errors.append(
                "Field 'description' for planning class must start with "
                "'Use as planning reference'"
            )
    elif not description.startswith("Use when"):
        errors.append("Field 'description' must start with 'Use when'")

    # Routing metadata is intentionally delegated to the same normalizer used
    # by discovery.  This also makes old and mixed formats hard failures.
    try:
        normalize_routing_signature(data, registry)
    except RoutingContractError as exc:
        errors.append(f"Routing metadata is invalid: {exc}")

    # Validate class
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

    try:
        registry = load_repository_registry(path)
        errors = validate_frontmatter(parsed, registry)
    except (OSError, ValueError, RoutingContractError) as exc:
        errors.append(f"Routing metadata is invalid: {exc}")

    return {"valid": len(errors) == 0, "errors": errors}
