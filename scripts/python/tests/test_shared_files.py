"""Tests for the shared files module."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.shared.files import read_text, resolve_path, write_text


class TestResolvePath:
    """Tests for ``resolve_path()``."""

    def test_absolute_path(self) -> None:
        """An absolute path is returned as-is."""
        result = resolve_path("/usr/bin/python")
        assert result == Path("/usr/bin/python").resolve()

    def test_relative_path(self) -> None:
        """A relative path is resolved against CWD."""
        result = resolve_path("some/relative/path")
        assert result.is_absolute()
        assert str(result).endswith("some/relative/path")

    def test_relative_path_with_base(self) -> None:
        """A relative path is resolved against the given base."""
        base = Path("/tmp")
        result = resolve_path("sub/dir", base=base)
        assert result == (base / "sub/dir").resolve()

    def test_absolute_path_ignores_base(self) -> None:
        """An absolute path ignores the base parameter."""
        base = Path("/tmp")
        result = resolve_path("/etc/passwd", base=base)
        assert result == Path("/etc/passwd").resolve()


class TestReadText:
    """Tests for ``read_text()``."""

    def test_nominal(self, tmp_path: Path) -> None:
        """Read a file with typical content."""
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        assert read_text(f) == "hello world"

    def test_not_found(self) -> None:
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_text(Path("/nonexistent/file.txt"))

    def test_with_encoding(self, tmp_path: Path) -> None:
        """Read a file with a specific encoding."""
        f = tmp_path / "encoded.txt"
        content = "café résumé"
        f.write_text(content, encoding="utf-8")
        assert read_text(f, encoding="utf-8") == content


class TestWriteText:
    """Tests for ``write_text()``."""

    def test_nominal(self, tmp_path: Path) -> None:
        """Write content to a file."""
        f = tmp_path / "out.txt"
        write_text(f, "hello world")
        assert f.read_text() == "hello world"

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Parent directories are created automatically."""
        f = tmp_path / "a" / "b" / "c" / "out.txt"
        write_text(f, "nested content")
        assert f.exists()
        assert f.read_text() == "nested content"

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        """Existing file is overwritten."""
        f = tmp_path / "existing.txt"
        f.write_text("old content")
        write_text(f, "new content")
        assert f.read_text() == "new content"
