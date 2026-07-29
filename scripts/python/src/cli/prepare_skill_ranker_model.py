"""Explicit, reproducible acquisition and import of a checked ranker model."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path
from urllib.request import urlopen

import click

from lib.generate_task_json.ollama_ranker import (
    LoopbackHTTPTransport,
    OllamaQwenScorer,
)
from lib.generate_task_json.ranker_manifest import ManifestError, load_manifest


@click.command(name="prepare-skill-ranker-model")
@click.option(
    "--ranker-manifest", type=click.Path(exists=True, path_type=Path), default=None
)
@click.option(
    "--model-profile", type=click.Choice(("q8", "q4")), default="q8", show_default=True
)
@click.option("--ollama-host", default="http://127.0.0.1:11434", show_default=True)
@click.option(
    "--cache-dir", type=click.Path(file_okay=False, path_type=Path), default=None
)
def main(
    ranker_manifest: Path | None,
    model_profile: str,
    ollama_host: str,
    cache_dir: Path | None,
) -> None:
    """Download, verify, import, and verify the pinned local Ollama artifact."""
    try:
        LoopbackHTTPTransport(ollama_host)
        environment = {**os.environ, "OLLAMA_HOST": ollama_host}
        manifest = load_manifest(ranker_manifest, model_profile)
        artifact = manifest.data["artifact"]
        target_dir = cache_dir or Path(tempfile.gettempdir()) / "opencode-ranker"
        target_dir.mkdir(parents=True, exist_ok=True)
        if (
            hashlib.sha256(manifest.license_path.read_bytes()).hexdigest()
            != manifest.data["assets"]["license"]["sha256"]
        ):
            raise RuntimeError("packaged license digest does not match the manifest")
        target, digest = _obtain_artifact(
            target_dir,
            artifact["filename"],
            artifact["url"],
            artifact["sha256"],
        )
        # Ollama import is intentionally confined to this explicit command.
        subprocess.run(
            ["ollama", "create", manifest.model, "-f", "-"],
            check=True,
            env=environment,
            input=f"FROM {json.dumps(str(target))}\n",
            text=True,
        )
        OllamaQwenScorer(manifest, ollama_host)
        click.echo(
            json.dumps(
                {
                    "model": manifest.model,
                    "profile": model_profile,
                    "artifact_sha256": digest,
                },
                sort_keys=True,
            )
        )
    except (
        ManifestError,
        OSError,
        RuntimeError,
        subprocess.SubprocessError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _obtain_artifact(
    target_dir: Path,
    filename: str,
    url: str,
    expected_digest: str,
) -> tuple[Path, str]:
    """Reuse a verified cache entry or atomically publish one verified download."""
    target = target_dir / filename
    if target.exists():
        digest = _file_digest(target)
        if digest != expected_digest:
            raise RuntimeError("cached artifact SHA-256 does not match the manifest")
        return target, digest

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{filename}.",
        dir=target_dir,
    )
    temporary = Path(temporary_name)
    digest_state = hashlib.sha256()
    try:
        with os.fdopen(descriptor, "wb") as output:
            with urlopen(url, timeout=60) as source:
                while chunk := source.read(1024 * 1024):
                    digest_state.update(chunk)
                    output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        digest = digest_state.hexdigest()
        if digest != expected_digest:
            raise RuntimeError(
                "downloaded artifact SHA-256 does not match the manifest"
            )
        os.link(temporary, target)
        return target, digest
    finally:
        with suppress(OSError):
            temporary.unlink()


if __name__ == "__main__":  # pragma: no cover
    main()
