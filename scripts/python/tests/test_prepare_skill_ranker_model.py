"""Deterministic tests for explicit model preparation; no network or Ollama."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

from cli import prepare_skill_ranker_model as prepare


class Source:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size: int) -> bytes:
        if hasattr(self, "done"):
            return b""
        self.done = True
        return b"model-bytes"


def test_preparation_is_fully_mocked_and_verifies_before_success(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = b"model-bytes"
    license_path = tmp_path / "LICENSE"
    license_path.write_text("Apache", encoding="utf-8")

    manifest = SimpleNamespace(
        model="qwen-test",
        data={
            "artifact": {
                "filename": "model.gguf",
                "url": "https://example.invalid/model.gguf",
                "sha256": hashlib.sha256(artifact).hexdigest(),
            },
            "assets": {"license": {"sha256": hashlib.sha256(b"Apache").hexdigest()}},
        },
        license_path=license_path,
    )

    calls = []
    monkeypatch.setattr(prepare, "load_manifest", lambda *_args, **_kwargs: manifest)
    monkeypatch.setattr(prepare, "urlopen", lambda *_args, **_kwargs: Source())
    monkeypatch.setattr(
        prepare, "OllamaQwenScorer", lambda *_args: calls.append("verify")
    )
    monkeypatch.setattr(
        prepare.subprocess,
        "run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = CliRunner().invoke(
        prepare.main,
        ["--cache-dir", str(tmp_path / "cache")],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "model": "qwen-test",
        "profile": "q8",
    }
    assert calls[0][0][0][:3] == ["ollama", "create", "qwen-test"]
    assert calls[-1] == "verify"


def test_bad_digest_fails_without_import_or_model_verification(
    tmp_path: Path, monkeypatch
) -> None:
    license_path = tmp_path / "LICENSE"
    license_path.write_text("Apache", encoding="utf-8")

    manifest = SimpleNamespace(
        model="qwen-test",
        data={
            "artifact": {"filename": "model.gguf", "url": "x", "sha256": "0" * 64},
            "assets": {"license": {"sha256": hashlib.sha256(b"Apache").hexdigest()}},
        },
        license_path=license_path,
    )

    imported = []
    monkeypatch.setattr(prepare, "load_manifest", lambda *_args, **_kwargs: manifest)
    monkeypatch.setattr(prepare, "urlopen", lambda *_args, **_kwargs: Source())
    monkeypatch.setattr(
        prepare.subprocess,
        "run",
        lambda *_args, **_kwargs: imported.append(True),
    )
    result = CliRunner().invoke(prepare.main, ["--cache-dir", str(tmp_path / "cache")])
    assert result.exit_code == 1
    assert "SHA-256" in result.output
    assert imported == []
    assert list((tmp_path / "cache").iterdir()) == []


def test_non_loopback_is_rejected_before_download(tmp_path: Path, monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        prepare,
        "urlopen",
        lambda *_args, **_kwargs: calls.append("url"),
    )
    result = CliRunner().invoke(
        prepare.main,
        [
            "--ollama-host",
            "http://example.com:11434",
            "--cache-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert calls == []
