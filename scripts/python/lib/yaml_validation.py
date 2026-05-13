from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class YamlValidationError(Exception):
    """Raised when a YAML document fails validation."""


def load_yaml(path: Path) -> Any:
    """Load YAML from an explicit file path."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise YamlValidationError(f"file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise YamlValidationError(f"invalid YAML in {path}: {exc}") from exc
    except OSError as exc:
        raise YamlValidationError(f"could not read {path}: {exc}") from exc


def validate_yaml_path(yaml_path: str | Path) -> None:
    """Validate YAML syntax."""
    load_yaml(Path(yaml_path))
