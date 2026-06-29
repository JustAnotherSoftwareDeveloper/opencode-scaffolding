"""Public API for the generate_uuids module.

Re-exports ``generate`` from :mod:`lib.generate_uuids.core`.
"""

from __future__ import annotations

from lib.generate_uuids.core import generate

__all__ = [
    "generate",
]
