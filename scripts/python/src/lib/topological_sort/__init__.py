"""Public API for the topological_sort module.

Re-exports ``sort`` from :mod:`lib.topological_sort.core`.
"""

from __future__ import annotations

from lib.topological_sort.core import sort

__all__ = [
    "sort",
]
