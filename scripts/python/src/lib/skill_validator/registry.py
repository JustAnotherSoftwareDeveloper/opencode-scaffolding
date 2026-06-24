"""Check registry and orchestrator for skill validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .checks import (
    CheckResult,
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
)

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