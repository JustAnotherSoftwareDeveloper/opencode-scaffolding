from __future__ import annotations

from pathlib import Path

import pytest

from src.validate_plan import (
    REQUIRED_FILES,
    REJECTED_FILES,
    NAME_RE,
    VALID_STATUSES,
    validate_index_toc,
    validate_metadata_frontmatter,
    validate_plan,
    validate_path_shape,
    validate_required_files,
    validate_rejected_files,
    validate_steps_directory,
)


def _create_valid_plan(tmp_path: Path, plan_id: str = "test-plan") -> Path:
    """Create a valid plan workspace for testing."""
    workspace = tmp_path / ".plans" / plan_id
    steps_dir = workspace / "steps"
    steps_dir.mkdir(parents=True)
    
    # Create required files
    (workspace / "INDEX.md").write_text("# Test Plan\n\n## Steps\n\n- [Step 1](steps/01-example.md)\n", encoding="utf-8")
    
    metadata_content = """---
id: test-plan
title: "Test Plan"
status: draft
created_at: "2026-06-05T00:00:00Z"
updated_at: "2026-06-05T00:00:00Z"
proposal: ".proposals/test.md"
---

Plan body here.
"""
    (workspace / "metadata.md").write_text(metadata_content, encoding="utf-8")
    
    (workspace / "source.md").write_text("# Source\n", encoding="utf-8")
    (workspace / "execution-overview.md").write_text("# Execution Overview\n", encoding="utf-8")
    (workspace / "constraints.md").write_text("# Constraints\n", encoding="utf-8")
    (workspace / "file-impact.md").write_text("# File Impact\n", encoding="utf-8")
    (workspace / "implementation-notes.md").write_text("# Implementation Notes\n", encoding="utf-8")
    (workspace / "validation.md").write_text("# Validation\n", encoding="utf-8")
    (workspace / "rollback-recovery.md").write_text("# Rollback Recovery\n", encoding="utf-8")
    (workspace / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
    
    # Create valid step file
    (steps_dir / "01-example.md").write_text("# Step 1\n", encoding="utf-8")
    
    return workspace / "INDEX.md"


def test_validate_path_shape_valid() -> None:
    entry = Path(".plans/test-id/INDEX.md")
    result = validate_path_shape(entry)
    assert result.ok, result.messages
    assert ".plans" in str(result.messages[0]) or "test-id" in str(result.messages[0])


def test_validate_path_shape_wrong_filename() -> None:
    entry = Path(".plans/test-id/WRONG.md")
    result = validate_path_shape(entry)
    assert not result.ok
    assert any("INDEX.md" in message for message in result.messages)


def test_validate_required_files_all_present(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Verify all required files exist (sanity check)
    for f in REQUIRED_FILES:
        assert (workspace_root / f).exists(), f"Required file {f} should exist"


def test_validate_required_files_missing(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Remove a required file
    (workspace_root / "constraints.md").unlink()
    
    result = validate_required_files(workspace_root)
    assert not result.ok
    assert any("constraints.md" in message for message in result.messages)


def test_validate_steps_directory_missing(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Remove steps directory
    import shutil
    shutil.rmtree(workspace_root / "steps")
    
    result = validate_steps_directory(workspace_root)
    assert not result.ok
    assert any("steps/" in message for message in result.messages)


def test_validate_steps_directory_invalid_filename(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Create invalid step file name
    (workspace_root / "steps" / "invalid-name.md").write_text("# Invalid\n", encoding="utf-8")
    
    result = validate_steps_directory(workspace_root)
    assert not result.ok
    assert any("invalid-name.md" in message for message in result.messages or any("XX-description" in m for m in result.messages))


def test_validate_rejected_files_not_present(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Create a rejected file
    (workspace_root / "problem-opportunity.md").write_text("# Problem\n", encoding="utf-8")
    
    result = validate_rejected_files(workspace_root)
    assert not result.ok
    assert any("problem-opportunity.md" in message for message in result.messages)


def test_validate_metadata_frontmatter_valid(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    result = validate_metadata_frontmatter(workspace_root)
    assert result.ok, result.messages


def test_validate_metadata_frontmatter_missing_field(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Remove a required field
    metadata_content = """---
id: test-plan
title: "Test Plan"
status: draft
created_at: "2026-06-05T00:00:00Z"
updated_at: "2026-06-05T00:00:00Z"
---

Plan body.
"""
    (workspace_root / "metadata.md").write_text(metadata_content, encoding="utf-8")
    
    result = validate_metadata_frontmatter(workspace_root)
    assert not result.ok
    assert any("proposal" in message for message in result.messages)


def test_validate_metadata_frontmatter_invalid_status(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Invalid status
    metadata_content = """---
id: test-plan
title: "Test Plan"
status: unknown-status
created_at: "2026-06-05T00:00:00Z"
updated_at: "2026-06-05T00:00:00Z"
proposal: ".proposals/test.md"
---

Plan body.
"""
    (workspace_root / "metadata.md").write_text(metadata_content, encoding="utf-8")
    
    result = validate_metadata_frontmatter(workspace_root)
    assert not result.ok
    assert any("status" in message for message in result.messages)


def test_validate_index_toc_valid(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    result = validate_index_toc(workspace_root)
    assert result.ok, result.messages


def test_validate_index_toc_with_frontmatter_fails(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "test-id")
    workspace_root = plan_file.parent
    
    # Add frontmatter to INDEX.md (invalid for this validator)
    index_content = """---
id: test-plan
title: "Test"
status: draft
created_at: "2026-06-05T00:00:00Z"
updated_at: "2026-06-05T00:00:00Z"
proposal: ".proposals/test.md"
---

# Test Plan
"""
    (workspace_root / "INDEX.md").write_text(index_content, encoding="utf-8")
    
    result = validate_index_toc(workspace_root)
    assert not result.ok
    assert any("frontmatter" in message.lower() for message in result.messages)


def test_validate_plan_valid(tmp_path: Path) -> None:
    plan_file = _create_valid_plan(tmp_path, "1780663143-test")
    
    result = validate_plan(plan_file)
    assert result.ok, "\n".join(result.messages)


def test_name_re_pattern() -> None:
    """Test the step filename pattern."""
    assert NAME_RE.match("01-setup.md") is not None
    assert NAME_RE.match("99-final-step.md") is not None
    assert NAME_RE.match("01-example-with-dashes.md") is not None
    assert NAME_RE.match("invalid-name.md") is None  # No numeric prefix
    assert NAME_RE.match("a1-test.md") is None  # Wrong start