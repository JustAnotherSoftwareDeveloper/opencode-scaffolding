"""Deterministic Qwen classifier prompt rendering and token preflight.

The strings in this module are part of the ranker's scoring contract.  In
particular, this module intentionally does not use a chat-template helper:
Ollama receives the complete raw classifier prompt assembled here.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lib.generate_task_json.ranker import SkillRankingInputError

TASK_RENDER_VERSION = "task-skill-routing-signature-v2"
SKILL_RENDER_VERSION = "task-skill-routing-signature-v2"
QWEN_PROMPT_VERSION = "qwen3-reranker-4b-classifier-v1"
PLANNING_RENDER_VERSION = "planning-routing-signature-v2"
PLANNING_PROMPT_VERSION = "qwen3-reranker-4b-classifier-planning-v1"
QWEN_MAX_TOKENS = 8192

INSTRUCTION = (
    "Determine whether the candidate OpenCode skill contains procedures or reference "
    "material that are materially useful for executing the task. Rank direct owner "
    "skills above supporting references and unrelated skills."
)
PLANNING_INSTRUCTION = (
    "Determine whether the candidate OpenCode skill contains passive planning "
    "reference material that is materially useful for decomposing the planning request."
)
SYSTEM_PREFIX = (
    "<|im_start|>system\nJudge whether the Document meets the requirements based on "
    'the Query and the Instruct provided. Note that the answer can only be "yes" or '
    '"no".<|im_end|>\n<|im_start|>user\n'
)
ASSISTANT_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
_RESERVED_TOKEN_PREFIX = "<|"
# Compatibility names used by the detached evaluation harness.
PREFIX = SYSTEM_PREFIX
SUFFIX = ASSISTANT_SUFFIX


def _value(candidate: Any, name: str) -> Any:
    if isinstance(candidate, Mapping):
        return candidate.get(name)
    return getattr(candidate, name, None)


def _join(values: Any) -> str:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return str(values) if values is not None else ""
    return ", ".join(str(value) for value in values)


def render_task(task: Mapping[str, Any]) -> str:
    """Render all validated task fields in the evaluated, stable format."""
    if not isinstance(task, Mapping):
        raise SkillRankingInputError("task must be an object")
    instructions = task.get("executionInstructions", ())
    if not isinstance(instructions, Sequence) or isinstance(instructions, (str, bytes)):
        raise SkillRankingInputError("executionInstructions must be a sequence")
    steps: list[str] = []
    for item in instructions:
        if not isinstance(item, Mapping):
            raise SkillRankingInputError("execution instruction must be an object")
        step = item.get("step", "")
        action = item.get("action", "")
        line = f"{step}. {action}"
        # The evaluated fixtures did not contain per-step verification.  Add it
        # only when supplied, preserving their byte-for-byte rendering.
        if item.get("verification") is not None:
            line += f" (Verification: {item['verification']})"
        steps.append(line)
    verification = task.get("verification", ())
    if not isinstance(verification, Sequence) or isinstance(verification, (str, bytes)):
        raise SkillRankingInputError("verification must be a sequence")
    return (
        f"Purpose: {task.get('purpose', '')}\n"
        f"Context: {task.get('context', '')}\n"
        f"Files to read: {_join(task.get('filesToRead', ())) or '(none)'}\n"
        f"Files to write: {_join(task.get('filesToWrite', ())) or '(none)'}\n"
        f"Execution instructions:\n{chr(10).join(steps)}\n"
        f"Expected output: {task.get('expectedOutput', '')}\n"
        f"Verification: {'; '.join(str(value) for value in verification) or '(none)'}"
    )


def render_planning_request(description: str) -> str:
    """Render one complete planning description under the stable request label."""
    if not isinstance(description, str) or not description.strip():
        raise SkillRankingInputError("planning description must be a non-empty string")
    return f"Planning request: {description}"


def _structured_values(candidate: Any, field: str) -> Sequence[Any]:
    values = _value(candidate, field)
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise SkillRankingInputError(f"candidate {field} must be a sequence")
    return values


def _cue_value(cue: Any, field: str) -> Any:
    return cue.get(field) if isinstance(cue, Mapping) else getattr(cue, field, None)


def _render_text(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise SkillRankingInputError(
            f"candidate {field} must be a trimmed single-line string"
        )
    return value


def render_skill(candidate: Any) -> str:
    """Render only normalized routing metadata; source and path are excluded."""
    relationships = sorted(
        _structured_values(candidate, "relationships"),
        key=lambda relation: (
            str(_cue_value(relation, "role") or ""),
            str(_cue_value(relation, "target") or ""),
            str(_cue_value(relation, "rationale") or ""),
        ),
    )
    cues = sorted(
        _structured_values(candidate, "cues"),
        key=lambda cue: (
            str(_cue_value(cue, "facet") or ""),
            str(_cue_value(cue, "value") or ""),
            tuple(str(alias) for alias in (_cue_value(cue, "aliases") or ())),
        ),
    )
    if not relationships or not cues:
        raise SkillRankingInputError(
            "candidate cues and relationships must be non-empty"
        )
    relationship_lines = []
    for relation in relationships:
        role = _render_text(_cue_value(relation, "role"), "relationship role")
        if role not in ("owner", "support", "reference"):
            raise SkillRankingInputError("candidate relationship role is invalid")
        fields = [f"role={role}"]
        target = _cue_value(relation, "target")
        rationale = _cue_value(relation, "rationale")
        if target is not None:
            fields.append(f"target={_render_text(target, 'relationship target')}")
        if rationale is not None:
            fields.append(
                f"rationale={_render_text(rationale, 'relationship rationale')}"
            )
        relationship_lines.append("- " + "; ".join(fields))
    cue_lines = []
    for cue in cues:
        facet = _render_text(_cue_value(cue, "facet"), "cue facet")
        value = _render_text(_cue_value(cue, "value"), "cue value")
        fields = [
            f"facet={facet}",
            f"value={value}",
        ]
        aliases = _cue_value(cue, "aliases") or ()
        if not isinstance(aliases, Sequence) or isinstance(aliases, (str, bytes)):
            raise SkillRankingInputError("candidate cue aliases must be a sequence")
        if aliases:
            fields.append(
                "aliases="
                + ", ".join(_render_text(alias, "cue alias") for alias in aliases)
            )
        primary = _cue_value(cue, "primary")
        if primary is not None and not isinstance(primary, bool):
            raise SkillRankingInputError("candidate cue primary must be a boolean")
        if primary:
            fields.append("primary=true")
        cue_lines.append("- " + "; ".join(fields))
    name = _render_text(_value(candidate, "name"), "name")
    description = _render_text(_value(candidate, "description"), "description")
    skill_class = _render_text(
        _value(candidate, "skill_class") or _value(candidate, "class"), "class"
    )
    return (
        f"Skill name: {name}\n"
        f"Description: {description}\n"
        "Routing relationships:\n"
        + "\n".join(relationship_lines)
        + "\nRouting cues:\n"
        + "\n".join(cue_lines)
        + "\n"
        f"Class: {skill_class}"
    )


def compose_qwen_prompt(
    query: str,
    document: str,
    *,
    instruction: str = INSTRUCTION,
) -> str:
    """Compose the exact raw prompt used by the evaluated Qwen classifier."""
    for field, value in (
        ("instruction", instruction),
        ("query", query),
        ("document", document),
    ):
        if not isinstance(value, str) or not value:
            raise SkillRankingInputError(f"prompt {field} must be a non-empty string")
        if _RESERVED_TOKEN_PREFIX in value:
            raise SkillRankingInputError(
                f"prompt {field} contains a reserved control-token prefix"
            )
    return (
        SYSTEM_PREFIX
        + f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {document}"
        + ASSISTANT_SUFFIX
    )


@dataclass(frozen=True)
class TokenBudgetResult:
    prompt: str
    token_count: int
    limit: int = QWEN_MAX_TOKENS


@dataclass(frozen=True)
class QwenPromptResult:
    task: str
    skill: str
    prompt: str
    task_render_version: str = TASK_RENDER_VERSION
    skill_render_version: str = SKILL_RENDER_VERSION
    prompt_version: str = QWEN_PROMPT_VERSION
    token_count: int | None = None


def tokenizer_sha256(path: Path | str) -> str:
    """Return the digest of the pinned tokenizer file."""
    try:
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError as exc:
        raise SkillRankingInputError("pinned tokenizer cannot be read") from exc


class QwenTokenBudget:
    """Count complete prompts with a pinned ``tokenizer.json`` and reject overflow."""

    def __init__(
        self,
        tokenizer_path: Path | str,
        *,
        expected_sha256: str | None = None,
        limit: int = QWEN_MAX_TOKENS,
    ) -> None:
        if limit < 1:
            raise SkillRankingInputError("token budget must be positive")
        path = Path(tokenizer_path)
        if expected_sha256 is not None and tokenizer_sha256(path) != expected_sha256:
            raise SkillRankingInputError("pinned tokenizer digest does not match")
        try:
            from tokenizers import Tokenizer

            self._tokenizer = Tokenizer.from_file(str(path))
        except Exception as exc:
            raise SkillRankingInputError("pinned tokenizer is invalid") from exc
        self.tokenizer_path = path
        self.tokenizer_digest = tokenizer_sha256(path)
        self.limit = limit

    def count(self, prompt: str) -> int:
        if not isinstance(prompt, str):
            raise SkillRankingInputError("prompt must be a string")
        try:
            return len(self._tokenizer.encode(prompt).ids)
        except Exception as exc:
            raise SkillRankingInputError("prompt tokenization failed") from exc

    def preflight(self, prompt: str) -> TokenBudgetResult:
        count = self.count(prompt)
        if count > self.limit:
            raise SkillRankingInputError(
                f"complete Qwen prompt exceeds {self.limit} tokens: {count}"
            )
        return TokenBudgetResult(prompt, count, self.limit)


class QwenPromptRenderer:
    """Render a pair and optionally perform its complete-prompt token preflight."""

    def __init__(
        self,
        token_budget: QwenTokenBudget | None = None,
        *,
        instruction: str = INSTRUCTION,
    ) -> None:
        self.token_budget = token_budget
        self.instruction = instruction

    def render(self, task: Mapping[str, Any], candidate: Any) -> QwenPromptResult:
        query = render_task(task)
        skill = render_skill(candidate)
        prompt = compose_qwen_prompt(query, skill, instruction=self.instruction)
        count = (
            self.token_budget.preflight(prompt).token_count
            if self.token_budget
            else None
        )
        return QwenPromptResult(query, skill, prompt, token_count=count)


class QwenPlanningPromptRenderer:
    """Render a planning request and candidate without task-packet metadata."""

    def __init__(
        self,
        token_budget: QwenTokenBudget | None = None,
        *,
        instruction: str = PLANNING_INSTRUCTION,
    ) -> None:
        self.token_budget = token_budget
        self.instruction = instruction

    def render(self, description: str, candidate: Any) -> QwenPromptResult:
        query = render_planning_request(description)
        skill = render_skill(candidate)
        prompt = compose_qwen_prompt(query, skill, instruction=self.instruction)
        count = (
            self.token_budget.preflight(prompt).token_count
            if self.token_budget
            else None
        )
        return QwenPromptResult(
            query,
            skill,
            prompt,
            task_render_version=PLANNING_RENDER_VERSION,
            prompt_version=PLANNING_PROMPT_VERSION,
            token_count=count,
        )


class QwenPairPreflight:
    """Validate every complete task-candidate prompt before native transport setup."""

    def __init__(self, renderer: QwenPromptRenderer) -> None:
        if renderer.token_budget is None:
            raise SkillRankingInputError("pair preflight requires a token budget")
        self.renderer = renderer

    def __call__(
        self,
        tasks: Sequence[Mapping[str, Any]],
        candidates: Sequence[Any],
    ) -> None:
        for task in tasks:
            for candidate in candidates:
                self.renderer.render(task, candidate)
