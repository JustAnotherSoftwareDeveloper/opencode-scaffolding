"""test_collect_skills_main.py — Tests for cli/collect_skills.py main() function.

The main() function is a Click command.  We use CliRunner to invoke it and
monkeypatch ``lib.collect_skills.discovery.discover_all_skills`` to isolate
the discovery layer.

Run from ``scripts/python/``:

    uv run pytest tests/test_collect_skills_main.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.collect_skills import main


# ============================================================================
# Test main() function via CliRunner
# ============================================================================


class TestCollectSkillsMain:
    """Tests for the main() entry point in cli/collect_skills.py."""

    def test_main_success_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """main() returns 0 when discovery succeeds with no skills and produces empty JSON array."""
        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills",
            lambda index, **kwargs: None,
        )

        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_main_with_output_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """main() writes JSON to output file when --output is specified."""
        output_path = tmp_path / "skills.json"

        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills",
            lambda index, **kwargs: None,
        )

        runner = CliRunner()
        result = runner.invoke(main, ["--output", str(output_path)])
        assert result.exit_code == 0
        assert output_path.read_text(encoding="utf-8") == "[]"

    def test_main_verbose_with_warnings(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verbose mode prints warnings to stderr."""
        def fake_discover(index, **kwargs):
            from lib.collect_skills.models import Skill

            index.add(Skill(name="test", description="test", source="project"))
            index.add(
                Skill(name="test", description="override", source="global")
            )

        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills", fake_discover
        )

        runner = CliRunner()
        result = runner.invoke(main, ["--verbose"])
        assert result.exit_code == 0
        assert "Warning" in result.stderr
        assert "test" in result.output

    def test_main_discovery_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An exception during discovery returns 1 and prints to stderr."""
        def fake_discover(index, **kwargs):
            raise RuntimeError("Something went wrong")

        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills", fake_discover
        )

        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 1
        assert "Something went wrong" in result.stderr

    def test_main_output_write_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An OSError writing output returns 1 and prints to stderr."""
        output_path = tmp_path / "no-perm" / "skills.json"

        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills",
            lambda index, **kwargs: None,
        )

        runner = CliRunner()
        result = runner.invoke(main, ["--output", str(output_path)])
        assert result.exit_code == 1
        assert "Error writing output" in result.stderr

    def test_main_prints_to_stdout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without --output, JSON is printed to stdout."""
        def fake_discover(index, **kwargs):
            from lib.collect_skills.models import Skill

            index.add(
                Skill(
                    name="alpha",
                    description="test skill",
                    source="project",
                )
            )

        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills", fake_discover
        )

        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "test skill" in result.output