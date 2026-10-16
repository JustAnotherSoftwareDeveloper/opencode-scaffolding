"""CLI integration tests for resolve-script-root."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.resolve_script_root import main

pytestmark = pytest.mark.integration


class TestResolveScriptRootCLI:
    """Integration tests for the resolve-script-root CLI."""

    runner = CliRunner()

    def test_env_var_python(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--runtime python with env var set returns env var path."""
        monkeypatch.setenv("OPENCODE_SCRIPTS_PYTHON", "/custom/scripts/python")
        result = self.runner.invoke(main, ["--runtime", "python"])
        assert result.exit_code == 0
        assert result.output.strip() == "/custom/scripts/python"

    def test_project_root_fallback_text(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Legacy hidden Python path falls through to the exact global root."""
        monkeypatch.delenv("OPENCODE_SCRIPTS_PYTHON", raising=False)
        home = tmp_path / "home"
        monkeypatch.setenv("HOME", str(home))
        legacy_project_local = tmp_path / ".opencode" / "scripts" / "python"
        legacy_project_local.mkdir(parents=True)
        result = self.runner.invoke(
            main, ["--runtime", "python", "--project-root", str(tmp_path)]
        )
        assert result.exit_code == 0
        expected = home / ".config" / "opencode" / "scripts" / "python"
        assert result.output.strip() == str(expected.resolve())

    def test_json_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--format json returns JSON with path, runtime, and source."""
        monkeypatch.setenv("OPENCODE_SCRIPTS_PYTHON", "/override/path")
        result = self.runner.invoke(
            main, ["--runtime", "python", "--format", "json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["path"] == "/override/path"
        assert data["runtime"] == "python"
        assert data["source"] == "env-var"

    def test_json_format_project_local(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--format json with project-local resolution."""
        monkeypatch.delenv("OPENCODE_SCRIPTS_PYTHON", raising=False)
        project_local = tmp_path / "opencode" / "scripts" / "python"
        project_local.mkdir(parents=True)
        result = self.runner.invoke(
            main,
            [
                "--runtime",
                "python",
                "--project-root",
                str(tmp_path),
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["path"] == str(project_local.resolve())
        assert data["runtime"] == "python"
        assert data["source"] == "project-local"

    def test_help(self) -> None:
        """--help exits 0 and shows usage."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "--runtime" in result.output
        assert "--project-root" in result.output
        assert "--format" in result.output
        assert "./opencode/scripts/python" in result.output
        assert ".opencode/scripts/<runtime>" in result.output
        assert "~/.config/opencode/scripts/python" in result.output
