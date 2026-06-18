"""
test_example.py — Example / template test file for this project.

This file is self-contained: it defines a simple utility function and
tests it using plain ``assert`` statements.  It also demonstrates a
pytest fixture to provide reusable test data.

Use this file as a reference when writing new tests.  Run from the
``scripts/python/`` directory:

    uv run pytest tests/test_example.py -v
"""

from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Utility function under test (defined inline so the test is self-contained)
# ---------------------------------------------------------------------------


def add(a: int, b: int) -> int:
    """Return the sum of *a* and *b*."""
    return a + b


# ---------------------------------------------------------------------------
# Fixture – provides reusable test data
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_numbers() -> dict[str, tuple[int, int]]:
    """Return a dictionary of sample integer pairs for arithmetic tests."""
    return {
        "positive": (3, 5),
        "negative": (-2, -7),
        "mixed": (-4, 10),
        "zero": (0, 0),
    }


# ---------------------------------------------------------------------------
# Tests – plain ``assert``, no unittest.TestCase
# ---------------------------------------------------------------------------


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

    # ------------------------------------------------------------------
    # Test using the fixture
    # ------------------------------------------------------------------

    def test_add_with_fixture(self, sample_numbers: dict[str, tuple[int, int]]) -> None:
        """Verify ``add`` for every pair supplied by the fixture."""
        for label, (a, b) in sample_numbers.items():
            expected = a + b
            assert add(a, b) == expected, f"Failed for {label}: {a} + {b} != {expected}"


# ---------------------------------------------------------------------------
# Standalone test functions (outside a class) are also valid pytest style.
# ---------------------------------------------------------------------------


def test_add_commutative() -> None:
    """Addition is commutative: a + b == b + a."""
    assert add(7, 3) == add(3, 7)


def test_add_type_error() -> None:
    """Passing a non-integer should raise TypeError."""
    with pytest.raises(TypeError):
        a: Any = "foo"
        add(a, 3)
