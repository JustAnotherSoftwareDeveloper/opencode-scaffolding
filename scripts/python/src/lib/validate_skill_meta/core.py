"""Core validation logic for skill SKILL.md YAML frontmatter.

Used by:
  cli.validate_skill_meta  (validate-skill-meta CLI entry point)
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import yaml

from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata


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
    del registry
    errors: list[str] = []
    try:
        normalize_skill_metadata(data)  # type: ignore[arg-type]
    except SkillMetadataError as exc:
        errors.append(str(exc))

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
        errors = validate_frontmatter(parsed)
    except (OSError, ValueError) as exc:
        errors.append(f"Selection metadata is invalid: {exc}")

    return {"valid": len(errors) == 0, "errors": errors}
