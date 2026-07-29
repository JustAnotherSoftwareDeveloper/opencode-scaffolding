"""Transform TaskDraftList input into a validated BreakdownTasksOutput file."""

from __future__ import annotations

import contextlib
import inspect
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

from lib.collect_skills.discovery import discover_all_skills
from lib.collect_skills.models import Skill, SkillIndex
from lib.generate_task_json.ranker import RankingResult, SkillCandidate
from lib.generate_task_json.ranking_diagnostics import (
    RankingDiagnosticBundle,
    RankingDiagnosticRecord,
    canonical_hash,
    publish_diagnostics,
)
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
    inventory_project_root: Path | None = None,
    output_dir: Path | None = None,
    output_file: Path | None = None,
    skills_index: list[dict[str, Any]] | None = None,
    ranker: Any | None = None,
    ranker_factory: Any | None = None,
    assignment_mode: str = "lexical",
    diagnostic_sink: Any | None = None,
    pair_preflight: Any | None = None,
) -> Path:
    """Assign skills to *data* and write an epoch-prefixed local task file.

    ``lexical`` is deliberately an explicit rollback mode.  The other modes
    require an injected ranker (or factory); they never construct a native
    scorer implicitly and never fall back after a ranking failure.
    """
    if assignment_mode not in {"lexical", "shadow", "qwen"}:
        raise ValueError("assignment_mode must be lexical, shadow, or qwen")
    if ranker is not None and ranker_factory is not None:
        raise ValueError("ranker and ranker_factory are mutually exclusive")
    if assignment_mode == "shadow" and diagnostic_sink is None:
        raise ValueError("shadow assignment requires a diagnostics sink")
    input_schema = load_schema(INPUT_SCHEMA_PATH)
    input_errors = validate_json_schema(data, input_schema)
    if input_errors:
        raise GenerationValidationError(
            f"input failed TaskDraftList schema: {input_errors}"
        )

    candidates = _candidate_skills(skills_index)
    strict_candidates: tuple[SkillCandidate, ...] = ()
    if assignment_mode != "lexical":
        strict_candidates = _strict_candidates(
            skills_index,
            project_root=inventory_project_root or project_root,
        )
        if assignment_mode != "lexical" and not strict_candidates:
            raise ValueError("ranked assignment requires a non-empty skill inventory")
        if pair_preflight is not None:
            if not callable(pair_preflight):
                raise TypeError("pair_preflight must be callable")
            pair_preflight(tuple(data["tasks"]), strict_candidates)
    active_ranker = _make_ranker(ranker, ranker_factory, strict_candidates)
    tasks: list[dict[str, Any]] = []
    diagnostic_records: list[RankingDiagnosticRecord] = []
    published_diagnostics: list[Path] = []
    try:
        for draft in data["tasks"]:
            task = dict(draft)
            if assignment_mode == "lexical":
                task["skills"] = _select_skills(task, candidates)
            else:
                assert active_ranker is not None
                result = _rank_once(active_ranker, task, strict_candidates)
                if assignment_mode == "shadow":
                    task["skills"] = _select_skills(task, candidates)
                else:
                    task["skills"] = list(result.names)
                if diagnostic_sink is not None:
                    diagnostic_records.append(
                        _result_diagnostics(
                            active_ranker,
                            result,
                            draft,
                            strict_candidates,
                            assignment_mode,
                        )
                    )
            tasks.append(task)
    except BaseException:
        _cleanup_diagnostics(published_diagnostics)
        raise

    result = {"summary": data["summary"], "tasks": tasks}
    output_schema = load_schema(OUTPUT_SCHEMA_PATH)
    try:
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
        if diagnostic_records:
            diagnostic_path = getattr(diagnostic_sink, "path", None)
            publish_diagnostics(
                RankingDiagnosticBundle(tuple(diagnostic_records)),
                diagnostic_sink,
            )
            if diagnostic_path is not None:
                published_diagnostics.append(Path(diagnostic_path))
        _write_json_new(output_path, result)
        return output_path
    except BaseException:
        _cleanup_diagnostics(published_diagnostics)
        raise


def _strict_candidates(
    skills_index: list[dict[str, Any]] | None,
    *,
    project_root: Path | None,
) -> tuple[SkillCandidate, ...]:
    """Validate and freeze collector metadata before ranker construction."""
    if skills_index is None:
        raise ValueError("ranked assignment requires an explicit skill inventory")
    config_root = Path.home() / ".config" / "opencode"
    source_roots: dict[str, tuple[Path, ...]] = {"global": (config_root,)}
    if project_root is not None:
        source_roots["project"] = (project_root,)
    candidates = tuple(
        SkillCandidate.from_metadata(
            entry,
            original_index=index,
            approved_source_roots=source_roots,
        )
        for index, entry in enumerate(skills_index)
    )
    names = [candidate.name for candidate in candidates]
    if len(names) != len(set(names)):
        raise ValueError("skill inventory contains duplicate names")
    return candidates


def _make_ranker(
    ranker: Any | None,
    ranker_factory: Any | None,
    candidates: tuple[SkillCandidate, ...],
) -> Any | None:
    if ranker is not None:
        return ranker
    if ranker_factory is None:
        if candidates:
            raise ValueError("ranker or ranker_factory is required")
        return None
    if not callable(ranker_factory):
        raise TypeError("ranker_factory must be callable")
    parameters = inspect.signature(ranker_factory).parameters
    return ranker_factory(candidates) if parameters else ranker_factory()


def _rank_once(
    ranker: Any,
    task: dict[str, Any],
    candidates: tuple[SkillCandidate, ...],
) -> RankingResult:
    result = ranker.rank(task, candidates)
    if not isinstance(result, RankingResult):
        raise TypeError("ranker must return RankingResult")
    allowed = {candidate.name for candidate in candidates}
    if (
        not result.names
        or len(result.names) > MAX_SKILLS
        or len(set(result.names)) != len(result.names)
        or not set(result.names).issubset(allowed)
    ):
        raise ValueError("ranker returned names outside the frozen inventory")
    return result


def _result_diagnostics(
    ranker: Any,
    result: RankingResult,
    task: Any,
    candidates: tuple[SkillCandidate, ...],
    mode: str,
) -> RankingDiagnosticRecord:
    """Build content-free evidence from concrete ranker identities."""
    identity_provider = getattr(ranker, "diagnostic_identity", None)
    raw_identity: Any = identity_provider() if callable(identity_provider) else {}
    identity: dict[str, str] = (
        {str(key): str(value) for key, value in raw_identity.items()}
        if isinstance(raw_identity, dict)
        else {}
    )
    ranker_name = f"{type(ranker).__module__}.{type(ranker).__qualname__}"
    return RankingDiagnosticRecord(
        model_hash=canonical_hash(identity.get("model", ranker_name)),
        runtime_hash=canonical_hash(identity.get("runtime", ranker_name)),
        tokenizer_hash=canonical_hash(identity.get("tokenizer", ranker_name)),
        prompt_hash=canonical_hash(identity.get("prompt", ranker_name)),
        render_hash=canonical_hash(identity.get("render", ranker_name)),
        policy_hash=canonical_hash(identity.get("policy", ranker_name)),
        inventory_hash=canonical_hash(
            [
                {
                    "name": candidate.name,
                    "description": candidate.description,
                    "tags": candidate.tags,
                    "class": candidate.skill_class,
                    "source": candidate.source,
                    "path_hash": canonical_hash(candidate.path),
                    "index": candidate.original_index,
                }
                for candidate in candidates
            ]
        ),
        task_hash=canonical_hash(task),
        pair_prompt_hashes=result.diagnostics.pair_prompt_hashes,
        candidate_scores=result.diagnostics.candidate_scores,
        token_counts=result.diagnostics.token_counts,
        clipped_labels=result.diagnostics.clipped_labels,
        latencies_ms=result.diagnostics.latencies_ms,
        selected_names=result.names,
        assignment_mode=mode,
        forced_low_confidence=result.diagnostics.forced_low_confidence,
    )


def _cleanup_diagnostics(paths: list[Path]) -> None:
    for path in paths:
        with contextlib.suppress(OSError):
            path.unlink()


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
    """Return up to three threshold-qualified candidates without fallback."""
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
    return selected[:MAX_SKILLS]


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
