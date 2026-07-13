"""Transform TaskDraftList input into a validated BreakdownTasksOutput file."""

from __future__ import annotations

import contextlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from lib.collect_skills.discovery import discover_all_skills
from lib.collect_skills.models import Skill, SkillIndex
from lib.schema import load_schema
from lib.shared.schema import validate_json_schema
from lib.shared.skill_class import SkillClass

OPENCODE_CONFIG_DIR = Path.home() / ".config" / "opencode"
INPUT_SCHEMA_PATH = (
    OPENCODE_CONFIG_DIR
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-input.schema.json"
)
OUTPUT_SCHEMA_PATH = (
    OPENCODE_CONFIG_DIR
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)
DEFAULT_THRESHOLD = 0.15
MAX_SKILLS = 3
DEFAULT_WEIGHTS = {
    "keyword_overlap": 0.50,
    "class_match": 0.25,
    "tag_similarity": 0.25,
}
DEFAULT_CLASSES = (SkillClass.OPERATION, SkillClass.DOCUMENTATION)
SUMMARY_SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class GenerationValidationError(ValueError):
    """Raised when draft or final task JSON fails schema validation."""


class SummarySlugError(ValueError):
    """Raised when a summary slug cannot safely form an output filename."""


def generate_task_json(
    data: dict[str, Any],
    summary_slug: str,
    *,
    project_root: Path | None = None,
    skills_index: list[dict[str, Any]] | None = None,
) -> Path:
    """Assign skills to *data* and write a slug-named local task file."""
    input_schema = load_schema(INPUT_SCHEMA_PATH)
    input_errors = validate_json_schema(data, input_schema)
    if input_errors:
        raise GenerationValidationError(
            f"input failed TaskDraftList schema: {input_errors}"
        )

    candidates = _candidate_skills(skills_index)
    if not candidates:
        raise RuntimeError("No skills found for operation or documentation classes")

    tasks: list[dict[str, Any]] = []
    for draft in data["tasks"]:
        task = dict(draft)
        task["skills"] = _select_skills(task, candidates)
        tasks.append(task)

    result = {"summary": data["summary"], "tasks": tasks}
    output_schema = load_schema(OUTPUT_SCHEMA_PATH)
    output_errors = validate_json_schema(result, output_schema)
    if output_errors:
        raise GenerationValidationError(
            f"output failed BreakdownTasksOutput schema: {output_errors}"
        )

    output_path = _output_path(summary_slug, project_root or Path.cwd())
    _write_json_new(output_path, result)
    return output_path


def _output_path(summary_slug: str, project_root: Path) -> Path:
    """Return the local task-file path for a validated summary slug."""
    if not SUMMARY_SLUG_PATTERN.fullmatch(summary_slug):
        raise SummarySlugError("summary slug must be lowercase kebab-case")
    return project_root / ".tasks" / f"{summary_slug}.json"


def _candidate_skills(skills_index: list[dict[str, Any]] | None) -> list[Skill]:
    """Return discovered or supplied executable skill candidates."""
    skills = (
        _parse_skills(skills_index)
        if skills_index is not None
        else _discover_skills()
    )
    allowed = {skill_class.value for skill_class in DEFAULT_CLASSES}
    return [skill for skill in skills if skill.class_ in allowed]


def _discover_skills() -> list[Skill]:
    """Discover skills from the standard OpenCode roots."""
    index = SkillIndex()
    discover_all_skills(index, verbose=False)
    return index.resolve()


def _parse_skills(index: list[dict[str, Any]]) -> list[Skill]:
    """Convert a serialized skill index into Skill objects."""
    return [
        Skill(
            name=entry.get("name", ""),
            description=entry.get("description", ""),
            tags=entry.get("tags", []),
            class_=entry.get("class", ""),
        )
        for entry in index
    ]


def _select_skills(task: dict[str, Any], candidates: list[Skill]) -> list[str]:
    """Return every threshold-qualified candidate or the highest-ranked skill."""
    task_text = _task_text(task)
    scored = [
        (skill.name, _score_skill(skill, task_text))
        for skill in candidates
    ]
    scored.sort(key=lambda item: (-item[1], item[0]))
    selected = [name for name, score in scored if score >= DEFAULT_THRESHOLD]
    return (selected or [scored[0][0]])[:MAX_SKILLS]


def _task_text(task: dict[str, Any]) -> str:
    """Build the text corpus used for deterministic skill scoring."""
    return " ".join(
        [
            task["purpose"],
            task["context"],
            " ".join(task["filesToRead"]),
            " ".join(task["filesToWrite"]),
        ]
    )


def _score_skill(skill: Skill, task_text: str) -> float:
    """Return the weighted lexical and class-match score for one skill."""
    task_tokens = _tokenize(task_text)
    skill_tokens = _tokenize(f"{skill.name} {skill.description} {' '.join(skill.tags)}")
    tag_tokens = {tag.lower() for tag in skill.tags}
    keyword_overlap = len(task_tokens & skill_tokens) / max(len(task_tokens), 1)
    tag_similarity = len(task_tokens & tag_tokens) / max(
        len(task_tokens | tag_tokens),
        1,
    )
    class_match = float(skill.class_ == _infer_task_class(task_tokens))
    return (
        DEFAULT_WEIGHTS["keyword_overlap"] * keyword_overlap
        + DEFAULT_WEIGHTS["class_match"] * class_match
        + DEFAULT_WEIGHTS["tag_similarity"] * tag_similarity
    )


def _tokenize(text: str) -> set[str]:
    """Return normalized lexical tokens from *text*."""
    return set(re.findall(r"[a-z0-9_]{2,}", text.lower()))


def _infer_task_class(tokens: set[str]) -> str:
    """Infer whether a task primarily changes files or documents findings."""
    documentation = {
        "analyze",
        "analysis",
        "describe",
        "design",
        "document",
        "documentation",
        "explain",
        "guide",
        "proposal",
        "reference",
        "summary",
    }
    operation = {
        "build",
        "create",
        "execute",
        "fix",
        "generate",
        "implement",
        "modify",
        "run",
        "test",
        "update",
        "write",
    }
    return (
        SkillClass.DOCUMENTATION.value
        if len(tokens & documentation) > len(tokens & operation)
        else SkillClass.OPERATION.value
    )


def _write_json_new(path: Path, data: dict[str, Any]) -> None:
    """Atomically create *path* without replacing an existing task file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Task file already exists: {path}")

    descriptor, temporary_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.tmp_",
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=2)
            output_file.write("\n")
        os.link(temporary_path, path)
        os.unlink(temporary_path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary_path)
        raise
