"""
test_example.py — Tests for lib/example.py and cli/example.py.

This file covers:
- lib.example.example_message() — unit tests for the library function
- cli.example.main() — integration test via CliRunner

Run from ``scripts/python/``:

    uv run pytest tests/test_example.py -v
"""

from __future__ import annotations

import pytest

from lib.example import example_message

# ============================================================================
# Tests for lib.example.example_message()
# ============================================================================


class TestExampleMessage:
    """Tests for the ``example_message()`` library function."""

    def test_returns_expected_string(self) -> None:
        """Normal runtime value produces expected output."""
        result = example_message("python")
        assert result == "example runtime=python status=ok"

    def test_with_empty_string(self) -> None:
        """Empty string raises ValueError."""
        with pytest.raises(ValueError, match="runtime is required"):
            example_message("")

    def test_with_other_runtime(self) -> None:
        """Non-empty runtime produces the correct message."""
        result = example_message("node")
        assert result == "example runtime=node status=ok"

    def test_with_whitespace_runtime(self) -> None:
        """Whitespace-only string does NOT raise (only empty check)."""
        result = example_message("   ")
        # Whitespace is truthy, so it goes through normally
        assert "status=ok" in result


# ============================================================================
# Tests for cli.example.main()
# ============================================================================


class TestCliExample:
    """Tests for the ``cli.example`` module via CliRunner."""

    def test_main_success(self) -> None:
        """main() returns 0 and prints the example message."""
        from cli.example import main

        exit_code = main()
        assert exit_code == 0

    def test_main_prints_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """main() prints the expected message to stdout."""
        from cli.example import main

        main()
        captured = capsys.readouterr()
        assert "example runtime=python status=ok" in captured.out
