"""
test_collect_skills.py — Tests for the collect-skills library.

Covers frontmatter parsing, skill validation, directory traversal,
deduplication, JSON output shape, and CLI argument parsing.

Fixtures are under ``tests/fixtures/``; ephemeral files use ``tmp_path``.

Long lines in embedded SKILL.md content strings are permitted.

Run from ``scripts/python/``:

    uv run pytest tests/test_collect_skills.py -v
"""

# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from lib.collect_skills.discovery import (
    _should_exclude_dir,
    discover_all_skills,
    discover_skills_from_root,
    find_git_root,
    get_standard_search_roots,
)
from lib.collect_skills.models import Skill, SkillIndex
from lib.collect_skills.parser import extract_frontmatter, validate_skill_frontmatter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"


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

    # -- tags field validation ------------------------------------------------

    def test_tags_not_a_list(self) -> None:
        """``tags`` field that is not a list is rejected."""
        path = FIXTURES_DIR / "valid" / "ask-question" / "SKILL.md"
        fm: dict[str, Any] = {"name": "test-skill", "description": "Use when testing", "tags": "not-a-list"}
        errors = validate_skill_frontmatter(fm, "test-skill", path)
        assert any("tags" in e and "list" in e for e in errors)

    def test_tags_element_not_string(self) -> None:
        """A tag element that is not a string is rejected."""
        path = FIXTURES_DIR / "valid" / "ask-question" / "SKILL.md"
        fm: dict[str, Any] = {"name": "test-skill", "description": "Use when testing", "tags": [42, "valid-tag", "test-validation", "python"]}
        errors = validate_skill_frontmatter(fm, "test-skill", path)
        assert any("element" in e and "string" in e for e in errors)

    @pytest.mark.parametrize(
        ("tags", "error_fragment"),
        [
            ([], "4–7"),
            (["valid-tag", "test-validation", "python", "Bad Tag"], "kebab-case"),
            (["valid-tag", "test-validation", "python", "helper"], "filler"),
            (["valid-tag", "test-validation", "python", "valid-tag"], "duplicate"),
            (["test-skill", "test-validation", "python", "yaml-frontmatter"], "skill name"),
        ],
    )
    def test_tags_require_descriptive_values(
        self, tags: list[str], error_fragment: str
    ) -> None:
        """Required tags reject empty, malformed, generic, and duplicate values."""
        path = FIXTURES_DIR / "valid" / "ask-question" / "SKILL.md"
        fm: dict[str, Any] = {
            "name": "test-skill",
            "description": "Use when testing",
            "tags": tags,
        }
        errors = validate_skill_frontmatter(fm, "test-skill", path)
        assert any(error_fragment in error for error in errors)


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
        discover_skills_from_root(root, "project", index, verbose=False)
        skills = index.resolve()
        # ``valid/`` has two subdirectories: ask-question, breakdown-tasks
        assert len(skills) == 2

    def test_multiple_skills(self) -> None:
        """Discovering two valid skills produces both in the index."""
        index = SkillIndex()
        root = FIXTURES_DIR / "valid"
        discover_skills_from_root(root, "project", index, verbose=False)
        names = {s.name for s in index.resolve()}
        assert "ask-question" in names
        assert "breakdown-tasks" in names

    def test_empty_root(self, tmp_path: Path) -> None:
        """An empty root directory yields zero skills."""
        empty = tmp_path / "empty-root"
        empty.mkdir()
        index = SkillIndex()
        discover_skills_from_root(empty, "project", index, verbose=False)
        assert index.resolve() == []

    def test_non_existent_root(self) -> None:
        """A non-existent root is handled gracefully (no skills)."""
        index = SkillIndex()
        root = FIXTURES_DIR / "path" / "does" / "not" / "exist"
        discover_skills_from_root(root, "project", index, verbose=False)
        assert index.resolve() == []

    def test_dot_dir_exclusion(self) -> None:
        """Dot-directories (e.g. ``.hidden``) are excluded from traversal."""
        index = SkillIndex()
        root = FIXTURES_DIR / "dot-dir"
        discover_skills_from_root(root, "project", index, verbose=False)
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
        discover_skills_from_root(root, "project", index, verbose=False)
        assert index.resolve() == []

    def test_nested_dir_exclusion(self) -> None:
        """Nested subdirectories (not immediate children) are excluded."""
        index = SkillIndex()
        root = FIXTURES_DIR / "nested"
        discover_skills_from_root(root, "project", index, verbose=False)
        # ``nested/group/subgroup/SKILL.md`` is not an immediate child of root.
        assert index.resolve() == []

    def test_symlink_to_skill_dir(self, tmp_path: Path) -> None:
        """A symlink pointing to a valid skill directory is discovered."""
        real_skill = tmp_path / "real-skill"
        real_skill.mkdir()
        (real_skill / "SKILL.md").write_text(
            "---\nname: real-skill\ndescription: a real skill\ntags: [real-capability, test-discovery, symlink, parsing]\n---\n"
        )

        root = tmp_path / "symlink-root"
        root.mkdir()
        link = root / "linked-skill"
        link.symlink_to(real_skill, target_is_directory=True)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=False)
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
            "---\nname: valid-skill\ndescription: not in loop\ntags: [valid-capability, loop-safety, test-discovery, parsing]\n---\n"
        )

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=False)
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
# TestFilterByClasses
# ============================================================================


class TestFilterByClasses:
    """Tests for ``SkillIndex.filter_by_classes()``."""

    # ------------------------------------------------------------------
    # Repeatable --class union coverage
    # ------------------------------------------------------------------

    def _build_multi_class_index(self) -> SkillIndex:
        """Build a deterministic SkillIndex with skills across multiple classes."""
        index = SkillIndex()
        for name, class_ in [
            ("alpha", "operation"),
            ("bravo", "documentation"),
            ("charlie", "operation"),
            ("delta", "documentation"),
            ("echo", "planning"),
            ("foxtrot", "inline"),
        ]:
            index.add(
                Skill(
                    name=name,
                    description=f"A {class_} skill named {name}",
                    class_=class_,
                    source="project",
                    location=f"/tmp/.opencode/skills/{name}/SKILL.md",
                )
            )
        return index

    def test_empty_filter_returns_empty(self) -> None:
        """An empty tuple of class filters returns an empty list."""
        index = self._build_multi_class_index()
        result = index.filter_by_classes(())
        assert result == []

    def test_single_class_filter(self) -> None:
        """A single class value returns only skills of that class."""
        index = self._build_multi_class_index()
        result = index.filter_by_classes(("operation",))
        assert len(result) == 2
        names = [s.name for s in result]
        assert names == ["alpha", "charlie"]
        for s in result:
            assert s.class_ == "operation"

    def test_multi_class_union(self) -> None:
        """Two class values return the union of both classes."""
        index = self._build_multi_class_index()
        result = index.filter_by_classes(("operation", "documentation"))
        assert len(result) == 4
        names = [s.name for s in result]
        assert names == ["alpha", "bravo", "charlie", "delta"]
        for s in result:
            assert s.class_ in ("operation", "documentation")

    def test_multi_class_no_duplicates(self) -> None:
        """Skills are never duplicated even if a skill matched multiple classes.

        (Each Skill has exactly one class_, so this is structural, but the
        test documents the guarantee.)
        """
        index = self._build_multi_class_index()
        result = index.filter_by_classes(("operation", "documentation"))
        names = [s.name for s in result]
        assert len(names) == len(set(names))  # no duplicates

    def test_multi_class_alphabetical_order(self) -> None:
        """Multi-class output is sorted alphabetically by name."""
        index = self._build_multi_class_index()
        # Add skills out of alphabetical order to prove sorting.
        index.add(
            Skill(
                name="zeta",
                description="A documentation skill",
                class_="documentation",
                source="project",
            )
        )
        index.add(
            Skill(
                name="yankee",
                description="An operation skill",
                class_="operation",
                source="project",
            )
        )
        result = index.filter_by_classes(("documentation", "operation"))
        names = [s.name for s in result]
        assert names == sorted(names)

    def test_filter_preserves_index_content(self) -> None:
        """Filtering does not mutate the underlying index."""
        index = self._build_multi_class_index()
        before_count = len(index.resolve())
        index.filter_by_classes(("operation",))
        after_count = len(index.resolve())
        assert before_count == after_count

    def test_no_match_returns_empty(self) -> None:
        """A class value that matches no skills returns an empty list."""
        index = self._build_multi_class_index()
        result = index.filter_by_classes(("orchestrated",))
        assert result == []

    def test_empty_index_returns_empty(self) -> None:
        """An empty SkillIndex returns an empty list for any filter."""
        index = SkillIndex()
        assert index.filter_by_classes(("operation",)) == []
        assert index.filter_by_classes(()) == []

    def test_multi_class_interleaved_alpha_order(self) -> None:
        """Alphabetical order holds across interleaved class values."""
        index = SkillIndex()
        for name, class_ in [
            ("advance", "operation"),
            ("basic", "documentation"),
            ("core", "operation"),
            ("data", "documentation"),
            ("edge", "operation"),
        ]:
            index.add(
                Skill(
                    name=name,
                    class_=class_,
                    source="project",
                )
            )
        # All five names are in alphabetical order already.
        result = index.filter_by_classes(("operation", "documentation"))
        assert [s.name for s in result] == [
            "advance",
            "basic",
            "core",
            "data",
            "edge",
        ]


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
        discover_skills_from_root(root, "project", index, verbose=False)
        data = json.loads(index.to_json())
        assert len(data) == 1
        item = data[0]
        # location must be the real discovered path, not ``/fake/path/...``.
        assert item["path"] != "/fake/path/should-be-overridden"
        assert "display-tasks" in item["path"]

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
        assert item["path"] == "/root/sample/SKILL.md"
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
# TestParserEdgeCases
# ============================================================================


class TestParserEdgeCases:
    """Tests for uncovered branches in lib/collect_skills/parser.py."""

    def test_opening_dash_dash_no_closing(self, tmp_path: Path) -> None:
        """Opening ``---`` but no closing ``---`` returns ``None``."""
        from lib.collect_skills.parser import extract_frontmatter

        skill_dir = tmp_path / "no-close"
        skill_dir.mkdir()
        f = skill_dir / "SKILL.md"
        f.write_text("---\nname: test\n")
        assert extract_frontmatter(f) is None

    def test_name_non_string(self, tmp_path: Path) -> None:
        """``name`` is not a string is reported."""
        from lib.collect_skills.parser import validate_skill_frontmatter

        f = tmp_path / "SKILL.md"
        f.write_text("---\nname: 42\n---\n")
        errors = validate_skill_frontmatter(
            {"name": 42, "description": "Use when test"}, "test", f
        )
        assert any("non-empty string" in e for e in errors)

    def test_description_non_string(self, tmp_path: Path) -> None:
        """``description`` is not a string is reported."""
        from lib.collect_skills.parser import validate_skill_frontmatter

        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: 123\n---\n")
        errors = validate_skill_frontmatter(
            {"name": "test", "description": 123}, "test", f
        )
        assert any("non-empty string" in e for e in errors)


# ============================================================================
# TestGetStandardSearchRoots
# ============================================================================


class TestGetStandardSearchRoots:
    """Tests for ``get_standard_search_roots()``."""

    def test_no_dirs_exist(self, tmp_path: Path) -> None:
        """When no subdirectories exist, returns empty list."""
        result = get_standard_search_roots(tmp_path / "project", tmp_path / "config")
        assert result == []

    def test_project_dirs_exist(self, tmp_path: Path) -> None:
        """Project subdirs that exist are returned with source 'project'."""
        project = tmp_path / "proj"
        project.mkdir()
        (project / ".opencode" / "skills").mkdir(parents=True)
        result = get_standard_search_roots(project, tmp_path / "config")
        assert len(result) >= 1
        assert any(source == "project" for _, source in result)

    def test_global_dirs_exist(self, tmp_path: Path) -> None:
        """Global subdirs that exist are returned with source 'global'."""
        config = tmp_path / ".config" / "opencode"
        config.mkdir(parents=True)
        (config / "skills").mkdir()
        result = get_standard_search_roots(tmp_path / "proj", config)
        found = [(p, s) for p, s in result if s == "global"]
        assert len(found) >= 1

    def test_all_project_roots(self, tmp_path: Path) -> None:
        """All three project search roots are checked."""
        project = tmp_path / "proj"
        project.mkdir()
        for sub in [".opencode/skills", ".claude/skills", ".agents/skills"]:
            (project / sub).mkdir(parents=True)
        result = get_standard_search_roots(project, tmp_path / "config")
        project_roots = [p for p, s in result if s == "project"]
        assert len(project_roots) == 3

    def test_all_global_roots(self, tmp_path: Path) -> None:
        """All three global search roots are checked."""
        config = tmp_path / ".config" / "opencode"
        config.mkdir(parents=True)
        (config / "skills").mkdir()
        parent = config.parent
        (parent / ".claude" / "skills").mkdir(parents=True)
        (parent / ".agents" / "skills").mkdir(parents=True)
        result = get_standard_search_roots(tmp_path / "proj", config)
        global_roots = [p for p, s in result if s == "global"]
        assert len(global_roots) == 3


# ============================================================================
# TestDiscoverAllSkills
# ============================================================================


class TestDiscoverAllSkills:
    """Tests for ``discover_all_skills()`` orchestrator."""

    def test_with_standard_roots(self, tmp_path: Path) -> None:
        """Standard search roots are scanned for skills."""
        project = tmp_path / "proj"
        project.mkdir()
        skill_root = project / ".opencode" / "skills"
        skill_root.mkdir(parents=True)
        skill_dir = skill_root / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: Use when testing\ntags: [test-capability, discovery, project-scope, parsing]\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=False,
            project_root=project,
            config_dir=tmp_path / "config",
            extra_paths=[],
            include_archive=False,
        )
        assert len(index.resolve()) == 1
        assert index.resolve()[0].name == "my-skill"

    def test_with_extra_paths(self, tmp_path: Path) -> None:
        """Extra paths are scanned with source 'extra'."""
        extra_root = tmp_path / "extra"
        extra_root.mkdir()
        skill_dir = extra_root / "extra-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: extra-skill\ndescription: Use when testing\ntags: [test-capability, discovery, extra-paths, parsing]\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=False,
            project_root=tmp_path / "proj",
            config_dir=tmp_path / "config",
            extra_paths=[extra_root],
            include_archive=False,
        )
        names = {s.name for s in index.resolve()}
        assert "extra-skill" in names

    def test_with_archive_paths(self, tmp_path: Path) -> None:
        """Archive paths are scanned when include_archive is True."""
        project = tmp_path / "proj"
        project.mkdir()
        archive_root = project / ".opencode" / "archive" / "skills"
        archive_root.mkdir(parents=True)
        skill_dir = archive_root / "archived-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: archived-skill\ndescription: Use when testing\ntags: [test-capability, discovery, archive-paths, parsing]\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=False,
            project_root=project,
            config_dir=tmp_path / "config",
            extra_paths=[],
            include_archive=True,
        )
        names = {s.name for s in index.resolve()}
        assert "archived-skill" in names

    def test_verbose_mode(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verbose mode prints progress messages to stderr."""
        project = tmp_path / "proj-verbose"
        project.mkdir()
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=True,
            project_root=project,
            config_dir=tmp_path / "config",
            extra_paths=[],
            include_archive=False,
        )
        captured = capsys.readouterr()
        # No standard roots exist, so no scanning messages
        # but verbose mode should not crash
        assert captured.err == ""

    def test_verbose_with_standard_roots(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verbose mode prints when standard roots are scanned."""
        project = tmp_path / "proj-verbose2"
        project.mkdir()
        skill_root = project / ".opencode" / "skills"
        skill_root.mkdir(parents=True)
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=True,
            project_root=project,
            config_dir=tmp_path / "config",
            extra_paths=[],
            include_archive=False,
        )
        captured = capsys.readouterr()
        assert "Scanning" in captured.err
        assert "project" in captured.err

    def test_verbose_with_extra_paths(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verbose mode prints when extra paths are scanned."""
        project = tmp_path / "proj-extra-verbose"
        project.mkdir()
        extra = tmp_path / "extra-verbose"
        extra.mkdir()
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=True,
            project_root=project,
            config_dir=tmp_path / "config",
            extra_paths=[extra],
            include_archive=False,
        )
        captured = capsys.readouterr()
        assert "Scanning extra root" in captured.err

    def test_verbose_with_archive(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verbose mode prints when archive paths are scanned."""
        project = tmp_path / "proj-archive-verbose"
        project.mkdir()
        archive_root = project / ".opencode" / "archive" / "skills"
        archive_root.mkdir(parents=True)
        skill_dir = archive_root / "archive-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: archive-skill\ndescription: Use when testing\ntags: [test-capability, discovery, archive-paths, parsing]\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=True,
            project_root=project,
            config_dir=tmp_path / "config",
            extra_paths=[],
            include_archive=True,
        )
        captured = capsys.readouterr()
        assert "Scanning archive root" in captured.err

    def test_extra_path_path_conversion(self, tmp_path: Path) -> None:
        """Extra paths that are already Path objects are not double-converted."""
        extra_root = tmp_path / "extra-path-obj"
        extra_root.mkdir()
        skill_dir = extra_root / "path-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: path-skill\ndescription: Use when testing\ntags: [test-capability, discovery, path-handling, parsing]\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=False,
            project_root=tmp_path / "proj",
            config_dir=tmp_path / "config",
            extra_paths=[extra_root],
            include_archive=False,
        )
        names = {s.name for s in index.resolve()}
        assert "path-skill" in names


# ============================================================================
# TestDiscoverSkillsFromRootEdgeCases
# ============================================================================


class TestDiscoverSkillsFromRootEdgeCases:
    """Edge cases for ``discover_skills_from_root()``."""

    def test_non_existent_root_verbose(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Non-existent root with verbose prints a warning."""
        index = SkillIndex()
        discover_skills_from_root(tmp_path / "nope", "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_non_existent_root_silent(self, tmp_path: Path) -> None:
        """Non-existent root without verbose is silent."""
        index = SkillIndex()
        discover_skills_from_root(tmp_path / "nope", "project", index, verbose=False)
        # Should not crash, no skills added
        assert index.resolve() == []

    def test_non_directory_root_verbose(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A file as root with verbose prints a warning."""
        f = tmp_path / "not-a-dir"
        f.write_text("I am a file")
        index = SkillIndex()
        discover_skills_from_root(f, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "not a directory" in captured.err

    def test_non_directory_root_silent(self, tmp_path: Path) -> None:
        """A file as root without verbose is silent."""
        f = tmp_path / "not-a-dir"
        f.write_text("I am a file")
        index = SkillIndex()
        discover_skills_from_root(f, "project", index, verbose=False)
        assert index.resolve() == []

    def test_permission_error_on_directory(
        self, tmp_path: Path
    ) -> None:
        """PermissionError when listing directory is caught."""
        root = tmp_path / "no-list"
        root.mkdir()
        root.chmod(0o000)
        index = SkillIndex()
        try:
            discover_skills_from_root(root, "project", index, verbose=True)
        finally:
            root.chmod(0o755)

    def test_file_entry_skipped(self, tmp_path: Path) -> None:
        """A file entry in the root is skipped (not a directory or symlink)."""
        root = tmp_path / "root"
        root.mkdir()
        (root / "README.txt").write_text("not a skill")
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=False)
        assert index.resolve() == []

    def test_skill_file_not_a_file(self, tmp_path: Path) -> None:
        """SKILL.md exists but is not a regular file (e.g. directory)."""
        root = tmp_path / "root"
        root.mkdir()
        skill_dir = root / "weird"
        skill_dir.mkdir()
        # Create SKILL.md as a directory instead of a file
        (skill_dir / "SKILL.md").mkdir()
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=False)
        assert index.resolve() == []

    def test_permission_denied_on_file_read(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """PermissionError when reading SKILL.md is caught."""
        root = tmp_path / "root-perm"
        root.mkdir()
        skill_dir = root / "no-read"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\nname: no-read\ndescription: test\n---\n")
        skill_file.chmod(0o000)
        index = SkillIndex()
        try:
            discover_skills_from_root(root, "project", index, verbose=True)
            captured = capsys.readouterr()
            assert "permission denied" in captured.err
        finally:
            skill_file.chmod(0o644)

    def test_broken_symlink(self, tmp_path: Path) -> None:
        """A broken symlink is skipped (not a valid directory)."""
        root = tmp_path / "root-broken"
        root.mkdir()
        broken = root / "broken-link"
        broken.symlink_to(tmp_path / "nonexistent")
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        # Broken symlink is skipped (resolve() finds target, is_dir() is False)
        assert index.resolve() == []

    def test_no_frontmatter_verbose(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """SKILL.md with no frontmatter triggers verbose warning."""
        root = tmp_path / "root-no-fm"
        root.mkdir()
        skill_dir = root / "no-fm"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Just content\n")
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "no frontmatter" in captured.err

    def test_validation_errors_verbose(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Validation errors trigger verbose warnings."""
        root = tmp_path / "root-valid-err"
        root.mkdir()
        skill_dir = root / "bad-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: different-name\ndescription: Use when testing\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "Warning" in captured.err


# ============================================================================
# TestModelEdgeCases
# ============================================================================


class TestModelEdgeCases:
    """Edge cases for models.py."""

    def test_equal_priority_same_location(self) -> None:
        """Equal priority entries keep the existing one silently."""
        index = SkillIndex()
        index.add(
            Skill(
                name="same",
                description="first",
                source="project",
                location="/tmp/.opencode/skills/same",
            )
        )
        index.add(
            Skill(
                name="same",
                description="second",
                source="project",
                location="/tmp/.opencode/skills/same",
            )
        )
        assert len(index.resolve()) == 1
        assert index.resolve()[0].description == "first"
        # No warning for equal priority
        assert index.warnings == []

    def test_to_dict_renames_class(self) -> None:
        """``to_dict()`` renames ``class_`` to ``class``."""
        skill = Skill(name="test", class_="operation")
        d = skill.to_dict()
        assert d["class"] == "operation"
        assert "class_" not in d

    def test_to_dict_excludes_internal(self) -> None:
        """Internal fields like ``_source_priority`` are not in dict."""
        skill = Skill(name="test")
        d = skill.to_dict()
        assert set(d.keys()) == {
            "name",
            "description",
            "tags",
            "class",
            "version",
            "license",
            "compatibility",
            "metadata",
            "path",
            "source",
            "permission",
        }

    def test_warnings_property_returns_copy(self) -> None:
        """``warnings`` property returns a copy, not the internal list."""
        index = SkillIndex()
        index._warnings.append("test warning")
        w = index.warnings
        w.append("mutated")
        assert len(index.warnings) == 1  # original unchanged

    def test_location_priority_different_locations(self) -> None:
        """Different location priorities within same source."""
        index = SkillIndex()
        # .opencode has highest location priority (3)
        index.add(
            Skill(
                name="tool",
                source="project",
                location="/a/.opencode/skills/tool/SKILL.md",
            )
        )
        # .agents has lowest location priority (1)
        index.add(
            Skill(
                name="tool",
                source="project",
                location="/a/.agents/skills/tool/SKILL.md",
            )
        )
        assert len(index.resolve()) == 1
        # The higher location priority (.opencode) should win
        assert ".opencode" in index.resolve()[0].location
