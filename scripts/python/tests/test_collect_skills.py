"""
test_collect_skills.py — Tests for the collect-skills library.

Covers frontmatter parsing, skill validation, directory traversal,
deduplication, JSON output shape, and CLI argument parsing.

Fixtures are under ``tests/fixtures/``; ephemeral files use ``tmp_path``.

Run from ``scripts/python/``:

    uv run pytest tests/test_collect_skills.py -v
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml

from lib.collect_skills.cli import parse_args
from lib.collect_skills.discovery import (
    _should_exclude_dir,
    discover_skills_from_root,
    find_git_root,
)
from lib.collect_skills.models import Skill, SkillIndex
from lib.collect_skills.parser import extract_frontmatter, validate_skill_frontmatter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Helper: default options object for discovery tests.
_DEFAULT_OPTS = SimpleNamespace(
    verbose=False,
    project_root=Path.cwd(),
    config_dir=Path.home() / ".config" / "opencode",
    extra_paths=[],
    include_archive=False,
)


# ============================================================================
# TestFrontmatterParsing
# ============================================================================


class TestFrontmatterParsing:
    """Tests for ``extract_frontmatter()``."""

    # -- valid ---------------------------------------------------------------

    def test_valid_frontmatter(self) -> None:
        """Parse a valid SKILL.md with frontmatter."""
        path = FIXTURES_DIR / "valid" / "ask-question" / "SKILL.md"
        result = extract_frontmatter(path)
        assert isinstance(result, dict)
        assert result["name"] == "ask-question"
        assert "description" in result

    # -- missing -------------------------------------------------------------

    def test_missing_frontmatter(self) -> None:
        """File with no ``---`` delimiters returns ``None``."""
        path = FIXTURES_DIR / "no-frontmatter" / "readme" / "SKILL.md"
        assert extract_frontmatter(path) is None

    # -- malformed YAML ------------------------------------------------------

    def test_malformed_yaml(self) -> None:
        """Malformed YAML raises ``yaml.YAMLError``."""
        path = FIXTURES_DIR / "malformed-yaml" / "broken" / "SKILL.md"
        with pytest.raises(yaml.YAMLError):
            extract_frontmatter(path)

    # -- missing file --------------------------------------------------------

    def test_missing_file(self) -> None:
        """Non-existent file raises ``FileNotFoundError``."""
        path = FIXTURES_DIR / "does-not-exist" / "SKILL.md"
        with pytest.raises(FileNotFoundError):
            extract_frontmatter(path)

    # -- permission error ----------------------------------------------------

    def test_permission_error(self, tmp_path: Path) -> None:
        """File without read permission raises ``PermissionError``."""
        skill_dir = tmp_path / "no-read"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\nname: test\n---\n")
        # Remove read permission.
        skill_file.chmod(0o000)
        try:
            with pytest.raises(PermissionError):
                extract_frontmatter(skill_file)
        finally:
            # Restore so tmp_path cleanup works.
            skill_file.chmod(0o644)

    # -- empty frontmatter ---------------------------------------------------

    def test_empty_frontmatter(self, tmp_path: Path) -> None:
        """``---\\n---`` returns an empty ``dict``."""
        skill_dir = tmp_path / "empty-fm"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\n---\n# content\n")
        result = extract_frontmatter(skill_file)
        assert result == {}

    # -- non-dict ------------------------------------------------------------

    def test_non_dict_frontmatter(self, tmp_path: Path) -> None:
        """YAML that is not a mapping raises ``ValueError``."""
        skill_dir = tmp_path / "non-dict"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\njust a string\n---\n")
        with pytest.raises(ValueError, match="must be a mapping"):
            extract_frontmatter(skill_file)


# ============================================================================
# TestSkillValidation
# ============================================================================


class TestSkillValidation:
    """Tests for ``validate_skill_frontmatter()``."""

    # -- valid ---------------------------------------------------------------

    def test_valid(self) -> None:
        """A well-formed frontmatter produces no errors."""
        path = FIXTURES_DIR / "valid" / "ask-question" / "SKILL.md"
        fm = extract_frontmatter(path)
        assert fm is not None
        errors = validate_skill_frontmatter(fm, "ask-question", path)
        assert errors == []

    # -- missing name --------------------------------------------------------

    def test_missing_name(self) -> None:
        """Missing ``name`` field is reported."""
        path = FIXTURES_DIR / "missing-name" / "noname" / "SKILL.md"
        fm = extract_frontmatter(path)
        assert fm is not None
        errors = validate_skill_frontmatter(fm, "noname", path)
        assert any("missing 'name'" in e for e in errors)

    # -- missing description -------------------------------------------------

    def test_missing_description(self) -> None:
        """Missing ``description`` field is reported."""
        path = FIXTURES_DIR / "missing-description" / "nodesc" / "SKILL.md"
        fm = extract_frontmatter(path)
        assert fm is not None
        errors = validate_skill_frontmatter(fm, "nodesc", path)
        assert any("missing 'description'" in e for e in errors)

    # -- name mismatch -------------------------------------------------------

    def test_name_mismatch(self) -> None:
        """Name that does not match directory name is reported."""
        path = FIXTURES_DIR / "name-mismatch" / "wrongname" / "SKILL.md"
        fm = extract_frontmatter(path)
        assert fm is not None
        errors = validate_skill_frontmatter(fm, "wrongname", path)
        assert any("must match directory name" in e for e in errors)

    # -- invalid characters --------------------------------------------------

    def test_invalid_chars(self) -> None:
        """Name with invalid characters fails the regex."""
        path = FIXTURES_DIR / "valid" / "ask-question" / "SKILL.md"
        fm: dict[str, Any] = {"name": "Invalid_Name!", "description": "test"}
        errors = validate_skill_frontmatter(fm, "ask-question", path)
        assert any("must match" in e for e in errors)

    # -- full frontmatter ----------------------------------------------------

    def test_full_frontmatter(self) -> None:
        """All optional fields populated passes validation."""
        path = FIXTURES_DIR / "valid-full" / "display-tasks" / "SKILL.md"
        fm = extract_frontmatter(path)
        assert fm is not None
        errors = validate_skill_frontmatter(fm, "display-tasks", path)
        assert errors == []


# ============================================================================
# TestDirectoryTraversal
# ============================================================================


class TestDirectoryTraversal:
    """Tests for ``_should_exclude_dir``, ``find_git_root``,
    ``discover_skills_from_root``."""

    # ------------------------------------------------------------------
    # _should_exclude_dir
    # ------------------------------------------------------------------

    def test_exclude_node_modules(self) -> None:
        assert _should_exclude_dir("node_modules") is True

    def test_exclude_pycache(self) -> None:
        assert _should_exclude_dir("__pycache__") is True

    def test_exclude_dot_dir(self) -> None:
        assert _should_exclude_dir(".hidden") is True

    def test_exclude_underscore_dir(self) -> None:
        assert _should_exclude_dir("_private") is True

    def test_include_normal_dir(self) -> None:
        assert _should_exclude_dir("my-skill") is False

    # ------------------------------------------------------------------
    # find_git_root
    # ------------------------------------------------------------------

    def test_find_git_root_found(self, tmp_path: Path) -> None:
        """A ``.git/`` directory is discovered by walking up."""
        (tmp_path / ".git").mkdir()
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        assert find_git_root(nested) == tmp_path

    def test_find_git_root_not_found(self, tmp_path: Path) -> None:
        """Returns ``None`` when no ``.git/`` exists."""
        nested = tmp_path / "x" / "y"
        nested.mkdir(parents=True)
        assert find_git_root(nested) is None

    # ------------------------------------------------------------------
    # discover_skills_from_root
    # ------------------------------------------------------------------

    def test_single_skill(self) -> None:
        """Discover one valid skill from a root directory."""
        index = SkillIndex()
        root = FIXTURES_DIR / "valid"
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        skills = index.resolve()
        # ``valid/`` has two subdirectories: ask-question, breakdown-tasks
        assert len(skills) == 2

    def test_multiple_skills(self) -> None:
        """Discovering two valid skills produces both in the index."""
        index = SkillIndex()
        root = FIXTURES_DIR / "valid"
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        names = {s.name for s in index.resolve()}
        assert "ask-question" in names
        assert "breakdown-tasks" in names

    def test_empty_root(self, tmp_path: Path) -> None:
        """An empty root directory yields zero skills."""
        empty = tmp_path / "empty-root"
        empty.mkdir()
        index = SkillIndex()
        discover_skills_from_root(empty, "project", index, _DEFAULT_OPTS)
        assert index.resolve() == []

    def test_non_existent_root(self) -> None:
        """A non-existent root is handled gracefully (no skills)."""
        index = SkillIndex()
        root = FIXTURES_DIR / "path" / "does" / "not" / "exist"
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        assert index.resolve() == []

    def test_dot_dir_exclusion(self) -> None:
        """Dot-directories (e.g. ``.hidden``) are excluded from traversal."""
        index = SkillIndex()
        root = FIXTURES_DIR / "dot-dir"
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        # The only entry is ``.hidden/`` which is excluded.
        assert index.resolve() == []

    def test_node_modules_exclusion(self, tmp_path: Path) -> None:
        """``node_modules/`` is excluded from traversal."""
        root = tmp_path / "test-node-modules"
        root.mkdir()
        skill_sub = root / "node_modules" / "some-skill"
        skill_sub.mkdir(parents=True)
        (skill_sub / "SKILL.md").write_text(
            "---\nname: some-skill\ndescription: test\n---\n"
        )
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        assert index.resolve() == []

    def test_nested_dir_exclusion(self) -> None:
        """Nested subdirectories (not immediate children) are excluded."""
        index = SkillIndex()
        root = FIXTURES_DIR / "nested"
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        # ``nested/group/subgroup/SKILL.md`` is not an immediate child of root.
        assert index.resolve() == []

    def test_symlink_to_skill_dir(self, tmp_path: Path) -> None:
        """A symlink pointing to a valid skill directory is discovered."""
        real_skill = tmp_path / "real-skill"
        real_skill.mkdir()
        (real_skill / "SKILL.md").write_text(
            "---\nname: real-skill\ndescription: a real skill\n---\n"
        )

        root = tmp_path / "symlink-root"
        root.mkdir()
        link = root / "linked-skill"
        link.symlink_to(real_skill, target_is_directory=True)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        skills = index.resolve()
        assert len(skills) == 1
        assert skills[0].name == "real-skill"  # uses real dir name

    def test_symlink_loop(self, tmp_path: Path) -> None:
        """A symlink loop does not cause infinite recursion."""
        root = tmp_path / "loop-root"
        root.mkdir()
        loop_dir = root / "loop"
        loop_dir.mkdir()
        # Create a symlink inside loop_dir that points back to itself.
        link = loop_dir / "loop"
        link.symlink_to(loop_dir, target_is_directory=True)

        # Add a valid skill that should be discovered.
        skill_dir = root / "valid-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: valid-skill\ndescription: not in loop\n---\n"
        )

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        # The loop entry is skipped; valid-skill is discovered.
        names = {s.name for s in index.resolve()}
        assert "valid-skill" in names
        assert "loop" not in names

    def test_git_root_ascent(self) -> None:
        """``find_git_root`` discovers the actual git root of this project."""
        repo_root = find_git_root(Path(__file__).resolve())
        assert repo_root is not None
        assert (repo_root / ".git").is_dir()


# ============================================================================
# TestDeduplication
# ============================================================================


class TestDeduplication:
    """Tests for ``SkillIndex`` precedence-based dedup."""

    def test_no_duplicates(self) -> None:
        """Different skill names are both kept."""
        index = SkillIndex()
        index.add(Skill(name="alpha", source="project"))
        index.add(Skill(name="beta", source="project"))
        assert len(index.resolve()) == 2

    def test_same_source_duplicate(self) -> None:
        """Same name and source — first entry kept silently."""
        index = SkillIndex()
        index.add(Skill(name="dup", description="first", source="project"))
        index.add(Skill(name="dup", description="second", source="project"))
        assert len(index.resolve()) == 1
        assert index.resolve()[0].description == "first"
        # Same source → no warning.
        assert index.warnings == []

    def test_project_overrides_global(self) -> None:
        """Project source takes precedence over global."""
        index = SkillIndex()
        index.add(Skill(name="skill-a", description="global version", source="global"))
        index.add(
            Skill(name="skill-a", description="project version", source="project")
        )
        assert len(index.resolve()) == 1
        assert index.resolve()[0].description == "project version"
        assert len(index.warnings) == 1
        assert "Shadowing" in index.warnings[0]
        assert "replaced by" in index.warnings[0]

    def test_builtin_lowest_precedence(self) -> None:
        """Full precedence: project > extra > global > archive > builtin."""
        index = SkillIndex()

        # Add in reverse-priority order to ensure each overrides the previous.
        index.add(Skill(name="tool", description="builtin", source="builtin"))
        index.add(Skill(name="tool", description="archive", source="archive"))
        index.add(Skill(name="tool", description="global", source="global"))
        index.add(Skill(name="tool", description="extra", source="extra"))
        index.add(Skill(name="tool", description="project", source="project"))

        assert len(index.resolve()) == 1
        assert index.resolve()[0].description == "project"
        # Four shadowing warnings (each lower one replaced).
        assert len(index.warnings) == 4

    def test_lower_precedence_shadowed(self) -> None:
        """A lower-precedence skill is shadowed (warning, not replaced)."""
        index = SkillIndex()
        index.add(Skill(name="tool", description="project", source="project"))
        index.add(Skill(name="tool", description="global", source="global"))
        # Project should remain; global is shadowed.
        assert index.resolve()[0].description == "project"
        assert len(index.warnings) == 1
        assert "hidden by" in index.warnings[0]


# ============================================================================
# TestJsonOutput
# ============================================================================


class TestJsonOutput:
    """Tests for JSON serialisation via ``SkillIndex.to_json()``."""

    def test_valid_json_shape(self) -> None:
        """Output is valid JSON and parses as a list."""
        index = SkillIndex()
        index.add(
            Skill(
                name="alpha",
                description="first skill",
                source="project",
                location="/a/b/SKILL.md",
            )
        )
        raw = index.to_json()
        data = json.loads(raw)
        assert isinstance(data, list)

    def test_flat_per_skill_object(self) -> None:
        """Each skill object has no ``frontmatter`` key."""
        index = SkillIndex()
        index.add(
            Skill(
                name="alpha",
                description="test",
                source="project",
                location="/a/b/SKILL.md",
            )
        )
        data = json.loads(index.to_json())
        for item in data:
            assert "frontmatter" not in item
            assert isinstance(item, dict)

    def test_location_overrides_frontmatter(self) -> None:
        """The discovered ``location`` is used even if frontmatter has one."""
        index = SkillIndex()
        # The display-tasks fixture has ``location: /fake/path/...`` in YAML.
        root = FIXTURES_DIR / "valid-full"
        discover_skills_from_root(root, "project", index, _DEFAULT_OPTS)
        data = json.loads(index.to_json())
        assert len(data) == 1
        item = data[0]
        # location must be the real discovered path, not ``/fake/path/...``.
        assert item["location"] != "/fake/path/should-be-overridden"
        assert "display-tasks" in item["location"]

    def test_metadata_fields_correct(self) -> None:
        """All expected fields appear in JSON output."""
        index = SkillIndex()
        index.add(
            Skill(
                name="sample",
                description="a test skill",
                class_="utility",
                version="1.0.0",
                license="MIT",
                compatibility=">=3.12",
                metadata={"key": "val"},
                location="/root/sample/SKILL.md",
                source="project",
                permission="allow",
            )
        )
        data = json.loads(index.to_json())
        item = data[0]
        assert item["name"] == "sample"
        assert item["description"] == "a test skill"
        assert item["class"] == "utility"
        assert item["version"] == "1.0.0"
        assert item["license"] == "MIT"
        assert item["compatibility"] == ">=3.12"
        assert item["metadata"] == {"key": "val"}
        assert item["location"] == "/root/sample/SKILL.md"
        assert item["source"] == "project"
        assert item["permission"] == "allow"

    def test_sorted_by_name(self) -> None:
        """Resolved skills are sorted alphabetically by name."""
        index = SkillIndex()
        for name in ("z-skill", "alpha", "beta", "A-skill"):
            index.add(Skill(name=name, description=f"desc-{name}", source="project"))
        data = json.loads(index.to_json())
        names = [item["name"] for item in data]
        assert names == sorted(names)


# ============================================================================
# TestCli
# ============================================================================


class TestCli:
    """Tests for CLI argument parsing."""

    def test_default_args(self) -> None:
        """Default values are as expected."""
        args = parse_args([])
        assert args.project_root == Path.cwd()
        assert args.config_dir == Path.home() / ".config" / "opencode"
        assert args.extra_paths == []
        assert args.include_archive is False
        assert args.builtins_manifest is None
        assert args.verbose is False
        assert args.output is None

    def test_custom_project_root(self) -> None:
        """``--project-root`` sets the project root."""
        args = parse_args(["--project-root", "/tmp/myproject"])
        assert args.project_root == Path("/tmp/myproject")

    def test_custom_config_dir(self) -> None:
        """``--config-dir`` sets the config directory."""
        args = parse_args(["--config-dir", "/custom/config"])
        assert args.config_dir == Path("/custom/config")

    def test_extra_paths(self) -> None:
        """``--extra-paths`` accepts multiple directories."""
        args = parse_args(["--extra-paths", "/path/a", "/path/b", "/path/c"])
        assert args.extra_paths == [
            Path("/path/a"),
            Path("/path/b"),
            Path("/path/c"),
        ]

    def test_include_archive_flag(self) -> None:
        """``--include-archive`` flag sets True."""
        args = parse_args(["--include-archive"])
        assert args.include_archive is True

    def test_verbose_flag(self) -> None:
        """``--verbose`` / ``-v`` sets verbose."""
        args = parse_args(["--verbose"])
        assert args.verbose is True
        args2 = parse_args(["-v"])
        assert args2.verbose is True

    def test_output_flag(self) -> None:
        """``--output`` / ``-o`` sets output path."""
        args = parse_args(["--output", "/tmp/skills.json"])
        assert args.output == Path("/tmp/skills.json")
        args2 = parse_args(["-o", "/tmp/out.json"])
        assert args2.output == Path("/tmp/out.json")
