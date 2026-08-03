"""Focused contract tests for the collect-skills publication boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.collect_skills import main
from lib.collect_skills.discovery import discover_skills_from_root
from lib.collect_skills.models import Skill, SkillIndex


def _populate(index: object, **_: object) -> None:
    assert isinstance(index, SkillIndex)
    index.add(
        Skill(
            name="alpha",
            description="Alpha",
            class_="operation",
            path="/tmp/alpha/SKILL.md",
            source="project",
        )
    )
    index.add(
        Skill(
            name="beta",
            description="Beta",
            class_="documentation",
            path="/tmp/beta/SKILL.md",
            source="project",
        )
    )


class TestCollectSkillsCli:
    def test_stdout_is_json_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("cli.collect_skills.discover_all_skills", _populate)
        result = CliRunner().invoke(main, ["--verbose"])
        assert result.exit_code == 0
        assert result.stderr == ""
        assert [item["name"] for item in json.loads(result.output)] == [
            "alpha",
            "beta",
        ]

    def test_filter_runs_after_discovery_finalization(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[str] = []

        def discover(index: object, **kwargs: object) -> None:
            calls.append("finalize")
            _populate(index, **kwargs)

        monkeypatch.setattr("cli.collect_skills.discover_all_skills", discover)
        result = CliRunner().invoke(main, ["--class", "operation"])
        assert result.exit_code == 0
        assert calls == ["finalize"]
        assert [item["name"] for item in json.loads(result.output)] == ["alpha"]

    def test_failure_has_no_partial_destination(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        destination = tmp_path / "inventory.json"

        def fail(*_: object, **__: object) -> None:
            raise ValueError("bad metadata")

        monkeypatch.setattr("cli.collect_skills.discover_all_skills", fail)
        result = CliRunner().invoke(main, ["--output", str(destination)])
        assert result.exit_code == 1
        assert result.stdout == ""
        assert "Error:" in result.stderr
        assert not destination.exists()

    def test_output_replaces_atomically(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr("cli.collect_skills.discover_all_skills", _populate)
        destination = tmp_path / "inventory.json"
        destination.write_text("old", encoding="utf-8")

        result = CliRunner().invoke(main, ["--output", str(destination)])
        assert result.exit_code == 0
        assert result.stdout == ""
        assert [item["name"] for item in json.loads(destination.read_text())] == [
            "alpha",
            "beta",
        ]
        assert list(tmp_path.glob(".*.tmp")) == []

    def test_builtin_manifest_option_is_removed(self) -> None:
        result = CliRunner().invoke(main, ["--builtins-manifest", "manifest.json"])
        assert result.exit_code != 0
        assert "no such option" in result.output.lower()

    def test_malformed_yaml_is_aggregated_without_stdout(self, tmp_path: Path) -> None:
        skills = tmp_path / "skills"
        skills.mkdir()
        (skills / "broken").mkdir()
        (skills / "broken" / "SKILL.md").write_text(
            "---\nname: [unterminated\n---\n", encoding="utf-8"
        )
        result = CliRunner().invoke(main, ["--extra-paths", str(skills)])
        assert result.exit_code == 1
        assert result.stdout == ""
        assert "discovery" in result.stderr.lower()

    def test_frontmatter_must_start_at_file_beginning(self, tmp_path: Path) -> None:
        root = tmp_path / "skills"
        root.mkdir()
        (root / "broken").mkdir()
        (root / "broken" / "SKILL.md").write_text(
            "comment\n---\nname: broken\n---\n", encoding="utf-8"
        )
        index = SkillIndex()
        discover_skills_from_root(root, "extra", index)
        assert not index.resolve()
