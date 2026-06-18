"""conftest.py — Ensure the project ``src/`` directory is on ``sys.path`` for pytest.

When pytest collects tests, the project root (``scripts/python/``) is not
automatically on ``sys.path`` the way the runtime wrapper inserts it during
normal execution.  This file prepends ``src/`` so that ``from lib.collect_skills.*``
imports resolve correctly against the new ``src/lib/collect_skills/`` layout.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECT_SRC))
