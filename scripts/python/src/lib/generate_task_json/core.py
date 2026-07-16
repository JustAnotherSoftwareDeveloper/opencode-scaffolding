"""Transform TaskDraftList input into a validated BreakdownTasksOutput file."""

from __future__ import annotations

import contextlib
import json
import os
import re
import tempfile
import time
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
# A class match contributes 0.25 by itself. Require additional semantic
# evidence before assigning a skill so every operation or documentation skill
# is not selected solely because it shares the inferred task class.
DEFAULT_THRESHOLD = 0.26
MIN_SEMANTIC_SCORE = 0.05
MAX_SKILLS = 3
DEFAULT_WEIGHTS = {
    "keyword_overlap": 0.50,
    "class_match": 0.25,
    "tag_similarity": 0.25,
}
DEFAULT_CLASSES = (SkillClass.OPERATION, SkillClass.DOCUMENTATION)
SUMMARY_SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _derive_slug(summary: str) -> str | None:
    """Derive a valid kebab-case slug from *summary*, or return None."""
    slug = summary.lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")
    if not SUMMARY_SLUG_PATTERN.fullmatch(slug):
        return None
    return slug


class GenerationValidationError(ValueError):
    """Raised when draft or final task JSON fails schema validation."""


class SummarySlugError(ValueError):
    """Raised when a summary slug cannot safely form an output filename."""


def generate_task_json(
    data: dict[str, Any],
    summary_slug: str | None = None,
    *,
    project_root: Path | None = None,
    output_dir: Path | None = None,
    output_file: Path | None = None,
    skills_index: list[dict[str, Any]] | None = None,
) -> Path:
    """Assign skills to *data* and write an epoch-prefixed local task file."""
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

    if summary_slug is None and output_file is None:
        summary_slug = _derive_slug(data["summary"])
        if summary_slug is None:
            raise SummarySlugError(
                f"cannot derive a valid slug from summary: {data['summary']!r}"
            )

    output_path = _resolve_output_path(
        summary_slug,
        project_root=project_root,
        output_dir=output_dir,
        output_file=output_file,
    )
    _write_json_new(output_path, result)
    return output_path


def _resolve_output_path(
    summary_slug: str | None,
    *,
    project_root: Path | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> Path:
    """Return one validated output path for legacy or explicit-file mode."""
    if output_file is not None:
        if (
            summary_slug is not None
            or output_dir is not None
            or project_root is not None
        ):
            raise ValueError(
                "output_file is mutually exclusive with legacy output options"
            )
        if output_file.suffix != ".json":
            raise ValueError("output file must use a .json suffix")
        return output_file
    if summary_slug is None:
        raise ValueError("summary_slug is required without output_file")
    if output_dir is not None and project_root is not None:
        raise ValueError("provide either output_dir or project_root, not both")
    return _output_path(
        summary_slug,
        output_dir or (project_root or Path.cwd()) / ".tasks",
    )


def _output_path(summary_slug: str, output_dir: Path) -> Path:
    """Return an epoch-prefixed local task-file path for a validated slug."""
    if not SUMMARY_SLUG_PATTERN.fullmatch(summary_slug):
        raise SummarySlugError("summary slug must be lowercase kebab-case")
    epoch_milliseconds = time.time_ns() // 1_000_000
    return output_dir / f"{epoch_milliseconds}-{summary_slug}.json"


def _candidate_skills(skills_index: list[dict[str, Any]] | None) -> list[Skill]:
    """Return discovered or supplied executable skill candidates."""
    skills = (
        _parse_skills(skills_index) if skills_index is not None else _discover_skills()
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
    task_class = _infer_task_class(_tokenize(task_text))
    scored = [(skill, _score_skill(skill, task_text)) for skill in candidates]
    scored.sort(key=lambda item: (-item[1], item[0].name))
    selected = [
        skill.name
        for skill, score in scored
        if score >= DEFAULT_THRESHOLD
        and score
        - (DEFAULT_WEIGHTS["class_match"] if skill.class_ == task_class else 0)
        >= MIN_SEMANTIC_SCORE
    ]
    return (selected or [scored[0][0].name])[:MAX_SKILLS]


def _task_text(task: dict[str, Any]) -> str:
    """Build the text corpus used for deterministic skill scoring.

    Composed from purpose, context, and expectedOutput — the three
    semantic fields that describe *what the task is about*.  File-path
    fields (filesToRead, filesToWrite) are excluded because their tokens
    dominate Jaccard similarity without contributing task-meaning signal.
    """
    return " ".join(
        [
            task["purpose"],
            task["context"],
            task["expectedOutput"],
        ]
    )


def _score_skill(skill: Skill, task_text: str) -> float:
    """Return the weighted lexical and class-match score for one skill."""
    task_tokens = _tokenize(task_text)
    skill_tokens = _tokenize(f"{skill.name} {skill.description}")
    tag_tokens = _tokenize(" ".join(skill.tags))
    keyword_overlap = len(task_tokens & skill_tokens) / max(
        len(task_tokens | skill_tokens),
        1,
    )
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
