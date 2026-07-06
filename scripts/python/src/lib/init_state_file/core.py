"""State file initialization — derive path, guard against collision, write stub.

Consumers: :mod:`cli.init_state_file`.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from lib.shared.output import format_error


def init_state(output_dir: str) -> str:
    """Create and write a stub decomposition state file.

    Derives ``<epoch>-decomposition.json``, creates the output directory
    if needed, guards against filename collision, and writes an empty
    ``{"summary": "", "tasks": []}`` payload.  Returns the absolute path
    to the state file as a string.

    Args:
        output_dir: Path to the ``.tasks/`` directory.

    Returns:
        Absolute path to the created state file.

    Raises:
        FileExistsError: If a state file with the same epoch already exists.
        OSError: If directory creation or file write fails.
    """
    out = Path(output_dir).resolve()
    epoch = int(time.time())

    # Attempt up to 10 times with incremented epoch to avoid collision.
    max_attempts = 10
    for _attempt in range(max_attempts):
        filename = f"{epoch}-decomposition.json"
        filepath = out / filename
        try:
            out.mkdir(parents=True, exist_ok=True)
            # Use os.open with O_CREAT|O_EXCL to atomically check for existence.
            fd = os.open(str(filepath), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump({"summary": "", "tasks": []}, fh)
            return str(filepath)
        except FileExistsError:
            epoch += 1
            continue
        except OSError as exc:
            raise OSError(f"Failed to create state file {filepath}: {exc}") from exc

    raise OSError(
        format_error(
            f"Could not create state file in {out} after {max_attempts} attempts"
        )
    )
