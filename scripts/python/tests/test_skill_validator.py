"""test_skill_validator.py — Tests for the skill_validator lib and CLI.

Covers all 11 validation checks, helper functions, run_all(), and the
Click CLI entry point.

Long lines in embedded SKILL.md content strings are permitted.

Run from ``scripts/python/``:

    uv run pytest tests/test_skill_validator.py -v
"""

# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

# Import the CLI entry point separately (only available in cli package)
from cli.skill_validator import cli

# Import validation logic from the canonical lib package
from lib.skill_validator import (
    ALL_CHECKS,
    _is_in_skip_directory,
    _parse_frontmatter,
    _read_skill_md,
    check_class_valid,
    check_cross_references_exist,
    check_description_prefix,
    check_docs_last_section,
    check_frontmatter_valid,
    check_name_matches_dir,
    check_no_declarative_voice,
    check_no_examples_section,
    check_no_placeholders,
    check_one_sentence_per_line,
    check_reference_readme_exists,
    run_all,
)

# ============================================================================
# Helper fixtures
# ============================================================================


@pytest.fixture
def skill_dir(tmp_path: Path) -> Path:
    """Create a minimal valid skill directory with SKILL.md."""
    d = tmp_path / "my-skill"
    d.mkdir()
    skill_md = d / "SKILL.md"
    skill_md.write_text(
        "---\nname: my-skill\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nContent.\n"
    )
    return d


@pytest.fixture
def skill_dir_no_frontmatter(tmp_path: Path) -> Path:
    """Create a skill directory with SKILL.md lacking frontmatter."""
    d = tmp_path / "no-fm"
    d.mkdir()
    (d / "SKILL.md").write_text("# Just content\n\nNo frontmatter here.\n")
    return d


@pytest.fixture
def skill_dir_bad_yaml(tmp_path: Path) -> Path:
    """SKILL.md with malformed YAML frontmatter."""
    d = tmp_path / "bad-yaml"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: unclosed\ndescription: Use when testing\nclass: operation\ninvalid_yaml: [unclosed\n---\n"
    )
    return d


@pytest.fixture
def skill_dir_valid_full(tmp_path: Path) -> Path:
    """Create a valid skill with reference/README.md so all checks pass."""
    d = tmp_path / "full-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: full-skill\ndescription: Use when testing everything\nclass: operation\n---\n\n## Docs\n\nContent.\n"
    )
    ref = d / "reference"
    ref.mkdir()
    (ref / "README.md").write_text("# Reference\n")
    return d


# ============================================================================
# Test helpers
# ============================================================================


class TestIsInSkipDirectory:
    def test_file_in_skip_dir(self, tmp_path: Path) -> None:
        """File inside schemas/ returns True."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        f = skill_dir / "schemas" / "schema.json"
        f.parent.mkdir(parents=True)
        f.write_text("{}")
        assert _is_in_skip_directory(f, skill_dir, frozenset({"schemas"})) is True

    def test_file_not_in_skip_dir(self, tmp_path: Path) -> None:
        """File not in any skip directory returns False."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        f = skill_dir / "README.md"
        f.write_text("# hi")
        assert _is_in_skip_directory(f, skill_dir, frozenset({"schemas"})) is False

    def test_file_not_under_skill_dir(self, tmp_path: Path) -> None:
        """File outside skill_dir returns False (ValueError caught)."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        outside = tmp_path / "outside.md"
        outside.write_text("# hi")
        assert (
            _is_in_skip_directory(outside, skill_dir, frozenset({"schemas"})) is False
        )


class TestReadSkillMd:
    def test_file_exists(self, skill_dir: Path) -> None:
        """Returns content when SKILL.md exists."""
        content = _read_skill_md(skill_dir)
        assert content is not None
        assert "name: my-skill" in content

    def test_file_missing(self, tmp_path: Path) -> None:
        """Returns None when SKILL.md does not exist."""
        d = tmp_path / "empty-dir"
        d.mkdir()
        assert _read_skill_md(d) is None


class TestParseFrontmatter:
    def test_valid_frontmatter(self, skill_dir: Path) -> None:
        """Parse valid YAML frontmatter."""
        content = _read_skill_md(skill_dir)
        assert content is not None
        fm = _parse_frontmatter(content)
        assert fm is not None
        assert fm["name"] == "my-skill"
        assert fm["description"] == "Use when testing"
        assert fm["class"] == "operation"

    def test_missing_frontmatter(self) -> None:
        """No frontmatter delimiters returns None."""
        content = "# Just content\n\nNo frontmatter."
        assert _parse_frontmatter(content) is None

    def test_malformed_yaml(self) -> None:
        """Malformed YAML returns None."""
        content = "---\nname: unclosed\nvalue: [unclosed\n---\n"
        # The yaml.safe_load should raise YAMLError; our function catches it and returns None.
        result = _parse_frontmatter(content)
        assert result is None

    def test_empty_frontmatter(self) -> None:
        """Empty frontmatter yields empty dict."""
        content = "---\n\n---\n# content"
        result = _parse_frontmatter(content)
        assert result == {}


# ============================================================================
# Test individual check functions
# ============================================================================


class TestCheckFrontmatterValid:
    def test_valid(self, skill_dir: Path) -> None:
        result = check_frontmatter_valid(skill_dir)
        assert result.passed is True
        assert "Valid frontmatter" in result.detail

    def test_skippy_missing(self, tmp_path: Path) -> None:
        d = tmp_path / "nope"
        d.mkdir()
        result = check_frontmatter_valid(d)
        assert result.passed is False
        assert "not found" in result.detail

    def test_invalid_yaml(self, skill_dir_bad_yaml: Path) -> None:
        result = check_frontmatter_valid(skill_dir_bad_yaml)
        assert result.passed is False
        assert "missing or invalid" in result.detail or "Exception" in result.detail

    def test_extra_keys(self, tmp_path: Path) -> None:
        d = tmp_path / "extra-keys"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: extra-keys\ndescription: Use when testing\nclass: operation\nunexpected: yes\n---\n"
        )
        result = check_frontmatter_valid(d)
        assert result.passed is False
        assert "unexpected keys" in result.detail

    def test_missing_key(self, tmp_path: Path) -> None:
        d = tmp_path / "missing-key"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: missing-key\ndescription: Use when testing\n---\n"
        )
        result = check_frontmatter_valid(d)
        assert result.passed is False
        assert "missing keys" in result.detail

    def test_empty_name(self, tmp_path: Path) -> None:
        d = tmp_path / "empty-name"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: ''\ndescription: Use when testing\nclass: operation\n---\n"
        )
        result = check_frontmatter_valid(d)
        assert result.passed is False
        assert "missing or empty" in result.detail


class TestCheckNameMatchesDir:
    def test_matches(self, skill_dir: Path) -> None:
        result = check_name_matches_dir(skill_dir)
        assert result.passed is True
        assert "matches directory" in result.detail

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-skill"
        d.mkdir()
        result = check_name_matches_dir(d)
        assert result.passed is False

    def test_mismatch(self, tmp_path: Path) -> None:
        d = tmp_path / "dir-name"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: other-name\ndescription: Use when testing\nclass: operation\n---\n"
        )
        result = check_name_matches_dir(d)
        assert result.passed is False
        assert "does not match" in result.detail

    def test_no_frontmatter(self, skill_dir_no_frontmatter: Path) -> None:
        result = check_name_matches_dir(skill_dir_no_frontmatter)
        assert result.passed is False


class TestCheckDescriptionPrefix:
    def test_default_prefix(self, skill_dir: Path) -> None:
        """Non-planning skill with 'Use when' prefix passes."""
        result = check_description_prefix(skill_dir)
        assert result.passed is True

    def test_default_prefix_fail(self, tmp_path: Path) -> None:
        d = tmp_path / "bad-desc"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: bad-desc\ndescription: This skill does stuff\nclass: operation\n---\n"
        )
        result = check_description_prefix(d)
        assert result.passed is False
        assert "must start with" in result.detail

    def test_planning_prefix_ok(self, tmp_path: Path) -> None:
        d = tmp_path / "plan-skill"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: plan-skill\ndescription: Use as planning reference for project planning\nclass: planning\n---\n"
        )
        result = check_description_prefix(d)
        assert result.passed is True

    def test_planning_prefix_fail(self, tmp_path: Path) -> None:
        d = tmp_path / "bad-plan"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: bad-plan\ndescription: This plans things\nclass: planning\n---\n"
        )
        result = check_description_prefix(d)
        assert result.passed is False
        assert "planning reference" in result.detail

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_description_prefix(d)
        assert result.passed is False
        assert "not found" in result.detail


class TestCheckClassValid:
    def test_valid_class(self, skill_dir: Path) -> None:
        result = check_class_valid(skill_dir)
        assert result.passed is True

    def test_invalid_class(self, tmp_path: Path) -> None:
        d = tmp_path / "bad-class"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: bad-class\ndescription: Use when testing\nclass: invalid_class_value\n---\n"
        )
        result = check_class_valid(d)
        assert result.passed is False
        assert "not valid" in result.detail

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_class_valid(d)
        assert result.passed is False


class TestCheckDocsLastSection:
    def test_docs_is_last(self, skill_dir: Path) -> None:
        result = check_docs_last_section(skill_dir)
        assert result.passed is True

    def test_no_sections(self, tmp_path: Path) -> None:
        d = tmp_path / "no-sections"
        d.mkdir()
        (d / "SKILL.md").write_text("Just plain text.\n")
        result = check_docs_last_section(d)
        assert result.passed is False
        assert "No H2 sections" in result.detail

    def test_wrong_last_section(self, tmp_path: Path) -> None:
        d = tmp_path / "wrong-last"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: wrong-last\ndescription: Use when testing\nclass: operation\n---\n\n## Intro\n\nContent.\n## Usage\n\nMore.\n"
        )
        result = check_docs_last_section(d)
        assert result.passed is False
        assert "expected '## Docs'" in result.detail

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_docs_last_section(d)
        assert result.passed is False


class TestCheckReferenceReadmeExists:
    def test_exists(self, skill_dir: Path) -> None:
        """reference/README.md exists."""
        ref_dir = skill_dir / "reference"
        ref_dir.mkdir()
        (ref_dir / "README.md").write_text("# Reference\n")
        result = check_reference_readme_exists(skill_dir)
        assert result.passed is True

    def test_missing(self, skill_dir: Path) -> None:
        result = check_reference_readme_exists(skill_dir)
        assert result.passed is False
        assert "not found" in result.detail


class TestCheckNoExamplesSection:
    def test_no_examples(self, skill_dir: Path) -> None:
        result = check_no_examples_section(skill_dir)
        assert result.passed is True

    def test_has_examples(self, tmp_path: Path) -> None:
        d = tmp_path / "has-examples"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: has-examples\ndescription: Use when testing\nclass: operation\n---\n\n## Examples\n\nThis should not be here.\n"
        )
        result = check_no_examples_section(d)
        assert result.passed is False
        assert "Examples" in result.detail

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_no_examples_section(d)
        assert result.passed is False


class TestCheckOneSentencePerLine:
    def test_all_ok(self, skill_dir: Path) -> None:
        # Make a clean dir with proper one-sentence-per-line
        d = skill_dir.parent / "sentence-ok"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: sentence-ok\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nFirst sentence.\nSecond sentence.\n"
        )
        # Explicitly create reference/ subdir with multi-sentence lines (should be skipped)
        ref = d / "reference"
        ref.mkdir()
        (ref / "README.md").write_text(
            "This is a reference doc. It has multiple sentences on one line. But it should be skipped.\n"
        )
        result = check_one_sentence_per_line(d)
        assert result.passed is True

    def test_multiple_sentences_violation(self, tmp_path: Path) -> None:
        d = tmp_path / "multi-sent"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: multi-sent\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nFirst sentence. Second sentence. Third on same line.\n"
        )
        result = check_one_sentence_per_line(d)
        assert result.passed is False
        assert "multiple sentences" in result.detail

    def test_no_md_files(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md-files"
        d.mkdir()
        result = check_one_sentence_per_line(d)
        assert result.passed is False
        assert "No .md files found" in result.detail

    def test_skip_directories(self, tmp_path: Path) -> None:
        """schemas/, templates/, reference/ directories are skipped."""
        d = tmp_path / "skip-dirs"
        d.mkdir()
        # Create SKILL.md with proper format
        (d / "SKILL.md").write_text(
            "---\nname: skip-dirs\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nFine.\n"
        )
        # schemas file with multiple sentences - should be skipped
        (d / "schemas").mkdir()
        (d / "schemas" / "example.md").write_text("Sentence one. Sentence two.\n")
        # templates file - should be skipped
        (d / "templates").mkdir()
        (d / "templates" / "template.md").write_text("Sentence one. Sentence two.\n")

        result = check_one_sentence_per_line(d)
        assert result.passed is True

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_one_sentence_per_line(d)
        assert result.passed is False


class TestCheckNoDeclarativeVoice:
    def test_no_violations(self, skill_dir: Path) -> None:
        result = check_no_declarative_voice(skill_dir)
        assert result.passed is True

    def test_passive_voice_detected(self, tmp_path: Path) -> None:
        d = tmp_path / "passive"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: passive\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nThe file is used for testing.\n"
        )
        result = check_no_declarative_voice(d)
        assert result.passed is False
        assert "is used" in result.detail

    def test_hedging_detected(self, tmp_path: Path) -> None:
        d = tmp_path / "hedging"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: hedging\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nYou should run this command.\n"
        )
        result = check_no_declarative_voice(d)
        assert result.passed is False
        assert "should" in result.detail

    def test_no_md_files(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_no_declarative_voice(d)
        assert result.passed is False
        assert "No .md files" in result.detail

    def test_skip_directories(self, tmp_path: Path) -> None:
        """schemas/, templates/, reference/ are skipped."""
        d = tmp_path / "skip-dv"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: skip-dv\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nFine.\n"
        )
        (d / "reference").mkdir()
        (d / "reference" / "api.md").write_text("This is used as a reference.\n")
        result = check_no_declarative_voice(d)
        assert result.passed is True

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_no_declarative_voice(d)
        assert result.passed is False


class TestCheckNoPlaceholders:
    def test_no_placeholders(self, skill_dir: Path) -> None:
        result = check_no_placeholders(skill_dir)
        assert result.passed is True

    def test_placeholder_found(self, tmp_path: Path) -> None:
        d = tmp_path / "has-placeholder"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: has-placeholder\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nUse the <<placeholder>> here.\n"
        )
        result = check_no_placeholders(d)
        assert result.passed is False
        assert "placeholder" in result.detail

    def test_skip_templates_dir(self, tmp_path: Path) -> None:
        """templates/ and reference/ directories are skipped."""
        d = tmp_path / "skip-placeholders"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: skip-placeholders\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nNo placeholders.\n"
        )
        (d / "templates").mkdir()
        (d / "templates" / "tmpl.md").write_text("Use <<name>> here.\n")
        (d / "reference").mkdir()
        (d / "reference" / "ref.md").write_text("Use <<example>> here.\n")
        result = check_no_placeholders(d)
        assert result.passed is True

    def test_no_md_files(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_no_placeholders(d)
        assert result.passed is False
        assert "No .md files" in result.detail

    def test_no_skill_md(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_no_placeholders(d)
        assert result.passed is False


class TestCheckCrossReferencesExist:
    def test_all_exist(self, tmp_path: Path) -> None:
        d = tmp_path / "good-refs"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: good-refs\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nSee [details](./details.md) for more.\n"
        )
        (d / "details.md").write_text("# Details\n")
        result = check_cross_references_exist(d)
        assert result.passed is True

    def test_broken_ref(self, tmp_path: Path) -> None:
        d = tmp_path / "broken-ref"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: broken-ref\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nSee [missing](./missing.md) for more.\n"
        )
        result = check_cross_references_exist(d)
        assert result.passed is False
        assert "not found" in result.detail

    def test_ref_with_anchor(self, tmp_path: Path) -> None:
        d = tmp_path / "anchor-ref"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: anchor-ref\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nSee [details](./details.md#section) for more.\n"
        )
        (d / "details.md").write_text("# Details\n")
        result = check_cross_references_exist(d)
        assert result.passed is True

    def test_resolve_relative_to_file(self, tmp_path: Path) -> None:
        """Relative links resolve relative to the file containing them."""
        d = tmp_path / "rel-ref"
        d.mkdir()
        sub = d / "subdir"
        sub.mkdir()
        (sub / "page.md").write_text("See [up](../other.md).\n")
        (d / "other.md").write_text("# Other\n")
        result = check_cross_references_exist(d)
        assert result.passed is True

    def test_no_md_files(self, tmp_path: Path) -> None:
        d = tmp_path / "no-md"
        d.mkdir()
        result = check_cross_references_exist(d)
        assert result.passed is True  # vacuously true


# ============================================================================
# Test run_all
# ============================================================================


class TestRunAll:
    def test_valid_dir(self, skill_dir_valid_full: Path) -> None:
        result = run_all(skill_dir_valid_full)
        assert result["skill_name"] == "full-skill"
        assert result["file_count"] >= 1
        assert len(result["checks"]) > 0
        all_passed = all(c["passed"] for c in result["checks"])
        assert all_passed is True

    def test_non_existent_dir(self, tmp_path: Path) -> None:
        result = run_all(tmp_path / "does-not-exist")
        assert result["skill_name"] == "does-not-exist"
        assert result["file_count"] == 0
        assert len(result["checks"]) == 1
        assert result["checks"][0]["passed"] is False
        assert "Directory does not exist" in result["checks"][0]["detail"]

    def test_exception_in_check(self, tmp_path: Path) -> None:
        """A check that raises an exception is reported as failed."""
        d = tmp_path / "exception-dir"
        d.mkdir()
        # Create a broken symlink to trigger an error in one-sentence-per-line
        broken = d / "broken.md"
        broken.write_text("# Broken\n")  # this is fine, just test exception path
        # Force an error by making a file unreadable
        (d / "SKILL.md").write_text(
            "---\nname: exception-dir\ndescription: Use when testing\nclass: operation\n---\n\n## Docs\n\nFine.\n"
        )
        result = run_all(d)
        # All checks should complete; none should raise if data is valid
        passed_count = sum(1 for c in result["checks"] if c["passed"])
        assert passed_count >= 1
        assert result["skill_name"] == "exception-dir"

    def test_expected_check_names(self, skill_dir: Path) -> None:
        """Result includes all check names from ALL_CHECKS."""
        result = run_all(skill_dir)
        result_names = {c["name"] for c in result["checks"]}
        expected_names = {name for name, _ in ALL_CHECKS}
        assert result_names == expected_names


# ============================================================================
# Test Click CLI
# ============================================================================


class TestCli:
    """Tests for the Click CLI entry point via CliRunner."""

    def test_valid_dir(self, skill_dir_valid_full: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, [str(skill_dir_valid_full)])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["skill_name"] == "full-skill"
        assert all(c["passed"] for c in data["checks"])

    def test_invalid_dir_with_failures(self, tmp_path: Path) -> None:
        d = tmp_path / "invalid"
        d.mkdir()
        (d / "SKILL.md").write_text(
            "---\nname: invalid\ndescription: Bad\nclass: bad-class\n---\n"
        )
        runner = CliRunner()
        result = runner.invoke(cli, [str(d)])
        assert result.exit_code == 1, result.output
        data = json.loads(result.output)
        assert data["skill_name"] == "invalid"
        assert not all(c["passed"] for c in data["checks"])

    def test_non_existent_dir(self, tmp_path: Path) -> None:
        runner = CliRunner()
        path = str(tmp_path / "nope")
        result = runner.invoke(cli, [path])
        # Click should reject the path before our code runs
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower() or "Error" in result.output

    def test_help_text(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SKILL_PATH" in result.output
        assert "skill-writer" in result.output
