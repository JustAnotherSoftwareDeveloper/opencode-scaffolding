"""Unit tests for lib.shared.slug."""

from __future__ import annotations

from lib.shared.slug import derive_slug


def test_basic_slug() -> None:
    """Simple text produces expected hyphenated slug."""
    assert derive_slug("Hello World") == "hello-world"


def test_special_characters_stripped() -> None:
    """Non-alphanumeric characters are removed."""
    assert derive_slug("Fix: bug in parser (v2)!") == "fix-bug-in-parser-v2"


def test_multiple_spaces_collapsed() -> None:
    """Multiple whitespace collapses to single hyphen."""
    assert derive_slug("many   spaces   here") == "many-spaces-here"


def test_trailing_hyphens_stripped() -> None:
    """Leading/trailing hyphens are removed."""
    assert derive_slug("---trim-me---") == "trim-me"


def test_truncation_at_word_boundary() -> None:
    """Long text is truncated at word boundary within max_length."""
    slug = derive_slug(
        "this-is-a-very-long-slug-that-should-be-truncated-somewhere",
        max_length=30,
    )
    assert len(slug) <= 30
    # The last hyphen within the first 30 chars is after "that"
    assert slug == "this-is-a-very-long-slug-that"


def test_truncation_no_hyphen_boundary() -> None:
    """When no hyphen boundary exists within truncation, strip cleanly."""
    slug = derive_slug("abcdefghijklmnopqrstuvwxyz", max_length=10)
    assert len(slug) <= 10


def test_empty_string() -> None:
    """Empty string produces empty slug."""
    assert derive_slug("") == ""


def test_only_special_characters() -> None:
    """Text with only special characters produces empty slug."""
    assert derive_slug("!@#$%") == ""


def test_numbers_preserved() -> None:
    """Numbers are preserved in the slug."""
    assert derive_slug("python 3 12 is great") == "python-3-12-is-great"
