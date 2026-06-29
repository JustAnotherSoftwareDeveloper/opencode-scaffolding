"""Tests for the shared schema module."""

from __future__ import annotations

import pytest

from lib.shared.schema import (
    validate_json_schema,
    validate_required_keys,
    validate_type,
)


class TestValidateRequiredKeys:
    """Tests for ``validate_required_keys()``."""

    def test_all_present(self) -> None:
        """All required keys present returns empty list."""
        result = validate_required_keys(
            {"name": "test", "version": "1.0"}, ["name", "version"]
        )
        assert result == []

    def test_some_missing(self) -> None:
        """Missing keys are reported."""
        result = validate_required_keys(
            {"name": "test"}, ["name", "version", "description"]
        )
        assert result == ["version", "description"]

    def test_empty_data(self) -> None:
        """Empty data reports all required keys as missing."""
        result = validate_required_keys({}, ["name", "version"])
        assert result == ["name", "version"]

    def test_no_required_keys(self) -> None:
        """Empty required list returns empty."""
        result = validate_required_keys({"name": "test"}, [])
        assert result == []

    def test_extra_keys_ignored(self) -> None:
        """Keys in data but not in required are ignored."""
        result = validate_required_keys({"name": "test", "extra": "ignored"}, ["name"])
        assert result == []


class TestValidateType:
    """Tests for ``validate_type()``."""

    def test_all_match(self) -> None:
        """All fields match expected types."""
        data = {"name": "hello", "count": 42, "active": True}
        schema = {"name": str, "count": int, "active": bool}
        assert validate_type(data, schema) == []

    def test_type_mismatch(self) -> None:
        """A field with wrong type is reported."""
        data = {"name": "hello", "count": "not-an-int"}
        schema = {"name": str, "count": int}
        errors = validate_type(data, schema)
        assert len(errors) == 1
        assert "count" in errors[0]
        assert "int" in errors[0]
        assert "str" in errors[0]

    def test_missing_key_not_reported(self) -> None:
        """A missing key is not reported as a type error."""
        data = {"name": "hello"}
        schema = {"name": str, "count": int}
        assert validate_type(data, schema) == []

    def test_empty_schema(self) -> None:
        """Empty schema returns no errors."""
        data = {"name": "hello"}
        assert validate_type(data, {}) == []


class TestValidateJsonSchema:
    """Tests for ``validate_json_schema()``."""

    def test_valid_with_jsonschema(self) -> None:
        """Valid data against a simple JSON Schema."""
        instance = {"name": "test", "version": "1.0"}
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
        }
        errors = validate_json_schema(instance, schema)
        assert errors == []

    def test_invalid_with_jsonschema(self) -> None:
        """Invalid data produces error messages."""
        instance = {"name": 42}
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
            },
        }
        errors = validate_json_schema(instance, schema)
        assert len(errors) > 0

    def test_not_a_dict_no_jsonschema(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Instance must be a dict when jsonschema is absent."""
        monkeypatch.setattr("lib.shared.schema._HAS_JSONSCHEMA", False)
        errors = validate_json_schema("not a dict", {"required": ["name"]})
        assert "must be a dict" in errors[0].lower()

    def test_missing_required_no_jsonschema(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Required key check works without jsonschema."""
        monkeypatch.setattr("lib.shared.schema._HAS_JSONSCHEMA", False)
        errors = validate_json_schema(
            {"name": "test"}, {"required": ["name", "version"]}
        )
        assert errors == ["version"]

    def test_non_list_required_no_jsonschema(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Non-list ``required`` in schema returns empty list."""
        monkeypatch.setattr("lib.shared.schema._HAS_JSONSCHEMA", False)
        errors = validate_json_schema({"name": "test"}, {"required": "not-a-list"})
        assert errors == []
