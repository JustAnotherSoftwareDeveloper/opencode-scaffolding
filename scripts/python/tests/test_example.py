"""
test_example.py — Tests for lib/example.py and cli/example.py.

This file covers:
- lib.example.example_message() — unit tests for the library function
- cli.example.main() — integration test via CliRunner

Also retains the original self-contained ``add`` tests as reference.

Run from ``scripts/python/``:

    uv run pytest tests/test_example.py -v
"""

from __future__ import annotations

from typing import Any

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


# ============================================================================
# Original self-contained example tests (retained for reference)
# ============================================================================


def add(a: int, b: int) -> int:
    """Return the sum of *a* and *b*."""
    return a + b


@pytest.fixture
def sample_numbers() -> dict[str, tuple[int, int]]:
    """Return a dictionary of sample integer pairs for arithmetic tests."""
    return {
        "positive": (3, 5),
        "negative": (-2, -7),
        "mixed": (-4, 10),
        "zero": (0, 0),
    }


class TestAdd:
    """Group related tests for the ``add`` function."""

    def test_add_positive(self) -> None:
        """Two positive integers."""
        assert add(1, 2) == 3

    def test_add_negative(self) -> None:
        """Two negative integers."""
        assert add(-1, -2) == -3

    def test_add_positive_and_negative(self) -> None:
        """Mixed signs."""
        assert add(-5, 5) == 0

    def test_add_zero(self) -> None:
        """Zero is the additive identity."""
        assert add(0, 0) == 0
        assert add(0, 42) == 42
        assert add(42, 0) == 42

    def test_add_with_large_numbers(self) -> None:
        """Large integers (still within Python's arbitrary-precision ints)."""
        assert add(1_000_000, 2_000_000) == 3_000_000

    def test_add_with_fixture(self, sample_numbers: dict[str, tuple[int, int]]) -> None:
        """Verify ``add`` for every pair supplied by the fixture."""
        for label, (a, b) in sample_numbers.items():
            expected = a + b
            assert add(a, b) == expected, f"Failed for {label}: {a} + {b} != {expected}"


def test_add_commutative() -> None:
    """Addition is commutative: a + b == b + a."""
    assert add(7, 3) == add(3, 7)


def test_add_type_error() -> None:
    """Passing a non-integer should raise TypeError."""
    with pytest.raises(TypeError):
        a: Any = "foo"
        add(a, 3)