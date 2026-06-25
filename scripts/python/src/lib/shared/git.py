"""Git root walkup utility.

Consumers: shared by generated script CLIs.

Provides a single function that walks up the directory tree to find
the root of a Git repository (the ancestor that contains ``.git/``).
"""

from __future__ import annotations

from pathlib import Path


def find_git_root(start: Path | None = None) -> Path | None:
    """Walk up from *start* to find the repository root containing ``.git/``.

    Args:
        start: The directory to start the upward search from.
               Defaults to the current working directory.

    Returns:
        The absolute path of the first ancestor that contains a ``.git/``
        directory, or ``None`` if no ``.git/`` is found up to the filesystem root.
    """
    if start is None:
        start = Path.cwd()

    current = start.resolve()
    for ancestor in [current, *current.parents]:
        if (ancestor / ".git").is_dir():
            return ancestor

    return None
