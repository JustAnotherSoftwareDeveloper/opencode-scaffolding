"""Generate complete task packets from one frozen collector snapshot."""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from lib.generate_task_json.skill_inventory import (
    SkillInventoryError,
    validate_skill_inventory,
)
from lib.schema import load_task_packet_schema
from lib.shared.schema import validate_json_schema

SUMMARY_SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class GenerationValidationError(ValueError):
    """Raised when input or the final packet is invalid."""


class SummarySlugError(ValueError):
    """Raised when an output filename cannot be made safe."""


def generate_task_json(
    data: dict[str, Any],
    summary_slug: str | None = None,
    *,
    skills_index: list[dict[str, Any]],
    provider: object | None = None,
    project_root: Path | None = None,
    inventory_project_root: Path | None = None,
    output_dir: Path | None = None,
    output_file: Path | None = None,
    max_retries: int = 0,
) -> Path:
    """Publish a completed packet after all inventory and schema checks pass.

    ``inventory_project_root`` authorizes project-sourced skill paths, while
    ``project_root`` is only the legacy/default output root.  Callers that
    provide an explicit output destination must use the former so the two
    concerns cannot accidentally become mutually exclusive output options.
    """
    if provider is not None or max_retries:
        raise ValueError("direct selection accepts completed packets only")
    if output_file is not None and (
        output_dir is not None or project_root is not None or summary_slug is not None
    ):
        raise ValueError("output_file is mutually exclusive with output options")
    errors = validate_json_schema(data, load_task_packet_schema())
    if errors:
        raise GenerationValidationError(f"packet failed schema: {errors}")
    try:
        validate_skill_inventory(
            skills_index,
            project_root=inventory_project_root or project_root,
        )
    except SkillInventoryError as exc:
        raise GenerationValidationError(str(exc)) from exc

    result = data
    if summary_slug is None and output_file is None:
        summary_slug = _derive_slug(data["summary"])
        if summary_slug is None:
            raise SummarySlugError(
                f"cannot derive a valid slug from summary: {data['summary']!r}"
            )
    destination = _resolve_output_path(
        summary_slug, project_root, output_dir, output_file
    )
    _write_json_new(destination, result)
    return destination


def _derive_slug(summary: str) -> str | None:
    slug = re.sub(r"[^a-z0-9]+", "-", summary.lower()).strip("-")
    return slug if SUMMARY_SLUG_PATTERN.fullmatch(slug) else None


def _resolve_output_path(
    slug: str | None,
    project_root: Path | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> Path:
    if output_file is not None:
        if output_file.suffix != ".json":
            raise ValueError("output file must use a .json suffix")
        return output_file
    if slug is None:
        raise ValueError("summary_slug is required without output_file")
    if output_dir is not None and project_root is not None:
        raise ValueError("provide either output_dir or project_root, not both")
    return (
        output_dir or (project_root or Path.cwd()) / ".tasks"
    ) / f"{time.time_ns() // 1_000_000}-{slug}.json"


def _write_json_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    except FileExistsError as exc:
        raise OSError(f"output already exists: {path}") from exc
    finally:
        with suppress(FileNotFoundError):
            os.unlink(temporary)
