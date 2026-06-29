"""Public API for the validate_and_format_output module.

Re-exports ``validate_and_format`` from :mod:`lib.validate_and_format_output.core`.
"""

from __future__ import annotations

from lib.validate_and_format_output.core import validate_and_format

__all__ = [
    "validate_and_format",
]
