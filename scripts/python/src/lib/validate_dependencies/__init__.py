"""Public API for the validate_dependencies module.

Re-exports ``validate`` from :mod:`lib.validate_dependencies.core`.
"""

from __future__ import annotations

from lib.validate_dependencies.core import validate

__all__ = [
    "validate",
]
