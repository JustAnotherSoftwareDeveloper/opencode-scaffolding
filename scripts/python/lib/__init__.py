"""Reusable Python helper modules for OpenCode automation scripts."""

from lib.runbook_xml import (
    load_runbook,
    validate_runbook,
    RunbookLoadResult,
    LoadedStep,
    RunbookLoadError,
    InvariantViolation,
    XmlValidationError,
    detect_runbook_format,
)
from lib.runbook_state import (
    seed_runbook_state,
    seed_runbook_state_xml,
    create_default_manifest,
    create_default_manifests_for_v3,
)

__all__ = [
    "load_runbook",
    "validate_runbook",
    "RunbookLoadResult",
    "LoadedStep",
    "RunbookLoadError",
    "InvariantViolation",
    "XmlValidationError",
    "detect_runbook_format",
    "seed_runbook_state",
    "seed_runbook_state_xml",
    "create_default_manifest",
    "create_default_manifests_for_v3",
]
