"""Public API for the schema module.

Re-exports ``load_schema`` from :mod:`lib.schema.core`.
"""

from __future__ import annotations

from lib.schema.core import load_schema, load_task_packet_schema

__all__ = [
    "load_schema",
    "load_task_packet_schema",
]
