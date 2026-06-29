"""Public API for the schema module.

Re-exports ``load_schema`` from :mod:`lib.schema.core`.
"""

from __future__ import annotations

from lib.schema.core import load_schema

__all__ = [
    "load_schema",
]
