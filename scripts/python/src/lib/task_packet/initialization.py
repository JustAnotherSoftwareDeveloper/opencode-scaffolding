"""Validate and atomically publish canonical task packets."""

from __future__ import annotations

import json
import os
import tempfile
import time
from contextlib import suppress
from pathlib import Path

from lib.schema import load_task_packet_schema
from lib.validate_task_structure.core import validate_root


class InvalidTaskPacketError(ValueError):
    """Raised when a packet fails canonical task-packet validation."""


class TaskPacketSchemaError(RuntimeError):
    """Raised when the canonical task-packet schema cannot be loaded."""


def initialize_task_packet(packet: object, output_dir: Path) -> Path:
    """Validate *packet* and atomically publish it under *output_dir*."""
    try:
        schema = load_task_packet_schema()
    except Exception as exc:
        raise TaskPacketSchemaError(
            f"failed to load canonical task-packet schema: {exc}"
        ) from exc

    valid, errors = validate_root(packet, schema)
    if not valid:
        raise InvalidTaskPacketError(
            "packet must satisfy the canonical task-packet schema: "
            + "; ".join(errors)
        )
    assert isinstance(packet, dict)
    slug = packet["slug"]
    assert isinstance(slug, str)  # Established by canonical root validation.

    timestamp = time.time_ns() // 1_000_000
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{timestamp}-{slug}.json"

    fd, temporary_path = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=output_dir
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(packet, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary_path, destination)
        except FileExistsError as exc:
            raise FileExistsError(
                f"output already exists: {destination}"
            ) from exc
    finally:
        with suppress(FileNotFoundError):
            os.unlink(temporary_path)

    return destination
