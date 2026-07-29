"""Bounded, loopback-only Ollama adapter for the Qwen ranker.

This module intentionally uses no Ollama SDK.  The transport is a small
injectable boundary so all identity and scoring behaviour can be tested with
captured responses, without a running model.
"""

# Long request/metadata literals are kept readable for audit comparison.
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import math
import socket
import time
from collections.abc import Callable, Mapping, Sequence
from http.client import HTTPConnection, HTTPSConnection
from typing import Any, Protocol
from urllib.parse import urlparse

from .qwen_prompt import compose_qwen_prompt
from .ranker import (
    ScoreResult,
    SkillRankingConfigurationError,
    SkillRankingInputError,
    SkillRankingRuntimeError,
)
from .ranker_manifest import RankerManifest

_DEFAULT_HOST = "http://127.0.0.1:11434"
_ENDPOINTS = frozenset({"/api/version", "/api/tags", "/api/show", "/api/generate"})
_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
_DEFAULT_TIMEOUT = 10.0


class OllamaTransport(Protocol):
    def request(
        self, endpoint: str, payload: Mapping[str, Any] | None = None
    ) -> Any: ...


class OllamaError(SkillRankingRuntimeError):
    """Raised for an unavailable, malformed, or identity-inconsistent runtime."""


class LoopbackHTTPTransport:
    """Small bounded HTTP transport; no endpoint besides the four allowlisted ones."""

    def __init__(
        self,
        host: str = _DEFAULT_HOST,
        *,
        connect_timeout: float = 2.0,
        read_timeout: float = 10.0,
        max_response_bytes: int = _MAX_RESPONSE_BYTES,
    ) -> None:
        self.base = _validate_host(host)
        if connect_timeout <= 0 or read_timeout <= 0 or max_response_bytes <= 0:
            raise SkillRankingConfigurationError("transport bounds must be positive")
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.max_response_bytes = max_response_bytes

    def request(
        self, endpoint: str, payload: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        if endpoint not in _ENDPOINTS:
            raise OllamaError(f"unsupported Ollama endpoint: {endpoint}")
        parsed = urlparse(self.base)
        connection_class = (
            HTTPSConnection if parsed.scheme == "https" else HTTPConnection
        )
        hostname = parsed.hostname
        if hostname is None:  # Defensive; _validate_host rejects this earlier.
            raise SkillRankingConfigurationError("Ollama host has no hostname")
        connection = connection_class(
            hostname, parsed.port, timeout=self.connect_timeout
        )
        try:
            body = (
                None
                if payload is None
                else json.dumps(payload, separators=(",", ":")).encode()
            )
            connection.request(
                "GET" if body is None else "POST",
                endpoint,
                body=body,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            connection_socket = getattr(connection, "sock", None)
            if connection_socket is not None:
                connection_socket.settimeout(self.read_timeout)
            response = connection.getresponse()
            if not 200 <= response.status < 300:
                raise OllamaError(f"Ollama {endpoint} returned HTTP {response.status}")
            length = response.getheader("Content-Length")
            if length is not None and (
                not length.isdigit() or int(length) > self.max_response_bytes
            ):
                raise OllamaError(f"Ollama {endpoint} response is too large")
            data = response.read(self.max_response_bytes + 1)
            if len(data) > self.max_response_bytes:
                raise OllamaError(f"Ollama {endpoint} response is too large")
            try:
                value = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise OllamaError(f"Ollama {endpoint} returned invalid JSON") from exc
            if not isinstance(value, dict):
                raise OllamaError(f"Ollama {endpoint} JSON must be an object")
            return value
        except (OSError, TimeoutError) as exc:
            raise OllamaError(f"Ollama {endpoint} transport failed") from exc
        finally:
            connection.close()


def _validate_host(host: str) -> str:
    parsed = urlparse(host)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.username
        or parsed.password
        or not parsed.hostname
    ):
        raise SkillRankingConfigurationError("Ollama host must be an HTTP URL")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise SkillRankingConfigurationError(
            "Ollama host must not contain a path or query"
        )
    name = parsed.hostname.rstrip(".").lower()
    try:
        loopback = socket.inet_pton(socket.AF_INET, name).startswith(b"\x7f")
    except OSError:
        try:
            loopback = socket.inet_pton(socket.AF_INET6, name) == socket.inet_pton(
                socket.AF_INET6, "::1"
            )
        except OSError:
            loopback = name == "localhost"
    if not loopback:
        raise SkillRankingConfigurationError("Ollama must use a loopback host")
    return host.rstrip("/")


def _object(value: Any, endpoint: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise OllamaError(f"Ollama {endpoint} response must be an object")
    return value


def _version_at_least(actual: str, minimum: str) -> bool:
    def parts(value: str) -> tuple[int, ...]:
        raw = value.removeprefix("v").split("-", 1)[0].split(".")
        if len(raw) != 3 or any(not item.isdigit() for item in raw):
            raise OllamaError(f"invalid Ollama version: {value!r}")
        return tuple(int(item) for item in raw)

    return parts(actual) >= parts(minimum)


def _first(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _digest_for_model(tags: Mapping[str, Any], model: str) -> str:
    models = tags.get("models")
    if not isinstance(models, Sequence) or isinstance(models, (str, bytes)):
        raise OllamaError("Ollama /api/tags models must be an array")
    matches = [
        item
        for item in models
        if isinstance(item, Mapping) and item.get("name") == model
    ]
    if len(matches) != 1:
        raise OllamaError("Ollama model identity is missing or duplicated")
    digest = matches[0].get("digest")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(c not in "0123456789abcdef" for c in digest)
    ):
        raise OllamaError("Ollama model digest must be a full lowercase SHA-256 value")
    return digest


def _verify_show(show: Mapping[str, Any], manifest: RankerManifest) -> None:
    details = show.get("details")
    info = show.get("model_info")
    if not isinstance(details, Mapping) or not isinstance(info, Mapping):
        raise OllamaError("Ollama /api/show lacks model metadata")
    expected = manifest.data["ollama"]
    architecture = _first(details, "family", "architecture") or _first(
        info, "general.architecture", "architecture"
    )
    parameters = _first(details, "parameter_size", "parameters") or _first(
        info, "general.parameter_count", "parameter_count"
    )
    quantization = _first(details, "quantization_level", "quantization") or _first(
        info, "general.quantization_version", "quantization"
    )
    if (
        not isinstance(architecture, str)
        or architecture.lower() != expected["architecture"]
    ):
        raise OllamaError("Ollama model architecture does not match Qwen3")
    parameter_count = _first(info, "general.parameter_count", "parameter_count")
    if (
        parameters != expected["parameter_size"]
        or parameter_count != expected["parameter_count"]
    ):
        raise OllamaError("Ollama model parameter metadata does not match 4B")
    if (
        not isinstance(quantization, str)
        or quantization.upper() != expected["quantization"]
    ):
        raise OllamaError(
            "Ollama model quantization does not match the selected profile"
        )
    if show.get("model") not in {None, manifest.model}:
        raise OllamaError("Ollama /api/show model name mismatch")


class OllamaQwenScorer:
    """Verify one pinned local model, then score pairs sequentially."""

    def __init__(
        self,
        manifest: RankerManifest,
        host: str = _DEFAULT_HOST,
        *,
        transport: OllamaTransport | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        token_counter: Callable[[str], int] | None = None,
    ) -> None:
        if not math.isfinite(timeout) or timeout <= 0:
            raise SkillRankingConfigurationError("Ollama timeout must be positive")
        self.manifest = manifest
        self.host = _validate_host(host)
        self.timeout = timeout
        self.token_counter = token_counter
        self.transport = transport or LoopbackHTTPTransport(
            self.host, read_timeout=timeout
        )
        self.last_request_seconds: tuple[float, ...] = ()
        self.last_clipped_labels: tuple[tuple[str, ...], ...] = ()
        self.last_token_counts: tuple[int, ...] = ()
        self.last_prompt_hashes: tuple[str, ...] = ()
        self.last_load_seconds: tuple[float, ...] = ()
        self.runtime_version = ""
        self._verify_identity()

    def _call(
        self, endpoint: str, payload: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]:
        try:
            value = self.transport.request(endpoint, payload)
        except OllamaError:
            raise
        except Exception as exc:
            raise OllamaError(f"Ollama {endpoint} transport failed") from exc
        return _object(value, endpoint)

    def _verify_identity(self) -> None:
        version = self._call("/api/version")
        actual = version.get("version")
        minimum = self.manifest.data["ollama"]["minimum_version"]
        if not isinstance(actual, str) or not _version_at_least(actual, minimum):
            raise OllamaError(f"Ollama {actual!r} is older than {minimum}")
        self.runtime_version = actual
        digest = _digest_for_model(self._call("/api/tags"), self.manifest.model)
        if digest != self.manifest.data["ollama"]["manifest_digest"]:
            raise OllamaError("Ollama model manifest digest mismatch")
        _verify_show(
            self._call("/api/show", {"name": self.manifest.model}), self.manifest
        )

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
        results: list[ScoreResult] = []
        timings: list[float] = []
        clipped: list[tuple[str, ...]] = []
        token_counts: list[int] = []
        prompt_hashes: list[str] = []
        load_seconds: list[float] = []
        for document in documents:
            prompt = self._prompt(query, document)
            prompt_hashes.append(hashlib.sha256(prompt.encode("utf-8")).hexdigest())
            if self.token_counter is not None:
                try:
                    token_count = self.token_counter(prompt)
                except SkillRankingInputError:
                    raise
                except Exception as exc:
                    raise SkillRankingInputError(
                        "complete Qwen prompt tokenization failed"
                    ) from exc
                if (
                    isinstance(token_count, bool)
                    or not isinstance(token_count, int)
                    or token_count < 0
                ):
                    raise SkillRankingInputError(
                        "token counter returned an invalid count"
                    )
                if token_count > self.manifest.num_ctx:
                    raise SkillRankingInputError(
                        "complete Qwen pair exceeds the configured context"
                    )
                token_counts.append(token_count)
            payload = {
                "model": self.manifest.model,
                "prompt": prompt,
                "raw": self.manifest.data["runtime"]["raw"],
                "stream": self.manifest.data["runtime"]["stream"],
                "keep_alive": self.manifest.data["runtime"]["keep_alive"],
                "logprobs": self.manifest.data["runtime"]["logprobs"],
                "top_logprobs": self.manifest.data["runtime"]["top_logprobs"],
                "options": {
                    "temperature": self.manifest.data["runtime"]["temperature"],
                    "seed": self.manifest.data["runtime"]["seed"],
                    "num_predict": self.manifest.data["runtime"]["num_predict"],
                    "num_ctx": self.manifest.data["runtime"]["num_ctx"],
                    "num_batch": self.manifest.data["runtime"]["num_batch"],
                },
            }
            started = time.monotonic()
            response = self._call("/api/generate", payload)
            load_duration = response.get("load_duration", 0)
            if (
                isinstance(load_duration, bool)
                or not isinstance(load_duration, (int, float))
                or not math.isfinite(float(load_duration))
                or load_duration < 0
            ):
                raise OllamaError("Qwen load duration is malformed")
            result = parse_qwen_score(
                response, self.manifest.data["policy"]["missing_label_logprob"]
            )
            elapsed = time.monotonic() - started
            # Keep diagnostics bounded and content-free: prompts are never logged.
            timings.append(elapsed)
            clipped.append(result.clipped_labels)
            results.append(result)
            load_seconds.append(float(load_duration) / 1e9)
        self.last_request_seconds = tuple(timings)
        self.last_clipped_labels = tuple(clipped)
        self.last_token_counts = tuple(token_counts)
        self.last_prompt_hashes = tuple(prompt_hashes)
        self.last_load_seconds = tuple(load_seconds)
        return results

    def _prompt(self, query: str, document: str) -> str:
        return compose_qwen_prompt(
            query,
            document,
            instruction=self.manifest.data["prompt"]["instruction"],
        )

    def diagnostic_identity(self) -> Mapping[str, str]:
        """Return exact non-secret identities used for this scorer."""
        return {
            "model": self.manifest.data["ollama"]["manifest_digest"],
            "runtime": self.runtime_version,
            "tokenizer": self.manifest.data["assets"]["tokenizer"]["sha256"],
            "prompt": self.manifest.data["prompt"]["prompt_version"],
            "render": self.manifest.data["prompt"]["render_version"],
            "manifest": hashlib.sha256(
                json.dumps(
                    self.manifest.data,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
        }


def parse_qwen_score(
    response: Mapping[str, Any], missing: float = -10.0
) -> ScoreResult:
    if not isinstance(response, Mapping) or not math.isfinite(missing):
        raise OllamaError("Qwen response or missing-label value is malformed")
    token = response.get("response")
    if not isinstance(token, str) or token.strip().lower() not in {"yes", "no"}:
        raise OllamaError("Qwen generated a token other than yes or no")
    logprobs = response.get("logprobs")
    if (
        not isinstance(logprobs, Sequence)
        or isinstance(logprobs, (str, bytes))
        or not logprobs
    ):
        raise OllamaError("Qwen logprobs are missing or malformed")
    first = logprobs[0]
    if not isinstance(first, Mapping):
        raise OllamaError("Qwen first-token logprobs are malformed")
    alternatives = first.get("top_logprobs", first.get("top_logprobs_content"))
    if not isinstance(alternatives, Sequence) or isinstance(alternatives, (str, bytes)):
        raise OllamaError("Qwen top-logprobs are malformed")
    values: dict[str, float] = {}
    if isinstance(alternatives, Sequence) and not isinstance(
        alternatives, (str, bytes)
    ):
        for item in alternatives:
            if not isinstance(item, Mapping) or not isinstance(item.get("token"), str):
                raise OllamaError("Qwen top-logprob alternative is malformed")
            value = item.get("logprob")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise OllamaError("Qwen top-logprob value is malformed")
            if not math.isfinite(float(value)):
                raise OllamaError("Qwen top-logprob value is non-finite")
            label = item["token"].strip().lower()
            if label in {"yes", "no"}:
                values.setdefault(label, float(value))
    clipped = tuple(label for label in ("yes", "no") if label not in values)
    values.update({label: missing for label in clipped})
    if any(not math.isfinite(value) for value in values.values()):
        raise OllamaError("Qwen returned non-finite label evidence")
    high = max(values.values())
    denominator = math.exp(values["yes"] - high) + math.exp(values["no"] - high)
    score = math.exp(values["yes"] - high) / denominator
    if not math.isfinite(score):
        raise OllamaError("Qwen score is non-finite")
    return ScoreResult(score, clipped)
