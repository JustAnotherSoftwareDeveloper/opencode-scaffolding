"""test_collect_skills_cli.py — Tests for the collect-skills Click CLI.

Covers the Click CLI command (via CliRunner).

Run from ``scripts/python/``:

    uv run pytest tests/test_collect_skills_cli.py -v
"""

from __future__ import annotations

from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from cli.collect_skills import main


# ============================================================================
# Test Click CLI via CliRunner
# ============================================================================


class TestCli:
    """Tests for the Click CLI command via CliRunner."""

    def test_default_invocation(self) -> None:
        """Running with no arguments succeeds (empty pass-through)."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        # The CLI is a pass-through (body is empty);
        # currently it just returns None (exit 0).
        assert result.exit_code == 0

    def test_with_project_root(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--project-root", "/tmp"])
        assert result.exit_code == 0

    def test_with_extra_paths(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--extra-paths", "/tmp/a", "--extra-paths", "/tmp/b"])
        assert result.exit_code == 0

    def test_with_include_archive(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--include-archive"])
        assert result.exit_code == 0

    def test_with_all_options(self, tmp_path: Path) -> None:
        manifest = tmp_path / "manifest.json"
        manifest.write_text("[]")
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--project-root", str(tmp_path / "proj"),
                "--config-dir", str(tmp_path / "config"),
                "--extra-paths", str(tmp_path / "extra1"),
                "--include-archive",
                "--builtins-manifest", str(manifest),
                "--verbose",
                "--output", str(tmp_path / "out.json"),
            ],
        )
        assert result.exit_code == 0

    def test_help_text(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "collect-skills" in result.output
        assert "project-root" in result.output
        assert "config-dir" in result.output
        assert "extra-paths" in result.output
        assert "include-archive" in result.output
        assert "builtins-manifest" in result.output
        assert "verbose" in result.output
        assert "output" in result.output