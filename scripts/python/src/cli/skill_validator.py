#!/usr/bin/env python3
"""Validate a generated skill directory against skill-writer rules.

Usage:
    uv run --directory ~/.config/opencode/scripts/python python -m src.cli.skill_validator <path/to/skill/dir>

Returns structured JSON and exits 0 if all checks pass, 1 if any fail.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Set up path for sibling imports (same pattern as collect_skills.py)
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CLASSES = frozenset({
    "operation",
    "delegated",
    "inline",
    "orchestrated",
    "planning",
    "documentation",
})

PLANNING_DESCRIPTION_PREFIX = "Use as planning reference"
DEFAULT_DESCRIPTION_PREFIX = "Use when"

PASSIVE_VOICE_PATTERNS = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+\w+ed\b"
    r"|\bshould\b"
    r"|\bmay\b"
    r"|\bcould\b"
    r"|\bmight\b"
    r"|\b(must\s+be\s+\w+ed)\b"
    r"|\b(is\s+used)\b"
    r"|\b(will\s+be)\b",
    re.IGNORECASE,
)

PLACEHOLDER_PATTERN = re.compile(r"<<[^>]+>>")

RELATIVE_LINK_PATTERN = re.compile(r"\]\(\./.*?\.md(?:\#.*?)?\)")

SENTENCE_END_PATTERN = re.compile(r"[.!?][\s'\u2019\u201d]")


def _is_in_skip_directory(file_path: Path, skill_dir: Path, dirs: frozenset[str]) -> bool:
    """Check if a file resides within one of the given subdirectories of skill_dir."""
    try:
        rel = file_path.relative_to(skill_dir)
    except ValueError:
        return False
    return len(rel.parts) > 1 and rel.parts[0] in dirs


# ---------------------------------------------------------------------------
# Check result type
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """Result of a single validation check."""

    name: str
    passed: bool
    detail: str


# ---------------------------------------------------------------------------
# Helper: read SKILL.md
# ---------------------------------------------------------------------------


def _read_skill_md(skill_dir: Path) -> str | None:
    """Return the content of SKILL.md, or None if missing."""
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Parse YAML frontmatter from SKILL.md content.

    Returns the parsed dict or None on failure.
    """
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None
    try:
        return dict(yaml.safe_load(m.group(1)) or {})
    except yaml.YAMLError:
        return None


# ---------------------------------------------------------------------------
# Individual checks (1-11)
# ---------------------------------------------------------------------------


def check_frontmatter_valid(skill_dir: Path) -> CheckResult:
    """Check 1: Frontmatter YAML is valid and contains exactly name, description, class."""
    content = _read_skill_md(skill_dir)
    if content is None:
        return CheckResult("frontmatter-valid", False, "SKILL.md not found")

    fm = _parse_frontmatter(content)
    if fm is None:
        return CheckResult(
            "frontmatter-valid", False, "Frontmatter YAML is missing or invalid"
        )

    expected_keys = {"name", "description", "class"}
    actual_keys = set(fm.keys())
    if actual_keys != expected_keys:
        extra = actual_keys - expected_keys
        missing = expected_keys - actual_keys
        parts = []
        if extra:
            parts.append(f"unexpected keys: {', '.join(sorted(extra))}")
        if missing:
            parts.append(f"missing keys: {', '.join(sorted(missing))}")
        return CheckResult(
            "frontmatter-valid", False, "; ".join(parts)
        )

    # Verify each value is non-empty string
    for key in expected_keys:
        val = fm.get(key)
        if not isinstance(val, str) or not val.strip():
            return CheckResult(
                "frontmatter-valid",
                False,
                f"Field '{key}' is missing or empty",
            )

    return CheckResult("frontmatter-valid", True, "Valid frontmatter with name, description, class")


def check_name_matches_dir(skill_dir: Path) -> CheckResult:
    """Check 2: name matches the parent directory name."""
    content = _read_skill_md(skill_dir)
    if content is None:
        return CheckResult("name-matches-dir", False, "SKILL.md not found")

    fm = _parse_frontmatter(content)
    if fm is None:
        return CheckResult("name-matches-dir", False, "Cannot check name: frontmatter invalid")

    skill_name = fm.get("name", "")
    dir_name = skill_dir.name

    if skill_name == dir_name:
        return CheckResult("name-matches-dir", True, f"name '{skill_name}' matches directory '{dir_name}'")
    return CheckResult(
        "name-matches-dir",
        False,
        f"name '{skill_name}' does not match directory '{dir_name}'",
    )


def check_description_prefix(skill_dir: Path) -> CheckResult:
    """Check 3: description starts with 'Use when' (or 'Use as planning reference' for planning)."""
    content = _read_skill_md(skill_dir)
    if content is None:
        return CheckResult("description-prefix", False, "SKILL.md not found")

    fm = _parse_frontmatter(content)
    if fm is None:
        return CheckResult("description-prefix", False, "Cannot check description: frontmatter invalid")

    desc = fm.get("description", "")
    skill_class = fm.get("class", "")

    if skill_class == "planning":
        if desc.startswith(PLANNING_DESCRIPTION_PREFIX):
            return CheckResult(
                "description-prefix",
                True,
                f"Description starts with '{PLANNING_DESCRIPTION_PREFIX}' as required for planning class",
            )
        return CheckResult(
            "description-prefix",
            False,
            f"Planning skill description must start with '{PLANNING_DESCRIPTION_PREFIX}', got: '{desc[:80]}...'",
        )

    if desc.startswith(DEFAULT_DESCRIPTION_PREFIX):
        return CheckResult(
            "description-prefix",
            True,
            f"Description starts with '{DEFAULT_DESCRIPTION_PREFIX}'",
        )
    return CheckResult(
        "description-prefix",
        False,
        f"Description must start with '{DEFAULT_DESCRIPTION_PREFIX}', got: '{desc[:80]}...'",
    )


def check_class_valid(skill_dir: Path) -> CheckResult:
    """Check 4: class is one of the six valid values."""
    content = _read_skill_md(skill_dir)
    if content is None:
        return CheckResult("class-valid", False, "SKILL.md not found")

    fm = _parse_frontmatter(content)
    if fm is None:
        return CheckResult("class-valid", False, "Cannot check class: frontmatter invalid")

    skill_class = fm.get("class", "")
    if skill_class in VALID_CLASSES:
        return CheckResult("class-valid", True, f"Class '{skill_class}' is valid")
    valid_list = ", ".join(sorted(VALID_CLASSES))
    return CheckResult(
        "class-valid",
        False,
        f"Class '{skill_class}' is not valid. Must be one of: {valid_list}",
    )


def check_docs_last_section(skill_dir: Path) -> CheckResult:
    """Check 5: SKILL.md has a '## Docs' section as the last section."""
    content = _read_skill_md(skill_dir)
    if content is None:
        return CheckResult("docs-last-section", False, "SKILL.md not found")

    # Find all H2 section headings (## ...)
    headings = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    if not headings:
        return CheckResult("docs-last-section", False, "No H2 sections found in SKILL.md")

    last_heading = headings[-1].strip()
    if last_heading == "Docs":
        return CheckResult("docs-last-section", True, "Last H2 section is '## Docs'")
    return CheckResult(
        "docs-last-section",
        False,
        f"Last H2 section is '## {last_heading}', expected '## Docs'",
    )


def check_reference_readme_exists(skill_dir: Path) -> CheckResult:
    """Check 6: reference/README.md exists."""
    path = skill_dir / "reference" / "README.md"
    if path.is_file():
        return CheckResult("reference-readme-exists", True, "reference/README.md exists")
    return CheckResult("reference-readme-exists", False, "reference/README.md not found")


def check_no_examples_section(skill_dir: Path) -> CheckResult:
    """Check 7: No examples section present in SKILL.md."""
    content = _read_skill_md(skill_dir)
    if content is None:
        return CheckResult("no-examples-section", False, "SKILL.md not found")

    if re.search(r"^##\s+Examples\b", content, re.MULTILINE):
        return CheckResult("no-examples-section", False, "SKILL.md contains an '## Examples' section")
    return CheckResult("no-examples-section", True, "No examples section found")


def check_one_sentence_per_line(skill_dir: Path) -> CheckResult:
    """Check 8: Body sentences each start on a new line (one sentence per line) in .md files."""
    violations: list[str] = []
    md_files = list(skill_dir.rglob("*.md"))

    if not md_files:
        return CheckResult("one-sentence-per-line", False, "No .md files found in skill directory")

    for md_file in md_files:
        # Skip files in schemas/ and templates/ per style guide exceptions.
        # Also skip reference/ — these are documentation with looser conventions.
        if _is_in_skip_directory(md_file, skill_dir, frozenset({"schemas", "templates", "reference"})):
            continue

        text = md_file.read_text(encoding="utf-8")
        lines = text.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip YAML frontmatter lines, headings, empty lines, list items, code fences
            if not stripped:
                continue
            if stripped.startswith("---"):
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith("- "):
                continue
            if stripped.startswith("* "):
                continue
            if stripped.startswith("1.") or stripped.startswith("2."):
                continue
            if stripped.startswith("```"):
                continue
            if stripped.startswith(">"):
                continue
            # Check for multiple sentences on one line in prose paragraphs
            # A line with more than one sentence-ending punctuation followed by space indicates
            # multiple sentences joined
            matches = list(SENTENCE_END_PATTERN.finditer(stripped))
            if len(matches) > 1:
                violations.append(f"{md_file.name}:{i}: multiple sentences on one line")

    if violations:
        # Show first 5 violations
        detail_lines = violations[:5]
        if len(violations) > 5:
            detail_lines.append(f"... and {len(violations) - 5} more")
        return CheckResult("one-sentence-per-line", False, "; ".join(detail_lines))
    return CheckResult("one-sentence-per-line", True, "All .md files use one sentence per line")


def check_no_declarative_voice(skill_dir: Path) -> CheckResult:
    """Check 9: No procedural sentence uses declarative voice."""
    violations: list[str] = []
    md_files = list(skill_dir.rglob("*.md"))

    if not md_files:
        return CheckResult("no-declarative-voice", False, "No .md files found")

    for md_file in md_files:
        # Skip schemas/, templates/, and reference/ per style guide exceptions
        # reference/*.md has explicit exception for declarative voice in fact definitions
        if _is_in_skip_directory(md_file, skill_dir, frozenset({"schemas", "templates", "reference"})):
            continue

        text = md_file.read_text(encoding="utf-8")
        lines = text.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip headings, empty, code fences, list markers, frontmatter
            if not stripped or stripped.startswith(("#", "- ", "* ", "```", "---", ">")):
                continue
            if re.match(r"^\d+\.", stripped):
                continue

            # Heuristic: check for passive voice patterns or hedging in prose lines
            # Only flag in body text that looks like a procedural instruction
            if PASSIVE_VOICE_PATTERNS.search(stripped):
                violations.append(f"{md_file.name}:{i}: '{stripped[:80]}'")

    if violations:
        detail_lines = violations[:5]
        if len(violations) > 5:
            detail_lines.append(f"... and {len(violations) - 5} more")
        return CheckResult("no-declarative-voice", False, "; ".join(detail_lines))
    return CheckResult("no-declarative-voice", True, "No declarative voice or passive constructions detected")


def check_no_placeholders(skill_dir: Path) -> CheckResult:
    """Check 10: No un-replaced <<placeholders>> remain."""
    violations: list[str] = []
    md_files = list(skill_dir.rglob("*.md"))

    if not md_files:
        return CheckResult("no-placeholders", False, "No .md files found")

    for md_file in md_files:
        # Skip templates/ — they intentionally contain <<placeholders>>.
        # Also skip reference/ — contains example code blocks with intentional placeholders.
        if _is_in_skip_directory(md_file, skill_dir, frozenset({"templates", "reference"})):
            continue
        text = md_file.read_text(encoding="utf-8")
        for i, line in enumerate(text.split("\n"), 1):
            if PLACEHOLDER_PATTERN.search(line):
                violations.append(f"{md_file.name}:{i}: '{line.strip()[:60]}'")

    if violations:
        detail_lines = violations[:5]
        if len(violations) > 5:
            detail_lines.append(f"... and {len(violations) - 5} more")
        return CheckResult("no-placeholders", False, "; ".join(detail_lines))
    return CheckResult("no-placeholders", True, "No unreplaced <<placeholders>> found")


def check_cross_references_exist(skill_dir: Path) -> CheckResult:
    """Check 11: All relative cross-references point to existing files within the skill directory."""
    md_files = list(skill_dir.rglob("*.md"))
    broken_refs: list[str] = []

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        # Find all relative markdown links: ](./path/to/file.md)
        for match in RELATIVE_LINK_PATTERN.finditer(text):
            link = match.group(0)
            # Extract path between ]( and )
            path_str = link[2:-1]  # strip "](" and ")"
            # Remove anchor if present
            if "#" in path_str:
                path_str = path_str.split("#")[0]

            # Resolve relative to the skill directory root
            # Links starting with ./ are relative to the skill dir
            ref_path = (skill_dir / path_str).resolve()
            if not ref_path.is_file():
                # Also try relative to the file containing the link
                alt_path = (md_file.parent / path_str).resolve()
                if not alt_path.is_file():
                    broken_refs.append(
                        f"in {md_file.name}: '{link}' -> {ref_path.name} (not found)"
                    )

    if broken_refs:
        detail_lines = broken_refs[:5]
        if len(broken_refs) > 5:
            detail_lines.append(f"... and {len(broken_refs) - 5} more")
        return CheckResult("cross-references-exist", False, "; ".join(detail_lines))
    return CheckResult("cross-references-exist", True, "All relative cross-references resolve to existing files")


# ---------------------------------------------------------------------------
# Check registry
# ---------------------------------------------------------------------------

ALL_CHECKS: list[tuple[str, Any]] = [
    ("frontmatter-valid", check_frontmatter_valid),
    ("name-matches-dir", check_name_matches_dir),
    ("description-prefix", check_description_prefix),
    ("class-valid", check_class_valid),
    ("docs-last-section", check_docs_last_section),
    ("reference-readme-exists", check_reference_readme_exists),
    ("no-examples-section", check_no_examples_section),
    ("one-sentence-per-line", check_one_sentence_per_line),
    ("no-declarative-voice", check_no_declarative_voice),
    ("no-placeholders", check_no_placeholders),
    ("cross-references-exist", check_cross_references_exist),
]

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------


def run_all(skill_dir: Path) -> dict[str, Any]:
    """Run all applicable validation checks and return structured results.

    Returns dict with keys: skill_name, file_count, checks.
    """
    if not skill_dir.is_dir():
        return {
            "skill_name": skill_dir.name,
            "file_count": 0,
            "checks": [
                {
                    "name": "skill-dir-exists",
                    "passed": False,
                    "detail": f"Directory does not exist: {skill_dir}",
                }
            ],
        }

    # Count relevant files
    md_files = sorted(skill_dir.rglob("*.md"))
    file_count = len(md_files)

    results: list[dict[str, str | bool]] = []
    for check_name, check_fn in ALL_CHECKS:
        try:
            result = check_fn(skill_dir)
            results.append({"name": result.name, "passed": result.passed, "detail": result.detail})
        except Exception as exc:
            results.append({"name": check_name, "passed": False, "detail": f"Exception: {exc}"})

    return {
        "skill_name": skill_dir.name,
        "file_count": file_count,
        "checks": results,
    }


def main(args: list[str] | None = None) -> int:
    """CLI entry point. Parses args, runs validation, prints JSON, returns exit code."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate a generated skill directory against skill-writer rules",
    )
    parser.add_argument(
        "skill_path",
        type=Path,
        help="Path to the skill directory to validate",
    )
    parsed = parser.parse_args(args)

    result = run_all(parsed.skill_path)
    print(json.dumps(result, indent=2))

    # Exit 0 if all checks pass, 1 if any fail
    if all(check.get("passed", False) for check in result["checks"]):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
