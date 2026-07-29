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
_FILLER_TAGS: set[str] = {
    "common",
    "default",
    "general",
    "helper",
    "misc",
    "miscellaneous",
    "other",
    "skill",
    "tool",
    "utility",
}
_KNOWN_TOOLS: frozenset[str] = frozenset(
    {
        "bash",
        "pytest",
        "python",
        "bats",
        "bun",
        "cleye",
        "click",
        "todowrite",
        "makefile",
        "shellcheck",
        "biome",
    }
)
_DELIVERABLE_SUFFIXES: frozenset[str] = frozenset(
    {
        "-analysis",
        "-architecture",
        "-config",
        "-conventions",
        "-generation",
        "-guide",
        "-creation",
        "-output",
        "-json",
        "-workspace",
        "-record",
        "-reference",
        "-registry",
        "-dispatch",
        "-pipeline",
        "-rendering",
        "-tool",
        "-testing",
        "-writing",
        "-workflow",
        "-authoring",
    }
)
_CLUSTER_OVERUSE_THRESHOLD: int = 6


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_tool_or_deliverable_tag(tags: list[str]) -> bool:
    """Return *True* if *tags* includes at least one known tool or deliverable.

    A tag matches if it is a known tool name *or* ends with one of the
    recognised deliverable suffixes.
    """
    for tag in tags:
        if tag in _KNOWN_TOOLS:
            return True
        for suffix in _DELIVERABLE_SUFFIXES:
            if tag.endswith(suffix):
                return True
    return False


def compute_tag_frequencies(
    project_root: Path | None = None,
    config_dir: Path | None = None,
    extra_paths: list[Path] | None = None,
) -> dict[str, int]:
    """Compute frequency of each tag across all discovered skills.

    Uses :func:`lib.collect_skills.discovery.discover_all_skills` to
    enumerate all skills from the standard search roots and *extra_paths*.
    Returns a ``{tag: count}`` mapping for all tags found.
    """
    from lib.collect_skills.discovery import discover_all_skills
    from lib.collect_skills.models import SkillIndex

    index = SkillIndex()
    discover_all_skills(
        index,
        project_root=project_root,
        config_dir=config_dir,
        extra_paths=extra_paths,
    )
    freq: dict[str, int] = {}
    for skill in index.resolve():
        for tag in skill.tags:
            freq[tag] = freq.get(tag, 0) + 1
    return freq


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


def validate_skill_file(
    path: Path,
    tag_frequencies: dict[str, int] | None = None,
) -> ValidationResult:
    """Read and validate a SKILL.md file's frontmatter.

    When *tag_frequencies* is provided (a ``{tag: count}`` mapping from
    :func:`compute_tag_frequencies`), two additional checks are enforced:

    * **Tool / deliverable tag** — at least one tag must name a known tool or
      end with a recognised deliverable suffix.
    * **Cluster overuse** — no tag may appear in 6 or more discovered skills.

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

    # --- Additional checks requiring cross-skill context -------------------
    if tag_frequencies is not None and isinstance(parsed, dict):
        tags = parsed.get("tags")
        if isinstance(tags, list):
            # 5. Tool / deliverable tag requirement
            if not _has_tool_or_deliverable_tag(tags):
                errors.append(
                    "Field 'tags' must include at least one tool or deliverable tag"
                )

            # 4. Cluster overuse — any tag in 6+ discovered skills
            for tag in tags:
                if not isinstance(tag, str):
                    continue
                tag_val = tag.strip()
                count = tag_frequencies.get(tag_val, 0)
                if count >= _CLUSTER_OVERUSE_THRESHOLD:
                    errors.append(
                        f"Tag '{tag_val}' appears in {count} skills — "
                        f"use a more specific alternative"
                    )

    return {"valid": len(errors) == 0, "errors": errors}
