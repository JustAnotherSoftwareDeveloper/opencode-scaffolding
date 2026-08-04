"""Path bootstrap helper for CLI entry points.

Consumers: collect-skills, init-task-packet, generate-uuids, topological-sort,
validate-task-structure, example, skill-validator.

When running via ``uv run``, the project root (``scripts/python/``) is placed
on ``sys.path``, but ``src/`` is *not*.  This means that direct
``src/``-relative imports like ``from lib.schema import load_schema`` fail
unless ``src/`` is explicitly added to ``sys.path`` at import time.

This module provides a single function — :func:`setup_package_path` — that
every CLI entry point under ``src/cli/`` should call at module level (before
any ``src/``-relative imports) to bootstrap the Python path.
"""

from __future__ import annotations

import sys
from pathlib import Path


def setup_package_path() -> Path:
    """Resolve the ``src/`` directory and add it to ``sys.path[0]``.

    ``uv run`` sets up the project root (``scripts/python/``) on ``sys.path``,
    but not the ``src/`` subdirectory.  Since all source code lives under
    ``src/`` (e.g. ``src/lib/...``, ``src/cli/...``), a ``src/``-relative
    import like ``from lib.schema import load_schema`` will fail with
    ``ModuleNotFoundError`` unless ``src/`` is explicitly inserted into
    ``sys.path`` at import time.

    Call this function at module level in every CLI entry point before any
    ``src/``-relative imports::

        from lib.shared._path_helper import setup_package_path
        setup_package_path()

    The function is idempotent — it only inserts ``src/`` once.

    Returns:
        The resolved ``src/`` :class:`~pathlib.Path`.
    """
    src = Path(__file__).resolve().parents[2]
    src_str = str(src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    return src
