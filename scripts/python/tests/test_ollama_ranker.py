"""Frozen, offline tests for the Ollama identity and scoring boundary."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from lib.generate_task_json.ollama_ranker import (
    LoopbackHTTPTransport,
    OllamaError,
    OllamaQwenScorer,
    _digest_for_model,
    _version_at_least,
    parse_qwen_score,
)
from lib.generate_task_json.qwen_prompt import PLANNING_INSTRUCTION
from lib.generate_task_json.ranker import (
    SkillRankingConfigurationError,
    SkillRankingInputError,
)
from lib.generate_task_json.ranker_manifest import load_manifest

FIXTURES = Path(__file__).parent / "fixtures" / "ollama_ranker"


class FrozenTransport:
    def __init__(self, frozen: dict) -> None:
        self.frozen = frozen
        self.calls: list[tuple[str, Mapping[str, Any] | None]] = []

    def request(
        self, endpoint: str, payload: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        self.calls.append((endpoint, payload))
        if endpoint == "/api/version":
            return self.frozen["version"]
        if endpoint == "/api/tags":
            return self.frozen["tags"]
        if endpoint == "/api/show":
            return self.frozen["show"]
        if endpoint == "/api/generate":
            return self.frozen["generate"]
        raise AssertionError(endpoint)


def frozen(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.parametrize(
    ("profile", "file", "expected"),
    [("q8", "q8-success.json", 0.90025), ("q4", "q4-success.json", 0.00005545)],
)
def test_identity_profiles_and_exact_request(
    profile: str, file: str, expected: float
) -> None:
    manifest = load_manifest(profile=profile)
    transport = FrozenTransport(frozen(file))
    scorer = OllamaQwenScorer(
        manifest, transport=transport, token_counter=lambda _prompt: 114
    )
    before = list(transport.calls)
    result = scorer.score("query", ["document"])
    assert result[0].score == pytest.approx(expected, rel=0.01)
    assert scorer.last_clipped_labels == (((),) if profile == "q8" else (("yes",),))
    assert [call[0] for call in before] == ["/api/version", "/api/tags", "/api/show"]
    endpoint, request = transport.calls[-1]
    assert endpoint == "/api/generate"
    assert request == {
        "model": manifest.model,
        "prompt": scorer._prompt("query", "document"),
        "raw": True,
        "stream": False,
        "keep_alive": "30m",
        "logprobs": True,
        "top_logprobs": 20,
        "options": {
            "temperature": 0,
            "seed": 0,
            "num_predict": 1,
            "num_ctx": 8192,
            "num_batch": 128,
        },
    }


def test_default_instruction_and_identities_match_manifest() -> None:
    manifest = load_manifest(profile="q8")
    scorer = OllamaQwenScorer(
        manifest, transport=FrozenTransport(frozen("q8-success.json"))
    )
    policy_identity = hashlib.sha256(
        json.dumps(
            manifest.data["policy"], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()

    assert scorer.instruction == manifest.data["prompt"]["instruction"]
    assert scorer.diagnostic_identity() == {
        "model": manifest.data["ollama"]["manifest_digest"],
        "runtime": "0.31.1",
        "tokenizer": manifest.data["assets"]["tokenizer"]["sha256"],
        "prompt": manifest.data["prompt"]["prompt_version"],
        "render": manifest.data["prompt"]["render_version"],
        "policy": policy_identity,
        "manifest": scorer.diagnostic_identity()["manifest"],
    }


def test_planning_instruction_is_used_deterministically_without_changing_pins() -> None:
    manifest = load_manifest(profile="q8")
    first = OllamaQwenScorer(
        manifest,
        transport=FrozenTransport(frozen("q8-success.json")),
        instruction=PLANNING_INSTRUCTION,
        prompt_identity="qwen3-reranker-4b-classifier-planning-v1",
        render_identity="planning-request-v1",
        policy_identity="planning-policy-v1",
        token_counter=lambda prompt: len(prompt),
    )
    second = OllamaQwenScorer(
        manifest,
        transport=FrozenTransport(frozen("q8-success.json")),
        instruction=PLANNING_INSTRUCTION,
        prompt_identity="qwen3-reranker-4b-classifier-planning-v1",
        render_identity="planning-request-v1",
        policy_identity="planning-policy-v1",
        token_counter=lambda prompt: len(prompt),
    )

    assert first._prompt("planning request", "candidate") == second._prompt(
        "planning request", "candidate"
    )
    assert PLANNING_INSTRUCTION in first._prompt("planning request", "candidate")
    assert first.diagnostic_identity()["prompt"] == (
        "qwen3-reranker-4b-classifier-planning-v1"
    )
    assert first.diagnostic_identity()["render"] == "planning-request-v1"
    assert first.diagnostic_identity()["policy"] == "planning-policy-v1"
    result = first.score("planning request", ["candidate"])
    assert result[0].score == pytest.approx(0.90025, rel=0.01)
    assert first.last_token_counts == (
        len(first._prompt("planning request", "candidate")),
    )


@pytest.mark.parametrize(
    "field",
    ["instruction", "prompt_identity", "render_identity", "policy_identity"],
)
@pytest.mark.parametrize("value", ["", "   ", 42, False])
def test_custom_instruction_and_identities_reject_invalid_values(
    field: str, value: object
) -> None:
    kwargs: dict[str, Any] = {field: value}
    with pytest.raises(SkillRankingConfigurationError):
        OllamaQwenScorer(
            load_manifest(profile="q8"),
            transport=FrozenTransport(frozen("q8-success.json")),
            **kwargs,
        )


def test_custom_identities_do_not_bypass_runtime_or_model_pins() -> None:
    data = frozen("q8-success.json")
    data["version"]["version"] = "0.30.0"
    with pytest.raises(OllamaError):
        OllamaQwenScorer(
            load_manifest(profile="q8"),
            transport=FrozenTransport(data),
            instruction=PLANNING_INSTRUCTION,
            prompt_identity="custom-prompt",
            render_identity="custom-render",
            policy_identity="custom-policy",
        )


def test_sequential_reuse_and_failure_does_not_score_remaining() -> None:
    data = frozen("q8-success.json")
    data["generate"] = [data["generate"], {"response": "maybe", "logprobs": []}]

    class Sequential(FrozenTransport):
        def request(
            self, endpoint: str, payload: Mapping[str, Any] | None = None
        ) -> dict[str, Any]:
            self.calls.append((endpoint, payload))
            if endpoint == "/api/generate":
                return self.frozen["generate"].pop(0)
            return super().request(endpoint, payload)

    transport = Sequential(data)
    scorer = OllamaQwenScorer(load_manifest(profile="q8"), transport=transport)
    with pytest.raises(OllamaError):
        scorer.score("q", ["a", "b"])
    assert [endpoint for endpoint, _ in transport.calls].count("/api/generate") == 2


@pytest.mark.parametrize(
    "host",
    [
        "http://example.com:11434",
        "ftp://127.0.0.1",
        "http://127.0.0.1/path",
        "http://user@127.0.0.1",
    ],
)
def test_loopback_and_timeout_bounds(host: str) -> None:
    with pytest.raises(SkillRankingConfigurationError):
        LoopbackHTTPTransport(host)
    with pytest.raises(SkillRankingConfigurationError):
        OllamaQwenScorer(
            load_manifest(profile="q8"), host="http://127.0.0.1", timeout=0
        )


def test_transport_endpoint_status_content_and_response_bounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = LoopbackHTTPTransport(max_response_bytes=3)
    with pytest.raises(OllamaError):
        transport.request("/api/delete")

    class Response:
        status = 500
        sock = None

        def getheader(self, _name: str) -> str | None:
            return None

        def read(self, _size: int) -> bytes:
            return b"{}"

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            pass

        def getresponse(self):
            return Response()

        def close(self):
            pass

    monkeypatch.setattr(
        "lib.generate_task_json.ollama_ranker.HTTPConnection", Connection
    )
    with pytest.raises(OllamaError, match="HTTP 500"):
        transport.request("/api/version")


@pytest.mark.parametrize(
    "actual, minimum", [("0.31.1", "0.31.1"), ("v0.32.0-dev", "0.31.1")]
)
def test_version_and_digest_helpers(actual: str, minimum: str) -> None:
    assert _version_at_least(actual, minimum)
    assert (
        _digest_for_model({"models": [{"name": "m", "digest": "a" * 64}]}, "m")
        == "a" * 64
    )
    with pytest.raises(OllamaError):
        _digest_for_model({"models": []}, "m")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data["version"].update(version="0.30.0"),
        lambda data: data["version"].update(version="bad"),
        lambda data: data["tags"].update(models="bad"),
        lambda data: data["tags"]["models"][0].update(digest="A" * 64),
        lambda data: data["show"]["details"].update(family="llama"),
        lambda data: data["show"]["details"].update(parameter_size="7B"),
        lambda data: data["show"]["model_info"].update(
            {"general.parameter_count": 14_000_000_000}
        ),
        lambda data: data["show"]["details"].update(quantization_level="Q4_K_M"),
        lambda data: data["show"].update(model="other"),
    ],
)
def test_identity_mismatch_is_rejected(mutate) -> None:
    data = frozen("q8-success.json")
    mutate(data)
    with pytest.raises(OllamaError):
        OllamaQwenScorer(load_manifest(profile="q8"), transport=FrozenTransport(data))


def test_transport_rejects_invalid_json_shape_and_oversized_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = LoopbackHTTPTransport(max_response_bytes=3)

    class Response:
        status = 200
        sock = None

        def getheader(self, _name: str) -> str | None:
            return "not-a-number"

        def read(self, _size: int) -> bytes:
            return b"{}"

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            pass

        def getresponse(self):
            return Response()

        def close(self):
            pass

    monkeypatch.setattr(
        "lib.generate_task_json.ollama_ranker.HTTPConnection", Connection
    )
    with pytest.raises(OllamaError):
        transport.request("/api/version")


@pytest.mark.parametrize(
    "response",
    [
        {"response": "maybe", "logprobs": []},
        {"response": "yes", "logprobs": []},
        {
            "response": "yes",
            "logprobs": [{"top_logprobs": [{"token": "yes", "logprob": float("nan")}]}],
        },
    ],
)
def test_parser_rejects_malformed_and_nonfinite(response: dict) -> None:
    with pytest.raises(OllamaError):
        parse_qwen_score(response)


def test_parser_fallback_is_finite_and_deterministic() -> None:
    parsed = parse_qwen_score(
        {
            "response": "NO",
            "logprobs": [{"top_logprobs": [{"token": "no", "logprob": -1}]}],
        }
    )
    assert parsed.clipped_labels == ("yes",)
    assert parsed.score == pytest.approx(1 / (1 + 2.718281828459045**9))
    with pytest.raises(OllamaError):
        parse_qwen_score(
            {"response": "yes", "logprobs": [{"top_logprobs": []}]}, float("inf")
        )


def test_parser_uses_first_normalized_duplicate_label() -> None:
    parsed = parse_qwen_score(
        {
            "response": "yes",
            "logprobs": [
                {
                    "top_logprobs": [
                        {"token": "yes", "logprob": -0.1},
                        {"token": " yes", "logprob": -5.0},
                        {"token": "no", "logprob": -2.0},
                    ]
                }
            ],
        }
    )
    assert parsed.score == pytest.approx(1 / (1 + 2.718281828459045**-1.9))


def test_token_budget_and_counter_errors_are_input_failures() -> None:
    manifest = load_manifest(profile="q8")
    scorer = OllamaQwenScorer(
        manifest,
        transport=FrozenTransport(frozen("q8-success.json")),
        token_counter=lambda _: 8193,
    )
    with pytest.raises(SkillRankingInputError):
        scorer.score("q", ["d"])
    scorer = OllamaQwenScorer(
        manifest,
        transport=FrozenTransport(frozen("q8-success.json")),
        token_counter=lambda _: True,
    )
    with pytest.raises(SkillRankingInputError):
        scorer.score("q", ["d"])
