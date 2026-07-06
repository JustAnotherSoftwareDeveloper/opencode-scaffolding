"""Derive a deterministic filename slug from a decomposition summary.

Consumers: init-state-file.
"""

from __future__ import annotations

import re

_MAX_SLUG_LENGTH = 60


def derive_slug(text: str, max_length: int = _MAX_SLUG_LENGTH) -> str:
    """Derive a lowercased, hyphenated slug from *text*.

    Args:
        text: The decomposition summary or any descriptive text.
        max_length: Maximum length of the slug (default 60).

    Returns:
        A slug suitable for use in a filename: ``<epoch>-<slug>.json``.

    The derivation:
    1. Lowercase the text.
    2. Strip non-alphanumeric characters (keep letters, digits, spaces, hyphens).
    3. Collapse whitespace to single hyphens.
    4. Truncate to *max_length*, breaking at a word boundary.
    5. Strip trailing hyphens and whitespace.
    """
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")

    if len(slug) <= max_length:
        return slug

    truncated = slug[:max_length]
    last_hyphen = truncated.rfind("-")
    if last_hyphen > 0:
        truncated = truncated[:last_hyphen]

    return truncated.strip("-")
