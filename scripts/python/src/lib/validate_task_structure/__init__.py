"""Public API for the validate_task_structure module.

Re-exports ``validate`` and private helpers from
:mod:`lib.validate_task_structure.core`.

The private helpers are intentionally re-exported so that validators and
external consumers (e.g., tests) have a single import target through the
package public API instead of reaching into ``.core`` directly.
"""

from __future__ import annotations

from lib.validate_task_structure.core import (
    _validate_execution_steps,
    _validate_file_array,
    _validate_uuid_v4,
    validate,
)

__all__ = [
    "_validate_execution_steps",
    "_validate_file_array",
    "_validate_uuid_v4",
    "validate",
]
