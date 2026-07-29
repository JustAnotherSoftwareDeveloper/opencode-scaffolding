"""Pure, deterministic skill-ranking domain objects.

This module deliberately knows nothing about a model implementation.  A model
adapter supplies :class:`PairScorer`; validation and selection remain Python
responsibilities so a model can never manufacture an assignment.
"""

# The domain's serialized labels intentionally remain compact and readable.
# ruff: noqa: E501

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from lib.shared.skill_class import SkillClass

_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_MAX_DESCRIPTION = 8_000
_MAX_TAGS = 32
_MAX_TAG_LENGTH = 64
_MAX_CANDIDATES = 128
_DEFAULT_CLASSES = (SkillClass.OPERATION.value, SkillClass.DOCUMENTATION.value)


class SkillRankingInputError(ValueError):
    """Raised for malformed, unauthorized, or otherwise unsafe input."""


class SkillRankingConfigurationError(ValueError):
    """Raised for an invalid ranking policy or scorer configuration."""


class SkillRankingRuntimeError(RuntimeError):
    """Raised when scoring returns an unusable runtime result."""


class PairScorer(Protocol):
    """Minimal model boundary used by deterministic tests and adapters."""

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]: ...


def _text(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise SkillRankingInputError(f"{field} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SkillCandidate:
    name: str
    description: str
    tags: tuple[str, ...]
    skill_class: str
    source: str
    path: Path
    original_index: int = 0

    @classmethod
    def from_metadata(
        cls,
        metadata: Mapping[str, Any],
        *,
        original_index: int = 0,
        approved_sources: Sequence[str] = ("project", "global"),
        approved_roots: Sequence[Path | str] = (),
        approved_source_roots: Mapping[str, Sequence[Path | str]] | None = None,
        allowed_classes: Sequence[str] = _DEFAULT_CLASSES,
    ) -> SkillCandidate:
        """Construct one authorized candidate from a collector record."""
        if not isinstance(metadata, Mapping):
            raise SkillRankingInputError("skill metadata must be an object")
        name = _text(metadata.get("name"), "name")
        if not _NAME.fullmatch(name):
            raise SkillRankingInputError(f"noncanonical skill name: {name!r}")
        description = _text(metadata.get("description"), "description")
        if len(description) > _MAX_DESCRIPTION:
            raise SkillRankingInputError("skill description is oversized")
        raw_tags = metadata.get("tags", ())
        if isinstance(raw_tags, (str, bytes)) or not isinstance(raw_tags, Sequence):
            raise SkillRankingInputError("tags must be a sequence of strings")
        if len(raw_tags) > _MAX_TAGS:
            raise SkillRankingInputError("too many tags")
        tags: list[str] = []
        for tag in raw_tags:
            normalized = _text(tag, "tag").lower()
            if len(normalized) > _MAX_TAG_LENGTH or not _NAME.fullmatch(normalized):
                raise SkillRankingInputError(f"noncanonical tag: {tag!r}")
            if normalized in tags:
                raise SkillRankingInputError(f"duplicate tag: {normalized!r}")
            tags.append(normalized)
        skill_class = _text(metadata.get("class", metadata.get("class_")), "class")
        allowed = {str(item) for item in allowed_classes}
        if skill_class not in allowed:
            raise SkillRankingInputError(f"unsupported skill class: {skill_class!r}")
        source = _text(metadata.get("source"), "source")
        if source not in set(approved_sources):
            raise SkillRankingInputError(f"unapproved skill source: {source!r}")
        if (
            not isinstance(original_index, int)
            or isinstance(original_index, bool)
            or original_index < 0
        ):
            raise SkillRankingInputError(
                "original_index must be a non-negative integer"
            )
        raw_path = metadata.get("path", metadata.get("location"))
        if not isinstance(raw_path, (str, Path)) or not str(raw_path).strip():
            raise SkillRankingInputError("skill path is required")
        path = Path(raw_path)
        if not path.is_absolute():
            raise SkillRankingInputError("skill path must be absolute")
        try:
            resolved = path.resolve(strict=True)
        except OSError as exc:
            raise SkillRankingInputError("skill path cannot be resolved") from exc
        selected_roots = (
            approved_source_roots.get(source, ())
            if approved_source_roots is not None
            else approved_roots
        )
        roots = tuple(Path(root).resolve() for root in selected_roots)
        if not roots or not any(
            resolved == root or root in resolved.parents for root in roots
        ):
            raise SkillRankingInputError("skill path is outside approved roots")
        return cls(
            name,
            description,
            tuple(tags),
            skill_class,
            source,
            resolved,
            original_index,
        )


@dataclass(frozen=True)
class ScoreResult:
    score: float
    clipped_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class RankingPolicy:
    max_skills: int = 3
    additional_skill_threshold: float = 0.8
    low_confidence_threshold: float = 0.8

    def __post_init__(self) -> None:
        if self.max_skills < 1 or self.max_skills > 3:
            raise SkillRankingConfigurationError(
                "max_skills must be between one and three"
            )
        for value in (self.additional_skill_threshold, self.low_confidence_threshold):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise SkillRankingConfigurationError(
                    "ranking thresholds must be finite probabilities"
                )

    @classmethod
    def from_manifest(cls, manifest: Mapping[str, Any]) -> RankingPolicy:
        try:
            policy = manifest["policy"]
            return cls(
                policy["max_skills"],
                policy["additional_skill_threshold"],
                policy["low_confidence_threshold"],
            )
        except (KeyError, TypeError) as exc:
            raise SkillRankingConfigurationError(
                "manifest has no valid policy"
            ) from exc


@dataclass(frozen=True)
class RankingDiagnostics:
    candidate_scores: tuple[tuple[str, float], ...]
    selected_names: tuple[str, ...]
    forced_low_confidence: bool
    clipped_labels: tuple[str, ...] = ()
    token_counts: tuple[int, ...] = ()
    latencies_ms: tuple[float, ...] = ()
    pair_prompt_hashes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RankingResult:
    names: tuple[str, ...]
    diagnostics: RankingDiagnostics


def render_task(task: Mapping[str, Any]) -> str:
    """Render through the single evaluated Qwen task contract."""
    from lib.generate_task_json.qwen_prompt import render_task as render_qwen_task

    return render_qwen_task(task)


def render_skill(candidate: SkillCandidate) -> str:
    """Render through the single evaluated Qwen skill contract."""
    from lib.generate_task_json.qwen_prompt import render_skill as render_qwen_skill

    return render_qwen_skill(candidate)


class SkillRanker:
    """Validate a frozen inventory, score it, and apply the fixed cardinality policy."""

    def __init__(
        self,
        scorer: PairScorer,
        policy: RankingPolicy | None = None,
        *,
        max_candidates: int = _MAX_CANDIDATES,
    ) -> None:
        if max_candidates < 1:
            raise SkillRankingConfigurationError("max_candidates must be positive")
        self.scorer = scorer
        self.policy = policy or RankingPolicy()
        self.max_candidates = max_candidates

    def diagnostic_identity(self) -> Mapping[str, str]:
        """Return concrete scorer and policy identities for packet diagnostics."""
        identity_provider = getattr(self.scorer, "diagnostic_identity", None)
        raw_identity: Any = identity_provider() if callable(identity_provider) else {}
        values: dict[str, str] = (
            {str(key): str(value) for key, value in raw_identity.items()}
            if isinstance(raw_identity, Mapping)
            else {}
        )
        values.setdefault(
            "ranker",
            f"{type(self.scorer).__module__}.{type(self.scorer).__qualname__}",
        )
        values["policy"] = (
            f"max={self.policy.max_skills};additional="
            f"{self.policy.additional_skill_threshold};low="
            f"{self.policy.low_confidence_threshold}"
        )
        return values

    def _validate_inventory(
        self, skills: Sequence[SkillCandidate]
    ) -> tuple[SkillCandidate, ...]:
        if (
            isinstance(skills, (str, bytes))
            or not isinstance(skills, Sequence)
            or not skills
        ):
            raise SkillRankingInputError("skill inventory must be non-empty")
        if len(skills) > self.max_candidates:
            raise SkillRankingInputError("skill inventory exceeds candidate limit")
        names: set[str] = set()
        for candidate in skills:
            if not isinstance(candidate, SkillCandidate):
                raise SkillRankingInputError("inventory contains a non-candidate")
            if candidate.name in names:
                raise SkillRankingInputError(
                    f"duplicate skill name: {candidate.name!r}"
                )
            names.add(candidate.name)
        return tuple(skills)

    def rank(
        self, task: Mapping[str, Any], skills: Sequence[SkillCandidate]
    ) -> RankingResult:
        inventory = self._validate_inventory(skills)
        if not isinstance(task, Mapping):
            raise SkillRankingInputError("task must be an object")
        query = render_task(task)
        try:
            results = self.scorer.score(
                query, tuple(render_skill(item) for item in inventory)
            )
        except SkillRankingInputError:
            raise
        except Exception as exc:
            raise SkillRankingRuntimeError("pair scoring failed") from exc
        if not isinstance(results, list) or len(results) != len(inventory):
            raise SkillRankingRuntimeError("scorer returned the wrong number of scores")
        checked: list[tuple[SkillCandidate, ScoreResult]] = []
        clipped: list[str] = []
        for candidate, result in zip(inventory, results, strict=True):
            if (
                not isinstance(result, ScoreResult)
                or not math.isfinite(result.score)
                or not 0 <= result.score <= 1
            ):
                raise SkillRankingRuntimeError("scorer returned an invalid score")
            checked.append((candidate, result))
            clipped.extend(result.clipped_labels)
        ordered_all = sorted(
            checked, key=lambda pair: (-pair[1].score, pair[0].original_index)
        )
        blocked_names = _selection_blocked_names(task, inventory)
        ordered = [item for item in ordered_all if item[0].name not in blocked_names]
        if not ordered:
            raise SkillRankingInputError(
                "no selectable skills remain after assignment safety checks"
            )
        selected = [ordered[0]]
        for item in ordered[1 : self.policy.max_skills]:
            if item[1].score < self.policy.additional_skill_threshold:
                break
            selected.append(item)
        names = tuple(item[0].name for item in selected)
        diagnostics = RankingDiagnostics(
            tuple((item[0].name, item[1].score) for item in ordered_all),
            names,
            ordered[0][1].score < self.policy.low_confidence_threshold,
            tuple(clipped),
            tuple(getattr(self.scorer, "last_token_counts", ())),
            tuple(
                value * 1000
                for value in getattr(self.scorer, "last_request_seconds", ())
            ),
            tuple(getattr(self.scorer, "last_prompt_hashes", ())),
        )
        return RankingResult(names, diagnostics)


def _selection_blocked_names(
    task: Mapping[str, Any],
    inventory: Sequence[SkillCandidate],
) -> set[str]:
    """Block circular owner assignments and unusable factory update assignments."""
    targets = _skill_targets(task.get("filesToWrite", ()), "filesToWrite")
    read_targets = _skill_targets(task.get("filesToRead", ()), "filesToRead")
    existing_names = {candidate.name for candidate in inventory}
    blocked = targets & existing_names
    if not targets or targets & read_targets or targets <= existing_names:
        blocked.add("skill-factory")
    return blocked


def _skill_targets(values: Any, field: str) -> set[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise SkillRankingInputError(f"{field} must be a sequence")
    targets: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise SkillRankingInputError(f"{field} entries must be strings")
        match = re.search(r"(?:^|/)skills/([a-z0-9]+(?:-[a-z0-9]+)*)(?:/|$)", value)
        if match:
            targets.add(match.group(1))
    return targets
