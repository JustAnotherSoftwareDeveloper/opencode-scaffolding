"""conftest.py — Ensure the project root is on ``sys.path`` for pytest.

When pytest collects tests, the project root (``scripts/python/``) is not
automatically on ``sys.path`` the way the runtime wrapper inserts it during
normal execution.  This file prepends it so that ``from lib.collect_skills.*``
imports resolve correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
