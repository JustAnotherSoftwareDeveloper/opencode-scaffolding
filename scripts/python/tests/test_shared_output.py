"""Tests for the shared output module."""

from __future__ import annotations

import json

from lib.shared.output import format_error, format_json, format_text_result


class TestFormatJson:
    """Tests for ``format_json()``."""

    def test_dict_output(self) -> None:
        """A dict is serialized as formatted JSON with trailing newline."""
        result = format_json({"name": "test", "count": 42})
        parsed = json.loads(result)
        assert parsed == {"name": "test", "count": 42}
        assert result.endswith("\n")

    def test_list_output(self) -> None:
        """A list is serialized as formatted JSON with trailing newline."""
        result = format_json([1, 2, 3])
        assert json.loads(result) == [1, 2, 3]

    def test_indent_control(self) -> None:
        """Indentation level is configurable."""
        result = format_json({"a": 1}, indent=4)
        assert "    " in result  # 4-space indent

    def test_sort_keys(self) -> None:
        """Keys can be sorted."""
        result = format_json({"z": 1, "a": 2}, sort_keys=True)
        assert result.index('"a"') < result.index('"z"')

    def test_default_serializer(self) -> None:
        """Non-serializable types use the default callable."""
        result = format_json({"path": "/tmp/test"})
        assert json.loads(result) == {"path": "/tmp/test"}

    def test_empty_dict(self) -> None:
        """Empty dict produces ``{}`` with trailing newline."""
        result = format_json({})
        assert result == "{}\n"


class TestFormatTextResult:
    """Tests for ``format_text_result()``."""

    def test_single_entry(self) -> None:
        """A single key-value pair produces one line."""
        result = format_text_result({"name": "test"})
        assert result == "name: test\n"

    def test_multiple_entries(self) -> None:
        """Multiple entries produce one line each."""
        result = format_text_result({"name": "test", "count": "42"})
        lines = result.strip().split("\n")
        assert len(lines) == 2

    def test_custom_separator(self) -> None:
        """A custom separator is used between key and value."""
        result = format_text_result({"name": "test"}, separator=" = ")
        assert result == "name = test\n"

    def test_empty_mapping(self) -> None:
        """Empty mapping produces just a trailing newline."""
        result = format_text_result({})
        assert result == "\n"

    def test_numeric_values(self) -> None:
        """Numeric values are converted to strings."""
        result = format_text_result({"count": 42})
        assert result == "count: 42\n"


class TestFormatError:
    """Tests for ``format_error()``."""

    def test_standard_prefix(self) -> None:
        """Error message starts with ``Error: ``."""
        result = format_error("something went wrong")
        assert result == "Error: something went wrong\n"

    def test_empty_message(self) -> None:
        """An empty message still gets the prefix."""
        result = format_error("")
        assert result == "Error: \n"
