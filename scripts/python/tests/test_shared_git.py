"""Tests for the shared git module."""

from __future__ import annotations

from pathlib import Path

from lib.shared.git import find_git_root


class TestFindGitRoot:
    """Tests for ``find_git_root()``."""

    def test_root_found(self, tmp_path: Path) -> None:
        """A ``.git/`` directory is discovered by walking up."""
        (tmp_path / ".git").mkdir()
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        result = find_git_root(nested)
        assert result == tmp_path.resolve()

    def test_root_not_found(self, tmp_path: Path) -> None:
        """Returns ``None`` when no ``.git/`` exists."""
        nested = tmp_path / "x" / "y"
        nested.mkdir(parents=True)
        assert find_git_root(nested) is None

    def test_current_dir_default(self) -> None:
        """When called with no argument, uses CWD and detects real repo."""
        result = find_git_root()
        # This opencode config directory is itself a git repo.
        assert result is not None
        assert (result / ".git").is_dir()

    def test_dot_git_is_file_not_dir(self, tmp_path: Path) -> None:
        """A ``.git`` file (common in submodules) is not detected."""
        nested = tmp_path / "sub"
        nested.mkdir(parents=True)
        (tmp_path / ".git").write_text("gitdir: ../.git/modules/sub\n")
        result = find_git_root(nested)
        assert result is None

    def test_root_path_returned(self, tmp_path: Path) -> None:
        """The returned path is the git root itself, not a parent."""
        (tmp_path / ".git").mkdir()
        result = find_git_root(tmp_path)
        assert result == tmp_path.resolve()

    def test_nested_root_after_non_git_dirs(self, tmp_path: Path) -> None:
        """Walkup proceeds past non-git directories."""
        deep = tmp_path / "level1" / "level2" / "level3"
        deep.mkdir(parents=True)
        (tmp_path / ".git").mkdir()
        result = find_git_root(deep)
        assert result == tmp_path.resolve()
