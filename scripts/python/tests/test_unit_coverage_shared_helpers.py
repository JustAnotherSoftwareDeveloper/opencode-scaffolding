"""Direct tests for optional shared helpers and import-time fallbacks."""

from __future__ import annotations

import builtins
import importlib
import sys
import typing
from pathlib import Path

import pytest

from lib.shared import _path_helper
from lib.shared import schema as shared_schema

pytestmark = pytest.mark.unit


def test_package_path_setup_inserts_once_and_returns_resolved_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Insert the source root at the front of sys.path exactly once."""
    expected = Path(_path_helper.__file__).resolve().parents[2]
    paths = [entry for entry in sys.path if entry != str(expected)]
    monkeypatch.setattr(sys, "path", paths)

    resolved = _path_helper.setup_package_path()
    assert resolved == expected
    assert sys.path[0] == str(expected)
    assert sys.path.count(str(expected)) == 1
    assert _path_helper.setup_package_path() == expected
    assert sys.path.count(str(expected)) == 1


def test_shared_schema_import_branches_and_fallback_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise type-checking imports and the optional jsonschema fallback."""
    with monkeypatch.context() as patch:
        patch.setattr(typing, "TYPE_CHECKING", True)
        importlib.reload(shared_schema)
        assert shared_schema._jsonschema is not None

    importlib.reload(shared_schema)
    original_import = builtins.__import__

    def without_jsonschema(
        name: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ):
        if name == "jsonschema":
            raise ImportError("optional validation dependency unavailable")
        return original_import(name, globals, locals, fromlist, level)

    with monkeypatch.context() as patch:
        patch.setattr(builtins, "__import__", without_jsonschema)
        fallback = importlib.reload(shared_schema)
        assert fallback._HAS_JSONSCHEMA is False
        assert fallback.validate_json_schema("wrong", {}) == [
            "Instance must be a dict"
        ]
        assert fallback.validate_json_schema(
            {"name": "present"}, {"required": "not-an-array"}
        ) == []
        assert fallback.validate_json_schema(
            {"name": "present"}, {"required": ["name", "version"]}
        ) == ["version"]

    importlib.reload(shared_schema)
    assert shared_schema._HAS_JSONSCHEMA is True
