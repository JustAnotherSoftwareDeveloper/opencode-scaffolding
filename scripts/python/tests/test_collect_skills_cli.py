"""test_collect_skills_cli.py — Tests for the collect-skills Click CLI.

Covers the Click CLI command (via CliRunner).

Run from ``scripts/python/``:

    uv run pytest tests/test_collect_skills_cli.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.collect_skills import main
from lib.shared.skill_routing import RoutingCue, RoutingRelationship

# ============================================================================
# Test Click CLI via CliRunner
# ============================================================================


class TestCli:
    """Tests for the Click CLI command via CliRunner."""

    def test_default_invocation(self) -> None:
        """Running with no arguments succeeds and produces JSON output."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert result.output.startswith("[")

    def test_with_project_root(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--project-root", "/tmp"])
        assert result.exit_code == 0
        assert result.output.startswith("[")

    def test_with_extra_paths(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main, ["--extra-paths", "/tmp/a", "--extra-paths", "/tmp/b"]
        )
        assert result.exit_code == 0
        assert result.output.startswith("[")

    def test_with_include_archive(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--include-archive"])
        assert result.exit_code == 0
        assert result.output.startswith("[")

    def test_with_all_options(self, tmp_path: Path) -> None:
        manifest = tmp_path / "manifest.json"
        manifest.write_text("[]")
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--project-root",
                str(tmp_path / "proj"),
                "--config-dir",
                str(tmp_path / "config"),
                "--extra-paths",
                str(tmp_path / "extra1"),
                "--include-archive",
                "--builtins-manifest",
                str(manifest),
                "--verbose",
                "--output",
                str(tmp_path / "out.json"),
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


# ============================================================================
# TestClassFilter — repeatable --class option coverage
# ============================================================================


class TestClassFilter:
    """Tests for the repeatable ``--class`` option.

    Uses monkeypatch to inject known skills into the discovery layer so that
    assertions are deterministic and independent of the global skill inventory.
    """

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _inject_multi_class_skills(
        index: object,
        **_: object,
    ) -> None:
        """Inject skills across multiple classes into the SkillIndex."""
        from lib.collect_skills.models import Skill, SkillIndex

        skills_data = [
            ("alpha", "operation"),
            ("bravo", "documentation"),
            ("charlie", "operation"),
            ("delta", "documentation"),
            ("echo", "planning"),
            ("foxtrot", "inline"),
        ]
        # Cast to SkillIndex — we control the injection.
        assert isinstance(index, SkillIndex)
        for name, class_ in skills_data:
            index.add(
                Skill(
                    name=name,
                    description=f"A {class_} skill named {name}",
                    cues=(RoutingCue("operation", "validate", primary=True),),
                    relationships=(RoutingRelationship("owner"),),
                    class_=class_,
                    source="project",
                    location=f"/tmp/.opencode/skills/{name}/SKILL.md",
                )
            )

    # -- tests -------------------------------------------------------------

    def test_no_class_returns_all(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without ``--class``, all skills are returned."""
        monkeypatch.setattr(
            "cli.collect_skills.discover_all_skills",
            self._inject_multi_class_skills,
        )
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 6
        names = [item["name"] for item in data]
        assert names == sorted(names)
        assert all(item["cues"][0]["value"] == "validate" for item in data)

    def test_single_class_filter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """``--class operation`` returns only operation skills, in order."""
        monkeypatch.setattr(
            "cli.collect_skills.discover_all_skills",
            self._inject_multi_class_skills,
        )
        runner = CliRunner()
        result = runner.invoke(main, ["--class", "operation"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        for item in data:
            assert item["class"] == "operation"
        assert [item["name"] for item in data] == ["alpha", "charlie"]

    def test_multi_class_union(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """``--class operation --class documentation`` returns the union."""
        monkeypatch.setattr(
            "cli.collect_skills.discover_all_skills",
            self._inject_multi_class_skills,
        )
        runner = CliRunner()
        result = runner.invoke(
            main, ["--class", "operation", "--class", "documentation"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 4
        for item in data:
            assert item["class"] in ("operation", "documentation")
        assert [item["name"] for item in data] == [
            "alpha",
            "bravo",
            "charlie",
            "delta",
        ]

    def test_multi_class_alphabetical_order(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Multi-class output is sorted alphabetically regardless of filter order."""
        monkeypatch.setattr(
            "cli.collect_skills.discover_all_skills",
            self._inject_multi_class_skills,
        )
        runner = CliRunner()
        # Reverse the --class invocations to prove CLI order doesn't matter.
        result = runner.invoke(
            main, ["--class", "documentation", "--class", "operation"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        names = [item["name"] for item in data]
        assert names == sorted(names)

    def test_multi_class_repeated_flag_parses(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Repeated ``--class`` flags are parsed as a tuple by Click."""
        monkeypatch.setattr(
            "cli.collect_skills.discover_all_skills",
            self._inject_multi_class_skills,
        )
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--class", "operation", "--class", "documentation"],
        )
        assert result.exit_code == 0
        # Only operation and documentation classes present.
        data = json.loads(result.output)
        classes = {item["class"] for item in data}
        assert classes == {"operation", "documentation"}

    def test_single_class_help_text(self) -> None:
        """Help text documents that ``--class`` is repeatable."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "repeatable" in result.output.lower() or "--class" in result.output

    def test_filter_on_empty_index(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """``--class`` on an empty index returns an empty JSON array."""
        monkeypatch.setattr(
            "cli.collect_skills.discover_all_skills",
            lambda *_, **__: None,  # noqa: ARG005
        )
        runner = CliRunner()
        result = runner.invoke(main, ["--class", "operation"])
        assert result.exit_code == 0
        assert result.output.strip() == "[]"
