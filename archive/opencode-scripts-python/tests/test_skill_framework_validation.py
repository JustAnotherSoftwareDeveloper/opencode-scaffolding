from __future__ import annotations

from pathlib import Path

from src.validate_skill_framework import (
    CLASSES,
    render_markdown,
    validate_class_schemas,
    validate_skill_file,
)


def _skill(tmp_path: Path, name: str, frontmatter: str, body: str = "# Body\n") -> Path:
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    path = skill_dir / "SKILL.md"
    path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
    return path


def test_valid_skill_with_class(tmp_path: Path) -> None:
    path = _skill(tmp_path, "example-skill", "name: example-skill\ndescription: Use when testing skills.\nclass: operation\n")
    result = validate_skill_file(path, require_class=True)
    assert result.ok, result.messages


def test_invalid_name_fails(tmp_path: Path) -> None:
    path = _skill(tmp_path, "bad-skill", "name: BadSkill\ndescription: Use when testing skills.\nclass: operation\n")
    result = validate_skill_file(path)
    assert not result.ok
    assert any("lowercase" in message for message in result.messages)


def test_missing_description_fails(tmp_path: Path) -> None:
    path = _skill(tmp_path, "example-skill", "name: example-skill\nclass: operation\n")
    result = validate_skill_file(path)
    assert not result.ok
    assert any("description" in message for message in result.messages)


def test_invalid_class_fails(tmp_path: Path) -> None:
    path = _skill(tmp_path, "example-skill", "name: example-skill\ndescription: Use when testing skills.\nclass: giant\n")
    result = validate_skill_file(path)
    assert not result.ok
    assert any("frontmatter.class" in message for message in result.messages)


def test_legacy_no_class_is_allowed(tmp_path: Path) -> None:
    path = _skill(tmp_path, "legacy-skill", "name: legacy-skill\ndescription: Use when testing legacy skills.\n")
    result = validate_skill_file(path, require_class=False)
    assert result.ok, result.messages


def test_required_class_fails_when_missing(tmp_path: Path) -> None:
    path = _skill(tmp_path, "new-skill", "name: new-skill\ndescription: Use when testing new skills.\n")
    result = validate_skill_file(path, require_class=True)
    assert not result.ok
    assert any("class is required" in message for message in result.messages)


def test_class_schemas_exist_and_are_documented() -> None:
    result = validate_class_schemas(Path("skills/skill-hygiene"))
    assert result.ok, result.messages
    assert all("schemas/" in message for message in result.messages)


def test_render_markdown_for_all_classes() -> None:
    for class_name in CLASSES:
        result = render_markdown(class_name)
        assert result.ok, result.messages
        assert f"# {class_name.title()} Skill Guidance" in result.messages[0]
