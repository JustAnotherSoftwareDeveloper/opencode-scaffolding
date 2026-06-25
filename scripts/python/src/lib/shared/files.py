"""File/path utilities shared by: collect-skills, count-tokens, validate-skill.

Consumers: shared by generated script CLIs.
"""

from __future__ import annotations

from pathlib import Path


def resolve_path(path_str: str, base: Path | None = None) -> Path:
    """Resolve *path_str* to an absolute :class:`Path`.

    If *path_str* is relative, it is resolved relative to *base*
    (or the current working directory if *base* is ``None``).

    Args:
        path_str: A filesystem path as a string.
        base: An optional base directory for relative resolution.

    Returns:
        The resolved absolute path.
    """
    path = Path(path_str)
    if not path.is_absolute():
        path = base / path if base is not None else Path.cwd() / path
    return path.resolve()


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """Read and return the text content of *path*.

    Args:
        path: The file to read.
        encoding: File encoding (default ``utf-8``).

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If *path* does not exist.
        IsADirectoryError: If *path* is a directory.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding=encoding)


def write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write *content* to *path*, creating parent directories as needed.

    Args:
        path: The file to write.
        content: The text content to write.
        encoding: File encoding (default ``utf-8``).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)
