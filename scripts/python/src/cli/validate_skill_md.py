"""Validate a complete skill entry point against the hard-cut profile contract."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import click
import yaml

from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata

_ACTIVE = {"operation", "delegated", "inline", "orchestrated"}
_PASSIVE = {"planning", "documentation"}


def _body_errors(body: str, skill_class: str) -> list[str]:
    errors: list[str] = []
    if not body.strip():
        errors.append("body must not be empty")
        return errors
    numbered = re.search(r"(?m)^\s*\d+[.)]\s+", body) is not None
    if skill_class in _ACTIVE and not numbered:
        errors.append("active classes must define numbered execution steps")
    if skill_class in _PASSIVE and numbered:
        errors.append(
            "planning and documentation classes must not define execution steps"
        )
    return errors


def validate_skill_file(path: Path) -> dict[str, Any]:
    """Return the same small result shape for every invalidity, without raising."""
    errors: list[str] = []
    if not path.is_file():
        return {"valid": False, "errors": [f"File not found: {path}"]}
    if path.name != "SKILL.md":
        errors.append("path must end in SKILL.md")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"valid": False, "errors": [f"Unable to read file: {exc}"]}
    if not text.startswith("---\n"):
        errors.append("frontmatter must start with '---'")
        return {"valid": False, "errors": errors}
    end = text.find("\n---", 4)
    if end < 0:
        errors.append("frontmatter closing delimiter is missing")
        return {"valid": False, "errors": errors}
    raw = text[4:end]
    body = text[end + 4 :]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"Frontmatter YAML parse error: {exc}")
        return {"valid": False, "errors": errors}
    try:
        profile = normalize_skill_metadata(data)
    except (SkillMetadataError, TypeError) as exc:
        errors.append(str(exc))
        return {"valid": False, "errors": errors}

    if profile.name != path.parent.name:
        errors.append(
            f"name '{profile.name}' does not match directory '{path.parent.name}'"
        )
    errors.extend(_body_errors(body, profile.skill_class))
    if profile.skill_class in _PASSIVE and profile.selection.role != "reference":
        errors.append(
            "planning and documentation classes must use selection.role reference"
        )
    return {"valid": not errors, "errors": errors}


@click.command(name="validate-skill-md")
@click.argument("skill_paths", type=click.Path(dir_okay=False), nargs=-1, required=True)
def main(skill_paths: tuple[str, ...]) -> None:
    """Validate one or more complete SKILL.md files."""
    results = [validate_skill_file(Path(value)) for value in skill_paths]
    click.echo(json.dumps(results[0] if len(results) == 1 else results))
    if any(not result["valid"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
