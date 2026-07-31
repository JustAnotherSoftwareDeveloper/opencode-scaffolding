"""Private, deterministic diagnostics for skill ranking.

Diagnostics are deliberately a separate boundary from the task packet.  This
module accepts already-derived identities and never serializes task text,
contexts, or resolved paths.  A sink must successfully publish diagnostics
before its caller publishes a task (normal and shadow sinks use the same
fail-closed contract).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

DIAGNOSTICS_VERSION = "ranking-diagnostics-v1"
BUNDLE_VERSION = "ranking-diagnostics-bundle-v1"
DEFAULT_MAX_BYTES = 64 * 1024
_MAX_DEPTH = 8
_MAX_ITEMS = 256
_MAX_STRING = 512
# Diagnostic callers pass identities, rather than source material.  Keep this
# deny-list at the serialization boundary as a second line of defence for
# optional ``extra`` values and future record types.
_PRIVATE_KEYS = frozenset(
    {
        "task",
        "context",
        "query",
        "prompt",
        "description",
        "body",
        "skill",
        "skills",
        "resolved_path",
        "path",
        "filesToRead",
        "filesToWrite",
    }
)


def _is_private_key(key: object) -> bool:
    """Match sensitive field names without allowing casing bypasses."""
    return str(key).lower() in {item.lower() for item in _PRIVATE_KEYS}


def canonical_hash(value: Any) -> str:
    """Hash a stable JSON representation (never Python's process hash)."""
    return hashlib.sha256(
        json.dumps(
            _identity_value(value),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _identity_value(value: Any) -> Any:
    """Canonicalize identity input without lossy diagnostic size limits."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("identity values must be finite")
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key): _identity_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_identity_value(item) for item in value]
    return str(value)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _bounded(value), ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _bounded(value: Any, depth: int = 0) -> Any:
    """Return JSON-safe, deterministic data with bounded nesting and size."""
    if depth >= _MAX_DEPTH:
        return "[depth-limited]"
    if value is None or isinstance(value, (str, int, bool)):
        if isinstance(value, str):
            return value[:_MAX_STRING]
        return value
    if isinstance(value, float):
        return value if value == value and abs(value) != float("inf") else "[nonfinite]"
    if isinstance(value, Path):
        # Paths are never diagnostic payloads; callers should provide identities.
        return "[path-redacted]"
    if isinstance(value, Mapping):
        return (
            {
                str(key)[:_MAX_STRING]: _bounded(item, depth + 1)
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
                if not _is_private_key(key)
            }
            if len(value) <= _MAX_ITEMS
            else {
                str(key)[:_MAX_STRING]: _bounded(item, depth + 1)
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))[
                    :_MAX_ITEMS
                ]
                if not _is_private_key(key)
            }
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_bounded(item, depth + 1) for item in value[:_MAX_ITEMS]]
    return str(value)[:_MAX_STRING]


def canonical_json(value: Any, *, max_bytes: int = DEFAULT_MAX_BYTES) -> bytes:
    """Serialize bounded JSON, rejecting rather than truncating valid records."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    result = _canonical_bytes(value)
    if len(result) > max_bytes:
        raise ValueError("diagnostic record exceeds configured size")
    return result


def _identity(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("diagnostic identities must be non-empty strings")
    return value


@dataclass(frozen=True)
class RankingDiagnosticRecord:
    """Versioned content-free evidence for one ranking operation."""

    model_hash: str
    runtime_hash: str
    tokenizer_hash: str
    prompt_hash: str
    render_hash: str
    policy_hash: str
    inventory_hash: str
    task_hash: str
    pair_prompt_hashes: tuple[str, ...] = ()
    candidate_scores: tuple[tuple[str, float], ...] = ()
    token_counts: tuple[int, ...] = ()
    clipped_labels: tuple[str, ...] = ()
    latencies_ms: tuple[float, ...] = ()
    selected_names: tuple[str, ...] = ()
    assignment_mode: str = "qwen"
    forced_low_confidence: bool = False
    schema_version: str = DIAGNOSTICS_VERSION
    extra: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "model_hash",
            "runtime_hash",
            "tokenizer_hash",
            "prompt_hash",
            "render_hash",
            "policy_hash",
            "inventory_hash",
            "task_hash",
        ):
            _identity(getattr(self, name))
        if self.assignment_mode not in {"lexical", "shadow", "qwen"}:
            raise ValueError("unsupported assignment mode")
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in self.token_counts
        ):
            raise ValueError("token counts must be non-negative integers")
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
            or value > 1
            for _, value in self.candidate_scores
        ):
            raise ValueError("candidate scores must be finite probabilities")
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
            for value in self.latencies_ms
        ):
            raise ValueError("latencies must be finite non-negative values")

    def as_dict(self) -> dict[str, Any]:
        """Return the stable public schema; raw task and path fields are absent."""
        data = asdict(self)
        data["candidate_scores"] = [list(item) for item in self.candidate_scores]
        data["extra"] = dict(self.extra)
        return _bounded(data)

    def serialize(self, *, max_bytes: int = DEFAULT_MAX_BYTES) -> bytes:
        return canonical_json(self.as_dict(), max_bytes=max_bytes)


@dataclass(frozen=True)
class PlanningSelectionDiagnosticRecord:
    """Content-free evidence for one dynamic planning selection.

    Every value that could identify source content is represented by a hash.
    The metadata snapshot is the run-scoped, dynamically discovered inventory;
    it is not a cache of descriptions or skill bodies.
    """

    model_hash: str
    runtime_hash: str
    tokenizer_hash: str
    prompt_hash: str
    renderer_hash: str
    policy_hash: str
    metadata_snapshot_hash: str
    query_hash: str
    candidate_scores: tuple[tuple[str, float], ...] = ()
    latency_ms: float = 0.0
    selected_names: tuple[str, ...] = ()
    schema_version: str = DIAGNOSTICS_VERSION
    extra: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "model_hash",
            "runtime_hash",
            "tokenizer_hash",
            "prompt_hash",
            "renderer_hash",
            "policy_hash",
            "metadata_snapshot_hash",
            "query_hash",
        ):
            _identity(getattr(self, name))
        if (
            not isinstance(self.latency_ms, (int, float))
            or isinstance(self.latency_ms, bool)
            or not math.isfinite(self.latency_ms)
            or self.latency_ms < 0
        ):
            raise ValueError("latency must be a finite non-negative value")
        if any(
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not math.isfinite(score)
            or score < 0
            or score > 1
            for _, score in self.candidate_scores
        ):
            raise ValueError("candidate scores must be finite probabilities")

    def as_dict(self) -> dict[str, Any]:
        """Return hashes and numeric evidence only; never source content."""
        data = asdict(self)
        data["candidate_scores"] = [list(item) for item in self.candidate_scores]
        data["extra"] = dict(self.extra)
        return _bounded(data)

    def serialize(self, *, max_bytes: int = DEFAULT_MAX_BYTES) -> bytes:
        return canonical_json(self.as_dict(), max_bytes=max_bytes)


# Short name for callers that use the planning domain rather than the full
# record name.  The alias keeps one schema and one publication implementation.
PlanningDiagnosticRecord = PlanningSelectionDiagnosticRecord


@dataclass(frozen=True)
class RankingDiagnosticBundle:
    """One atomic diagnostic artifact for every task in a generated packet."""

    records: tuple[RankingDiagnosticRecord, ...]
    schema_version: str = BUNDLE_VERSION

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("diagnostic bundle must contain at least one record")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "records": [record.as_dict() for record in self.records],
        }

    def serialize(self, *, max_bytes: int = DEFAULT_MAX_BYTES) -> bytes:
        return canonical_json(self.as_dict(), max_bytes=max_bytes)


DiagnosticPayload = (
    RankingDiagnosticRecord
    | PlanningSelectionDiagnosticRecord
    | RankingDiagnosticBundle
)


class DiagnosticSink(Protocol):
    def publish(self, record: DiagnosticPayload) -> None: ...


class AtomicDiagnosticSink:
    """Atomically publish one bounded record and remove temporary output on error."""

    def __init__(self, path: Path | str, *, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        self.path = Path(path)
        self.max_bytes = max_bytes

    def publish(self, record: DiagnosticPayload) -> None:
        payload = record.serialize(max_bytes=self.max_bytes)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise RuntimeError("diagnostic destination already exists")
        temporary: str | None = None
        try:
            descriptor, temporary = tempfile.mkstemp(
                prefix=f".{self.path.name}.", dir=self.path.parent
            )
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, self.path)
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                "diagnostic publication failed; task publication must stop"
            ) from exc
        finally:
            if temporary is not None:
                with suppress(OSError):
                    os.unlink(temporary)


class NullDiagnosticSink:
    """Explicit test sink that validates records without writing content."""

    def publish(self, record: DiagnosticPayload) -> None:
        record.serialize()


class CompositeDiagnosticSink:
    """Publish to every configured sink, raising before task publication."""

    def __init__(self, sinks: Sequence[DiagnosticSink]) -> None:
        self.sinks = tuple(sinks)

    def publish(self, record: DiagnosticPayload) -> None:
        if not self.sinks:
            raise RuntimeError("at least one diagnostics sink is required")
        for sink in self.sinks:
            sink.publish(record)


def publish_diagnostics(
    record: DiagnosticPayload,
    sink: DiagnosticSink | None,
) -> None:
    """Fail closed when a configured sink is absent or rejects publication."""
    if sink is None:
        raise RuntimeError("configured diagnostics sink is required before publication")
    sink.publish(record)


def publish_planning_diagnostics(
    record: PlanningSelectionDiagnosticRecord,
    sink: DiagnosticSink | None,
) -> None:
    """Atomically publish planning evidence through the configured sink."""
    publish_diagnostics(record, sink)
