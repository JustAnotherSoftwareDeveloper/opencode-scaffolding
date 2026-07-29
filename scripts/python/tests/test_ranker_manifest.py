"""Strict manifest and packaged-resource tests; no Ollama is contacted."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.generate_task_json.ranker_manifest import ManifestError, load_manifest

ROOT = Path(__file__).parents[1]
Q8 = ROOT / "src/lib/generate_task_json/ranker_manifest.json"


def test_production_profiles_load_packaged_assets() -> None:
    q8 = load_manifest(profile="q8")
    q4 = load_manifest(profile="q4")
    assert q8.profile == "q8" and q4.profile == "q4"
    assert q8.num_ctx == q4.num_ctx == 8192
    assert q8.tokenizer_path.is_file() and q8.license_path.is_file()


@pytest.mark.parametrize("profile", ["q8", "q4"])
def test_manifest_is_strict_about_profile_and_assets(
    tmp_path: Path, profile: str
) -> None:
    source = Q8 if profile == "q8" else Q8.with_name("ranker_manifest.q4.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    data["unexpected"] = True
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ManifestError, match="exactly"):
        load_manifest(path, profile)


def test_manifest_rejects_digest_path_traversal_and_bad_profile(tmp_path: Path) -> None:
    data = json.loads(Q8.read_text(encoding="utf-8"))
    data["assets"]["tokenizer"]["path"] = "assets/../tokenizer.json"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ManifestError, match="packaged asset"):
        load_manifest(path)
    with pytest.raises(ManifestError, match="unsupported profile"):
        load_manifest(profile="q3")


def test_manifest_reports_missing_or_invalid_files(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="cannot read manifest"):
        load_manifest(tmp_path / "missing.json")
    malformed = tmp_path / "malformed.json"
    malformed.write_text("[]", encoding="utf-8")
    with pytest.raises(ManifestError, match="exactly"):
        load_manifest(malformed)


def test_manifest_detects_packaged_asset_digest_failure(tmp_path: Path) -> None:
    data = json.loads(Q8.read_text(encoding="utf-8"))
    data["assets"]["license"]["sha256"] = "0" * 64
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ManifestError, match="asset digest mismatch"):
        load_manifest(path)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("artifact", "filename", "Different.Q8_0.gguf"),
        ("artifact", "url", "https://example.invalid/model.gguf"),
        ("artifact", "sha256", "0" * 64),
        ("ollama", "model", "hf.co/QuantFactory/Qwen3-Reranker-4B-GGUF:other"),
        ("ollama", "manifest_digest", "1" * 64),
        ("evaluation", "report", "different-ollama-evaluation.json"),
    ],
)
def test_custom_manifest_cannot_replace_profile_pins(
    tmp_path: Path,
    section: str,
    field: str,
    value: str,
) -> None:
    data = json.loads(Q8.read_text(encoding="utf-8"))
    data[section][field] = value
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ManifestError, match="profile pin"):
        load_manifest(path)
