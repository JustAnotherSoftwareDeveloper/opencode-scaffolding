"""Strict, package-safe loading of the checked Qwen ranker profiles."""

# The manifest's immutable pins are intentionally kept visually identical to
# their upstream values; wrapping those literals obscures audit comparisons.
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when a manifest or one of its immutable assets is invalid."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PROFILES = ("q8", "q4")
_ROOT = "generate_task_json"
_PROFILE_PINS: dict[str, dict[str, str]] = {
    "q8": {
        "filename": "Qwen3-Reranker-4B.Q8_0.gguf",
        "url": "https://huggingface.co/QuantFactory/Qwen3-Reranker-4B-GGUF/resolve/2a42c7aa9c702165da87b09dec164a54d973123b/Qwen3-Reranker-4B.Q8_0.gguf",
        "artifact_sha256": "27feb99a25d2f9b6d305bef699ac74fecfeb66ff3c73ef2212aab71bdfe2fb8d",
        "ollama_model": "hf.co/QuantFactory/Qwen3-Reranker-4B-GGUF:Q8_0",
        "ollama_digest": "78bbe0fc51686fcb75e1d6af3f957d24599b4a9aedb1adeed0f516e29768e25f",
        "quantization": "Q8_0",
        "report": "qwen3-reranker-4b-q8-ollama-evaluation.json",
        "report_sha256": "0d2caf7ced308fac4b2af0bdb8ba5d01921ff0f8b0d874f93a11b5c4a2c1c80e",
    },
    "q4": {
        "filename": "Qwen3-Reranker-4B.Q4_K_M.gguf",
        "url": "https://huggingface.co/QuantFactory/Qwen3-Reranker-4B-GGUF/resolve/2a42c7aa9c702165da87b09dec164a54d973123b/Qwen3-Reranker-4B.Q4_K_M.gguf",
        "artifact_sha256": "6113f1556b2c099725bf043ecb2748e4efa106c5fd32c3bf8c4f3ce8877e3c92",
        "ollama_model": "hf.co/QuantFactory/Qwen3-Reranker-4B-GGUF:q4_K_M",
        "ollama_digest": "2de967e79703f558c472460eafa8847283b523e036771f68fde40317ff97bbe4",
        "quantization": "Q4_K_M",
        "report": "qwen3-reranker-4b-q4-ollama-evaluation.json",
        "report_sha256": "9a83c3b5db2385fd5a6c962ed7b528fa84ae518af6676accd7833ca90a34a185",
    },
}


@dataclass(frozen=True)
class Asset:
    path: str
    sha256: str


@dataclass(frozen=True)
class RankerManifest:
    profile: str
    data: dict[str, Any]
    tokenizer_path: Path
    license_path: Path

    @property
    def model(self) -> str:
        return self.data["ollama"]["model"]

    @property
    def num_ctx(self) -> int:
        return self.data["runtime"]["num_ctx"]


def _expect_keys(value: Any, required: set[str], where: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != required:
        raise ManifestError(f"{where} must contain exactly {sorted(required)}")
    return value


def _digest(value: Any, where: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ManifestError(f"{where} must be a lowercase SHA-256 digest")
    return value


def _asset(raw: Any, where: str) -> Asset:
    item = _expect_keys(raw, {"path", "sha256"}, where)
    path = item["path"]
    if (
        not isinstance(path, str)
        or not path.startswith("assets/")
        or ".." in Path(path).parts
    ):
        raise ManifestError(f"{where}.path must name a packaged asset")
    return Asset(path, _digest(item["sha256"], f"{where}.sha256"))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest {path}: {exc}") from exc
    return _expect_keys(
        value,
        {
            "schema_version",
            "profile",
            "model",
            "artifact",
            "ollama",
            "assets",
            "runtime",
            "prompt",
            "policy",
            "evaluation",
        },
        "manifest",
    )


def _validate(raw: dict[str, Any], expected_profile: str) -> None:
    if raw["schema_version"] != 1 or raw["profile"] != expected_profile:
        raise ManifestError("unsupported manifest version or profile")
    model = _expect_keys(
        raw["model"], {"name", "upstream_revision", "license"}, "model"
    )
    if model != {
        "name": "Qwen/Qwen3-Reranker-4B",
        "upstream_revision": "22e683669bc0f0bd69640a1354a6d0aebcfeede5",
        "license": "Apache-2.0",
    }:
        raise ManifestError("model pin is not the audited Qwen model")
    artifact = _expect_keys(
        raw["artifact"],
        {"repository", "revision", "filename", "url", "sha256"},
        "artifact",
    )
    if (
        artifact["repository"] != "QuantFactory/Qwen3-Reranker-4B-GGUF"
        or artifact["revision"] != "2a42c7aa9c702165da87b09dec164a54d973123b"
    ):
        raise ManifestError("artifact source pin mismatch")
    pins = _PROFILE_PINS[expected_profile]
    if artifact["filename"] != pins["filename"] or artifact["url"] != pins["url"]:
        raise ManifestError("artifact reference is not the approved profile pin")
    if _digest(artifact["sha256"], "artifact.sha256") != pins["artifact_sha256"]:
        raise ManifestError("artifact digest is not the approved profile pin")
    ollama = _expect_keys(
        raw["ollama"],
        {
            "model",
            "manifest_digest",
            "minimum_version",
            "architecture",
            "parameter_count",
            "parameter_size",
            "quantization",
        },
        "ollama",
    )
    if ollama["model"] != pins["ollama_model"]:
        raise ManifestError("Ollama model identity is not the approved profile pin")
    if (
        _digest(ollama["manifest_digest"], "ollama.manifest_digest")
        != pins["ollama_digest"]
    ):
        raise ManifestError("Ollama digest is not the approved profile pin")
    if ollama["minimum_version"] != "0.31.1":
        raise ManifestError("unsupported Ollama minimum version")
    if (
        ollama["architecture"] != "qwen3"
        or ollama["parameter_count"] != 4_410_057_216
        or ollama["parameter_size"] != "4.41B"
        or ollama["quantization"] != pins["quantization"]
    ):
        raise ManifestError("Ollama metadata is not the approved profile pin")
    assets = _expect_keys(raw["assets"], {"tokenizer", "license"}, "assets")
    _asset(assets["tokenizer"], "assets.tokenizer")
    _asset(assets["license"], "assets.license")
    runtime = _expect_keys(
        raw["runtime"],
        {
            "ollama_api",
            "num_ctx",
            "raw",
            "stream",
            "keep_alive",
            "temperature",
            "seed",
            "num_predict",
            "num_batch",
            "logprobs",
            "top_logprobs",
        },
        "runtime",
    )
    if runtime != {
        "ollama_api": "http://127.0.0.1:11434",
        "num_ctx": 8192,
        "raw": True,
        "stream": False,
        "keep_alive": "30m",
        "temperature": 0,
        "seed": 0,
        "num_predict": 1,
        "num_batch": 128,
        "logprobs": True,
        "top_logprobs": 20,
    }:
        raise ManifestError(
            "runtime profile is inconsistent with the evaluated contract"
        )
    prompt = _expect_keys(
        raw["prompt"], {"instruction", "prompt_version", "render_version"}, "prompt"
    )
    if (
        not prompt["instruction"]
        or prompt["prompt_version"] != "qwen3-reranker-4b-classifier-v1"
        or prompt["render_version"] != "task-skill-routing-signature-v2"
    ):
        raise ManifestError("invalid prompt pin")
    policy = _expect_keys(
        raw["policy"],
        {
            "missing_label_logprob",
            "additional_skill_threshold",
            "low_confidence_threshold",
            "max_skills",
        },
        "policy",
    )
    if policy != {
        "missing_label_logprob": -10.0,
        "additional_skill_threshold": 0.8,
        "low_confidence_threshold": 0.8,
        "max_skills": 3,
    }:
        raise ManifestError("invalid ranking policy")
    evaluation = _expect_keys(raw["evaluation"], {"report", "sha256"}, "evaluation")
    if evaluation["report"] != pins["report"]:
        raise ManifestError("evaluation report is not the approved profile pin")
    if _digest(evaluation["sha256"], "evaluation.sha256") != pins["report_sha256"]:
        raise ManifestError("evaluation digest is not the approved profile pin")


def _validate_pair(first: dict[str, Any], second: dict[str, Any]) -> None:
    """Ensure the two checked profiles share one scoring contract."""
    for key in ("model", "assets", "runtime", "prompt", "policy"):
        if first[key] != second[key]:
            raise ManifestError(f"Q8/Q4 {key} data is inconsistent")
    for key in ("repository", "revision"):
        if first["artifact"][key] != second["artifact"][key]:
            raise ManifestError(f"Q8/Q4 artifact {key} is inconsistent")
    if first["profile"] == second["profile"]:
        raise ManifestError("Q8/Q4 profiles are not distinct")


def _resource(asset: Asset) -> Path:
    name = Path(asset.path).name
    resource = resources.files("lib.generate_task_json").joinpath("assets", name)
    if not resource.is_file():
        raise ManifestError(f"missing packaged asset: {asset.path}")
    with resources.as_file(resource) as materialized:
        digest = hashlib.sha256(materialized.read_bytes()).hexdigest()
        if digest != asset.sha256:
            raise ManifestError(f"asset digest mismatch: {asset.path}")
        return materialized


def load_manifest(
    path: Path | str | None = None, profile: str = "q8"
) -> RankerManifest:
    """Load and verify one checked profile; Q4 is never selected implicitly."""
    if profile not in _PROFILES:
        raise ManifestError(f"unsupported profile: {profile}")
    manifest_path = (
        Path(path)
        if path is not None
        else Path(__file__).with_name(
            "ranker_manifest.json" if profile == "q8" else "ranker_manifest.q4.json"
        )
    )
    raw = _load_json(manifest_path)
    _validate(raw, profile)
    sibling_name = (
        "ranker_manifest.q4.json" if profile == "q8" else "ranker_manifest.json"
    )
    sibling_path = manifest_path.with_name(sibling_name)
    if sibling_path.is_file():
        sibling = _load_json(sibling_path)
        _validate(sibling, "q4" if profile == "q8" else "q8")
        _validate_pair(raw, sibling)
    tokenizer = _resource(_asset(raw["assets"]["tokenizer"], "assets.tokenizer"))
    license_file = _resource(_asset(raw["assets"]["license"], "assets.license"))
    return RankerManifest(profile, raw, tokenizer, license_file)


def load_ranker_manifest(
    path: Path | str | None = None, profile: str = "q8"
) -> RankerManifest:
    return load_manifest(path, profile)
