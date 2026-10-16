"""Unit tests for lib.resolve_script_root.core."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.resolve_script_root.core import resolve_script_root

pytestmark = pytest.mark.unit


def test_env_var_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """OPENCODE_SCRIPTS_PYTHON env var returns that path with env-var source."""
    monkeypatch.setenv("OPENCODE_SCRIPTS_PYTHON", "/custom/scripts/python")
    path, source = resolve_script_root(runtime="python")
    assert source == "env-var"
    assert str(path) == "/custom/scripts/python"


def test_env_var_node(monkeypatch: pytest.MonkeyPatch) -> None:
    """OPENCODE_SCRIPTS_NODE env var returns that path with env-var source."""
    monkeypatch.setenv("OPENCODE_SCRIPTS_NODE", "/custom/node")
    path, source = resolve_script_root(runtime="node")
    assert source == "env-var"
    assert str(path) == "/custom/node"


def test_env_var_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    """OPENCODE_SCRIPTS_SHELL env var returns that path with env-var source."""
    monkeypatch.setenv("OPENCODE_SCRIPTS_SHELL", "/custom/shell")
    path, source = resolve_script_root(runtime="shell")
    assert source == "env-var"
    assert str(path) == "/custom/shell"


def test_project_local_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When env var is unset and project-local dir exists, returns that path."""
    monkeypatch.delenv("OPENCODE_SCRIPTS_PYTHON", raising=False)
    project_local = tmp_path / "opencode" / "scripts" / "python"
    project_local.mkdir(parents=True)

    path, source = resolve_script_root(
        runtime="python",
        project_root=tmp_path,
    )
    assert source == "project-local"
    assert path == project_local.resolve()


def test_global_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When env var and project-local are absent, falls through to global."""
    monkeypatch.delenv("OPENCODE_SCRIPTS_PYTHON", raising=False)
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    # A legacy hidden path does not satisfy the explicit Python project root.
    legacy_project_local = tmp_path / ".opencode" / "scripts" / "python"
    legacy_project_local.mkdir(parents=True)

    path, source = resolve_script_root(
        runtime="python",
        project_root=tmp_path,
    )
    assert source == "global"
    assert (
        path == (home / ".config" / "opencode" / "scripts" / "python").resolve()
    )


def test_runtime_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--runtime node selects the node subdirectory for project-local."""
    monkeypatch.delenv("OPENCODE_SCRIPTS_NODE", raising=False)
    project_local_node = tmp_path / ".opencode" / "scripts" / "node"
    project_local_node.mkdir(parents=True)

    path, source = resolve_script_root(
        runtime="node",
        project_root=tmp_path,
    )
    assert source == "project-local"
    assert path == project_local_node.resolve()


def test_shell_project_root_remains_hidden(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Shell project-local resolution keeps the existing hidden root."""
    monkeypatch.delenv("OPENCODE_SCRIPTS_SHELL", raising=False)
    project_local_shell = tmp_path / ".opencode" / "scripts" / "shell"
    project_local_shell.mkdir(parents=True)

    path, source = resolve_script_root(
        runtime="shell",
        project_root=tmp_path,
    )
    assert source == "project-local"
    assert path == project_local_shell.resolve()


def test_runtime_selection_global(monkeypatch: pytest.MonkeyPatch) -> None:
    """--runtime shell falls through to global correctly."""
    monkeypatch.delenv("OPENCODE_SCRIPTS_SHELL", raising=False)

    path, source = resolve_script_root(runtime="shell")
    assert source == "global"
    assert str(path).endswith("/.config/opencode/scripts/shell")


def test_project_root_option_changes_search_base(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit --project-root changes where project-local is checked."""
    monkeypatch.delenv("OPENCODE_SCRIPTS_PYTHON", raising=False)
    # Create a project-local dir under a different base, not under tmp_path
    other_base = tmp_path / "other-project"
    other_base.mkdir()
    project_local = other_base / "opencode" / "scripts" / "python"
    project_local.mkdir(parents=True)

    path, source = resolve_script_root(
        runtime="python",
        project_root=other_base,
    )
    assert source == "project-local"
    assert path == project_local.resolve()

    # Without the explicit base, tmp_path has no opencode/scripts/python.
    path2, source2 = resolve_script_root(
        runtime="python",
        project_root=tmp_path,
    )
    assert source2 == "global"
