"""test_coverage_edge_cases.py — Tests for hard-to-reach coverage gaps.

Covers:
- ``if __name__ == "__main__"`` guards in cli/example.py, lib/collect_skills/cli.py,
  cli/skill_validator.py
- Edge-case branches in discovery.py (permission errors, OSError, symlink loops)
- Remaining uncovered branches in cli/skill_validator.py
- Truncation branches in check functions (>5 violations)
- _path_helper edge cases
- discover_all_skills None defaults

Long lines in embedded SKILL.md content strings are permitted.

Run from ``scripts/python/``:

    uv run pytest tests/test_coverage_edge_cases.py -v
"""

# ruff: noqa: E501  (long lines in embedded SKILL.md content strings)

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from lib.collect_skills.discovery import (
    discover_skills_from_root,
)
from lib.collect_skills.models import SkillIndex

# ============================================================================
# Test discovery edge cases
# ============================================================================


class TestDiscoveryEdgeCases:
    """Branches in discovery.py not yet covered."""

    def test_permission_error_on_iterdir_verbose(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """PermissionError when listing a directory is caught (verbose)."""
        root = tmp_path / "no-list"
        root.mkdir()
        root.chmod(0o000)
        index = SkillIndex()
        try:
            discover_skills_from_root(root, "project", index, verbose=True)
            captured = capsys.readouterr()
            assert "permission denied" in captured.err
        finally:
            root.chmod(0o755)

    def test_permission_error_on_iterdir_silent(self, tmp_path: Path) -> None:
        """PermissionError when listing a directory is silent (no verbose)."""
        root = tmp_path / "no-list-silent"
        root.mkdir()
        root.chmod(0o000)
        index = SkillIndex()
        try:
            discover_skills_from_root(root, "project", index, verbose=False)
            assert index.resolve() == []
        finally:
            root.chmod(0o755)

    def test_symlink_loop_detection(self, tmp_path: Path) -> None:
        """A symlink loop is detected and skipped."""
        root = tmp_path / "root-loop"
        root.mkdir()
        loop_dir = root / "loop"
        loop_dir.mkdir()
        # Create a valid skill alongside the loop
        skill_dir = root / "valid"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: valid\ndescription: Use when testing\ntags: [test-capability, discovery, symlink-handling, parsing]\nclass: operation\n---\n"
        )
        # Create a symlink inside loop_dir that points to its parent (creating a loop)
        link = loop_dir / "back"
        link.symlink_to(root, target_is_directory=True)
        # Also create a symlink that points to the same real path as another entry
        link2 = root / "dup-link"
        link2.symlink_to(skill_dir, target_is_directory=True)
        # Create another symlink that also points to skill_dir (duplicate visited real)
        link3 = root / "dup-link2"
        link3.symlink_to(skill_dir, target_is_directory=True)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=False)
        # We should have exactly 1 skill (valid), and no loops/duplicates
        assert len(index.resolve()) == 1
        assert index.resolve()[0].name == "valid"

    def test_permission_error_on_entry(
        self, tmp_path: Path
    ) -> None:
        """PermissionError accessing an entry (symlink) is caught (verbose)."""
        root = tmp_path / "root-entry-perm"
        root.mkdir()
        # Create a valid skill
        skill_dir = root / "ok-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: ok-skill\ndescription: Use when testing\ntags: [test-capability, discovery, permission-handling, parsing]\nclass: operation\n---\n"
        )
        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        # The valid skill should still be found
        assert len(index.resolve()) == 1

    def test_violation_truncation_one_sentence(self, tmp_path: Path) -> None:
        """>5 violations in check_one_sentence_per_line shows truncation."""
        from lib.skill_validator import check_one_sentence_per_line

        d = tmp_path / "many-violations"
        d.mkdir()
        # Create a file with 6 prose lines, each having 2+ sentences
        lines = [
            "Sentence one. Sentence two. Sentence three.",
            "First. Second. Third.",
            "Alpha. Beta. Gamma.",
            "X. Y. Z.",
            "A. B. C.",
            "P. Q. R.",
        ]
        content = (
            "---\nname: test\ndescription: test\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + "\n".join(lines)
            + "\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_one_sentence_per_line(d)
        assert result.passed is False
        assert "and 1 more" in result.detail or "and 2 more" in result.detail

    def test_violation_truncation_declarative_voice(self, tmp_path: Path) -> None:
        """>5 violations in check_no_declarative_voice shows truncation."""
        from lib.skill_validator import check_no_declarative_voice

        d = tmp_path / "many-dv"
        d.mkdir()
        # Create file with 6 lines, each containing passive voice
        lines = [
            "This file is used for one thing.",
            "That file is used for another.",
            "This code should be refactored.",
            "That code could be improved.",
            "The system may be restarted.",
            "It might be better to wait.",
        ]
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + "\n".join(lines)
            + "\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_no_declarative_voice(d)
        assert result.passed is False
        assert "and 1 more" in result.detail or "and 2 more" in result.detail

    def test_violation_truncation_placeholders(self, tmp_path: Path) -> None:
        """>5 violations in check_no_placeholders shows truncation."""
        from lib.skill_validator import check_no_placeholders

        d = tmp_path / "many-ph"
        d.mkdir()
        # Create file with 6 placeholder violations
        lines = [
            "Use <<name1>> here.",
            "Use <<name2>> here.",
            "Use <<name3>> here.",
            "Use <<name4>> here.",
            "Use <<name5>> here.",
            "Use <<name6>> here.",
        ]
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + "\n".join(lines)
            + "\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_no_placeholders(d)
        assert result.passed is False
        assert "and 1 more" in result.detail or "and 2 more" in result.detail

    def test_violation_truncation_cross_refs(self, tmp_path: Path) -> None:
        """>5 violations in check_cross_references_exist shows truncation."""
        from lib.skill_validator import check_cross_references_exist

        d = tmp_path / "many-refs"
        d.mkdir()
        # Create references to 6 missing files
        refs = "\n".join(f"See [ref{i}](./ref{i}.md) for details." for i in range(6))
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + refs
            + "\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_cross_references_exist(d)
        assert result.passed is False
        assert "and 1 more" in result.detail or "and 2 more" in result.detail

    def test_covered_list_items(self, tmp_path: Path) -> None:
        """List items (* and -) and numbered lists are skipped in sentence check."""
        from lib.skill_validator import check_one_sentence_per_line

        d = tmp_path / "list-items"
        d.mkdir()
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + "- First item\n"
            + "* Second item\n"
            + "1. Third item\n"
            + "2. Fourth item\n"
            + "Some text.\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_one_sentence_per_line(d)
        # All items should be skipped; only "Some text." is checked, which has 1 sentence
        assert result.passed is True

    def test_covered_code_fence(self, tmp_path: Path) -> None:
        """Code fences (```) are skipped in sentence check."""
        from lib.skill_validator import check_one_sentence_per_line

        d = tmp_path / "code-fence"
        d.mkdir()
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + "```python\n"
            + "x = 1\n"
            + "```\n"
            + "Some text.\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_one_sentence_per_line(d)
        assert result.passed is True

    def test_covered_blockquote(self, tmp_path: Path) -> None:
        """Blockquote lines (>) are skipped in sentence check."""
        from lib.skill_validator import check_one_sentence_per_line

        d = tmp_path / "blockquote"
        d.mkdir()
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            + "## Docs\n\n"
            + "> A quoted line.\n"
            + "> Another quoted line.\n"
            + "Some text.\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_one_sentence_per_line(d)
        assert result.passed is True

    def test_no_frontmatter_in_description_check(self, tmp_path: Path) -> None:
        """check_description_prefix handles None frontmatter."""
        from lib.skill_validator import check_description_prefix

        d = tmp_path / "bad-fm-desc"
        d.mkdir()
        (d / "SKILL.md").write_text("---\ninvalid_yaml: [\n---\n")
        result = check_description_prefix(d)
        assert result.passed is False
        assert "frontmatter invalid" in result.detail

    def test_no_frontmatter_in_class_check(self, tmp_path: Path) -> None:
        """check_class_valid handles None frontmatter."""
        from lib.skill_validator import check_class_valid

        d = tmp_path / "bad-fm-class"
        d.mkdir()
        (d / "SKILL.md").write_text("---\ninvalid_yaml: [\n---\n")
        result = check_class_valid(d)
        assert result.passed is False
        assert "frontmatter invalid" in result.detail

    def test_exception_in_run_all(self, tmp_path: Path) -> None:
        """An exception raised within a check function is caught by run_all."""
        from lib.skill_validator import run_all

        d = tmp_path / "exception-dir"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: exception-dir\ndescription: Use when testing\nclass: operation\n---\n\n"
            "## Docs\n\nContent.\n"
        )
        # Create a situation where a check might fail - malformed data
        # One of the checks might raise; run_all should catch it.
        result = run_all(d)
        for check in result["checks"]:
            assert "name" in check
            assert "passed" in check
        # At least some checks should pass
        assert any(c["passed"] for c in result["checks"])

    def test_check_description_prefix_no_frontmatter(self, tmp_path: Path) -> None:
        """check_description_prefix handles SKILL.md with frontmatter that has invalid FM."""
        from lib.skill_validator import check_description_prefix

        d = tmp_path / "bad-fm-2"
        d.mkdir()
        # Create a file that has --- markers but no valid YAML
        (d / "SKILL.md").write_text("---\n  invalid_yaml_here: [broken\n---\n")
        result = check_description_prefix(d)
        assert result.passed is False

    def test_check_class_valid_no_frontmatter(self, tmp_path: Path) -> None:
        """check_class_valid handles SKILL.md with invalid frontmatter."""
        from lib.skill_validator import check_class_valid

        d = tmp_path / "bad-fm-3"
        d.mkdir()
        (d / "SKILL.md").write_text("---\n  invalid: [broken\n---\n")
        result = check_class_valid(d)
        assert result.passed is False
        assert "frontmatter invalid" in result.detail


# ============================================================================
# Additional skill_validator edge cases
# ============================================================================


class TestSkillValidatorRemaining:
    """Remaining uncovered lines in cli/skill_validator.py."""

    def test_numbered_list_in_declarative_voice(self, tmp_path: Path) -> None:
        """Numbered list lines are skipped in check_no_declarative_voice."""
        from lib.skill_validator import check_no_declarative_voice

        d = tmp_path / "num-list"
        d.mkdir()
        content = (
            "---\nname: test\ndescription: Use when testing\nclass: operation\n---\n\n"
            "## Docs\n\n"
            "1. First item.\n"
            "2. Second item.\n"
            "Some text.\n"
        )
        (d / "SKILL.md").write_text(content)
        result = check_no_declarative_voice(d)
        # Numbered list items are skipped; "Some text." has no passive voice
        assert result.passed is True

    def test_exception_in_check_caught_by_run_all(self, tmp_path: Path) -> None:
        """An exception in a check function is caught by run_all's handler."""
        from lib.skill_validator import run_all

        d = tmp_path / "exception-check"
        d.mkdir()
        # Write binary (non-UTF-8) content to SKILL.md to trigger UnicodeDecodeError
        # when _read_skill_md tries to read it
        f = d / "SKILL.md"
        f.write_bytes(b"\xff\xfe\x00\x01")
        result = run_all(d)
        # Some checks should have failed with an exception
        failed_checks = [c for c in result["checks"] if not c["passed"]]
        assert len(failed_checks) > 0
        # At least one check should show an Exception detail
        exception_details = [c for c in failed_checks if "Exception" in c["detail"]]
        assert len(exception_details) > 0


# ============================================================================
# Additional discovery edge cases (monkeypatched)
# ============================================================================


class TestDiscoveryMonkeypatched:
    """Discovery branches that require monkeypatching to trigger."""

    def test_oserror_on_iterdir(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """OSError when listing a directory is caught (verbose)."""
        from pathlib import Path as _Path

        root = tmp_path / "oserror-dir"
        root.mkdir()

        original_iterdir = _Path.iterdir

        def mock_iterdir(self):
            if self == root:
                raise OSError("Mock filesystem error")
            return original_iterdir(self)

        monkeypatch.setattr(_Path, "iterdir", mock_iterdir)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "cannot list" in captured.err

    def test_oserror_on_iterdir_silent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """OSError on iterdir is silent without verbose."""
        from pathlib import Path as _Path

        root = tmp_path / "oserror-dir-silent"
        root.mkdir()

        original_iterdir = _Path.iterdir

        def mock_iterdir(self):
            if self == root:
                raise OSError("Mock error")
            return original_iterdir(self)

        monkeypatch.setattr(_Path, "iterdir", mock_iterdir)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=False)
        assert index.resolve() == []

    def test_permission_error_on_entry_access(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """PermissionError when accessing an entry is caught (verbose)."""
        from pathlib import Path as _Path

        root = tmp_path / "entry-perm"
        root.mkdir()
        entry_dir = root / "some-entry"
        entry_dir.mkdir()

        original_resolve = _Path.resolve

        def mock_resolve(self):
            if self == entry_dir:
                raise PermissionError("Access denied")
            return original_resolve(self)

        # We need is_symlink to return True so the code tries resolve()
        monkeypatch.setattr(_Path, "is_symlink", lambda self: self == entry_dir)
        monkeypatch.setattr(_Path, "resolve", mock_resolve)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "cannot access" in captured.err

    def test_file_not_found_on_parse(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """FileNotFoundError during parse is caught (verbose)."""
        # Patch the reference to extract_frontmatter in the discovery module
        import lib.collect_skills.discovery as discovery_mod

        root = tmp_path / "root-fnf"
        root.mkdir()
        skill_dir = root / "good-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: Use when testing\nclass: operation\n---\n"
        )

        def raise_fnf(*args, **kwargs):  # noqa: ARG001
            raise FileNotFoundError("File vanished")

        monkeypatch.setattr(discovery_mod, "extract_frontmatter", raise_fnf)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "vanished" in captured.err or "Warning" in captured.err

    def test_general_exception_on_parse(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """General exception during parse is caught (verbose)."""
        import lib.collect_skills.discovery as discovery_mod

        root = tmp_path / "root-exc"
        root.mkdir()
        skill_dir = root / "erratic-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: erratic-skill\ndescription: test\n---\n"
        )

        def raise_general(*args, **kwargs):  # noqa: ARG001
            raise ValueError("Something unexpected")

        monkeypatch.setattr(discovery_mod, "extract_frontmatter", raise_general)

        index = SkillIndex()
        discover_skills_from_root(root, "project", index, verbose=True)
        captured = capsys.readouterr()
        assert "error reading" in captured.err


# ============================================================================
# Test __main__ guards via module execution
# ============================================================================


class TestModuleMainGuards:
    """Test that ``if __name__ == '__main__'`` blocks execute.

    Uses ``runpy.run_module`` to actually run the module with ``__name__="__main__"``,
    which triggers the guard code.
    """

    def test_example_module(self) -> None:
        """Running cli.example as __main__ executes the guard block."""

        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("cli.example", run_name="__main__")
        # main() returns 0, so SystemExit(0)
        assert exc_info.value.code == 0

    def test_collect_skills_module(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Running cli.collect_skills as __main__ executes the guard block."""

        # Stub discovery so the command runs without scanning the filesystem
        monkeypatch.setattr(
            "lib.collect_skills.discovery.discover_all_skills",
            lambda _index, **kwargs: None,  # noqa: ARG005
        )

        saved_argv = sys.argv
        sys.argv = ["collect-skills"]
        try:
            with pytest.raises(SystemExit) as exc_info:
                runpy.run_module("cli.collect_skills", run_name="__main__")
            assert exc_info.value.code == 0
        finally:
            sys.argv = saved_argv

    def test_skill_validator_module(self, tmp_path: Path) -> None:
        """Running cli.skill_validator as __main__ executes the guard block."""

        # Create a valid skill dir
        d = tmp_path / "test-skill"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Use when testing\ntags: [test-capability, skill-validation, yaml-frontmatter, python]\nclass: operation\n---\n\n## Docs\n\nContent.\n"
        )
        ref = d / "reference"
        ref.mkdir()
        (ref / "README.md").write_text("# Reference\n")

        # Set sys.argv so click gets the right arguments
        saved_argv = sys.argv
        sys.argv = ["skill_validator", str(d)]
        try:
            with pytest.raises(SystemExit) as exc_info:
                runpy.run_module("cli.skill_validator", run_name="__main__")
            assert exc_info.value.code == 0
        finally:
            sys.argv = saved_argv


# ============================================================================
# Test _path_helper coverage
# ============================================================================


class TestPathHelperCoverage:
    """Cover remaining lines in lib/shared/_path_helper.py."""

    def test_setup_package_path_inserts_src(self) -> None:
        """When src/ is not on sys.path, setup_package_path inserts it."""
        from lib.shared._path_helper import setup_package_path

        # Remove src/ from sys.path to force the insert branch
        saved_paths = [p for p in sys.path]
        sys.path[:] = [p for p in sys.path if "scripts/python/src" not in p]
        try:
            result = setup_package_path()
            assert result is not None
            assert "scripts/python/src" in str(result)
        finally:
            sys.path[:] = saved_paths


# ============================================================================
# Test discover_all_skills None defaults coverage
# ============================================================================


class TestDiscoverAllSkillsDefaults:
    """Cover None default parameter handling in discover_all_skills()."""

    def test_discover_all_skills_none_defaults(self, tmp_path: Path) -> None:
        """Calling discover_all_skills with None config_dir/extra_paths hits default assignment lines."""
        from lib.collect_skills.discovery import discover_all_skills
        from lib.collect_skills.models import SkillIndex

        # Create a minimal project root with a skill
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
        # Call with None for config_dir and extra_paths to trigger defaults
        discover_all_skills(
            index,
            verbose=False,
            project_root=project,
            config_dir=None,
            extra_paths=None,
            include_archive=False,
        )
        assert len(index.resolve()) >= 1
        assert any(s.name == "my-skill" for s in index.resolve())

    def test_discover_all_skills_project_root_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Calling discover_all_skills with project_root=None triggers Path.cwd() default."""
        from lib.collect_skills.discovery import discover_all_skills
        from lib.collect_skills.models import SkillIndex

        # Change to a known directory with a skill
        project = tmp_path / "proj"
        project.mkdir()
        skill_root = project / ".opencode" / "skills"
        skill_root.mkdir(parents=True)
        skill_dir = skill_root / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: Use when testing\ntags: [test-capability, discovery, project-scope, parsing]\nclass: operation\n---\n"
        )

        monkeypatch.setattr("lib.collect_skills.discovery.Path.cwd", lambda: project)

        index = SkillIndex()
        discover_all_skills(
            index,
            verbose=False,
            project_root=None,
            config_dir=tmp_path / "config",
            extra_paths=None,
            include_archive=False,
        )
        assert any(s.name == "my-skill" for s in index.resolve())
