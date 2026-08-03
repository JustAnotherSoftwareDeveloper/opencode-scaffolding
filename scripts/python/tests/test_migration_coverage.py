"""Contract and failure-path coverage for the direct-selection migration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.evaluate_semantic_selection import main as evaluate_main
from cli.generate_task_json import main as generate_main
from cli.skill_validator import cli as validator_main
from cli.validate_skill_meta import main as meta_main
from lib.collect_skills.discovery import (
    discover_all_skills,
    discover_skills_from_root,
    find_git_root,
    get_standard_search_roots,
)
from lib.collect_skills.models import Skill, SkillIndex
from lib.collect_skills.parser import extract_frontmatter, validate_skill_frontmatter
from lib.collect_skills.skill_md import parse_skill_md
from lib.generate_task_json.core import (
    GenerationValidationError,
    SummarySlugError,
    _derive_slug,
    _resolve_output_path,
    generate_task_json,
)
from lib.generate_task_json.skill_inventory import validate_skill_inventory
from lib.semantic_selection_evaluation.core import (
    EvaluationError,
    evaluate_fixture,
    load_fixture,
    load_responses,
)
from lib.skill_validator.checks import (
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
)
from lib.skill_validator.registry import run_all
from lib.validate_skill_meta.core import (
    _extract_frontmatter,
    validate_frontmatter,
    validate_skill_file,
)


def profile(name: str = "demo-skill", **extra: object) -> dict[str, object]:
    value: dict[str, object] = {
        "name": name,
        "description": "Use when testing direct selection",
        "selection": {"role": "owner", "tags": {"actions": ["test"]}},
        "class": "operation",
    }
    value.update(extra)
    return value


def write_skill(root: Path, name: str = "demo-skill", **changes: object) -> Path:
    data = profile(name, **changes)
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        *[f"{key}: {json.dumps(value)}" for key, value in data.items()],
        "---",
        "# Demo",
        "Use it.",
        "## Docs",
        "Documentation.",
    ]
    path = directory / "SKILL.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_models_parser_and_skill_md_edges(tmp_path: Path) -> None:
    skill = write_skill(tmp_path)
    parsed = extract_frontmatter(skill)
    assert parsed is not None and parsed["name"] == "demo-skill"


@pytest.mark.parametrize(
    "change",
    [
        {"description": ""},
        {"name": "Bad Name"},
        {"class": "unknown"},
        {"selection": {"role": "owner", "tags": {"unknown": ["x"]}}},
        {"selection": {"role": "owner", "tags": {"actions": ["x", "x"]}}},
    ],
)
def test_metadata_rejects_scalar_and_selection_edges(change: dict[str, object]) -> None:
    from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata

    with pytest.raises(SkillMetadataError):
        normalize_skill_metadata({**profile(), **change})


def test_metadata_rejects_invalid_role_and_optional_metadata() -> None:
    from lib.shared.skill_metadata import SkillMetadataError, normalize_skill_metadata

    with pytest.raises(SkillMetadataError):
        normalize_skill_metadata(
            {**profile(), "selection": {"role": "bad", "tags": {"actions": ["x"]}}}
        )
    with pytest.raises(SkillMetadataError):
        normalize_skill_metadata({**profile(), "metadata": "not an object"})


def test_parser_and_skill_md_malformed_inputs(tmp_path: Path) -> None:
    no_front = tmp_path / "none.md"
    no_front.write_text("body", encoding="utf-8")
    assert extract_frontmatter(no_front) is None
    incomplete = tmp_path / "incomplete.md"
    incomplete.write_text("---\nname: x\n", encoding="utf-8")
    assert extract_frontmatter(incomplete) is None
    scalar = tmp_path / "scalar.md"
    scalar.write_text("---\n- x\n---\n", encoding="utf-8")
    with pytest.raises(ValueError):
        extract_frontmatter(scalar)
    assert parse_skill_md(no_front, "extra") is None
    bad = tmp_path / "bad.md"
    bad.write_text("---\nname: bad name\n---\n", encoding="utf-8")
    assert parse_skill_md(bad, "extra") is None
    errors = validate_skill_frontmatter({}, "x", bad)
    assert any("missing 'name'" in item for item in errors)
    assert validate_skill_frontmatter(
        {**profile("x"), "description": "wrong"}, "x", bad
    )


def test_index_projection_and_precedence() -> None:
    index = SkillIndex()
    first = Skill(
        "same",
        class_="operation",
        source="global",
        path="/.claude/skills/SKILL.md",
        version="1",
        metadata={"x": 1},
    )
    project = Skill(
        "same", class_="operation", source="project", path="/.opencode/skills/SKILL.md"
    )
    index.add(first)
    index.add(project)
    index.add(
        Skill("same", class_="operation", source="archive", path="/archive/SKILL.md")
    )
    assert index.resolve()[0] is project
    assert index.warnings
    assert index.filter_by_classes(("operation",))
    assert json.loads(index.to_json())[0]["source"] == "project"


def test_discovery_roots_and_success(tmp_path: Path) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    write_skill(project / ".opencode" / "skills")
    write_skill(
        project / ".claude" / "skills",
        "doc",
        **{"class": "documentation", "description": "Use when reading docs"},
    )
    write_skill(project / ".opencode" / "archive" / "skills", "arch")
    extra = tmp_path / "extra"
    write_skill(extra, "extra-skill")
    assert get_standard_search_roots(project, config)
    index = SkillIndex()
    discover_all_skills(
        index,
        project_root=project,
        config_dir=config,
        extra_paths=[extra],
        include_archive=True,
    )
    assert {item.name for item in index.resolve()} == {
        "demo-skill",
        "doc",
        "arch",
        "extra-skill",
    }
    assert find_git_root(tmp_path) is None
    git = tmp_path / "git"
    (git / ".git").mkdir(parents=True)
    assert find_git_root(git / "child") == git


def test_discovery_failure_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    index = SkillIndex()
    discover_skills_from_root(tmp_path / "missing", "extra", index, verbose=True)
    discover_skills_from_root(tmp_path / "file", "extra", index)
    (tmp_path / "file").write_text("x", encoding="utf-8")
    discover_skills_from_root(tmp_path / "file", "extra", index, verbose=True)
    discover_skills_from_root(tmp_path, "builtin", index, verbose=True)
    assert vars(index).get("_discovery_errors")
    assert "Error" in capsys.readouterr().err
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "SKILL.md").write_text("body", encoding="utf-8")
    discover_skills_from_root(tmp_path, "extra", index)
    dangling = tmp_path / "dangling"
    dangling.mkdir()
    (dangling / "SKILL.md").symlink_to(tmp_path / "missing-skill.md")
    discover_skills_from_root(tmp_path, "extra", index)
    assert any("invalid symlink" in item for item in vars(index)["_discovery_errors"])


def test_inventory_and_output_contracts(tmp_path: Path) -> None:
    path = write_skill(tmp_path)
    record = {**profile(), "path": str(path), "source": "project"}
    frozen = validate_skill_inventory([record], project_root=tmp_path)
    assert frozen.names == ("demo-skill",)
    assert _derive_slug("Hello, world!") == "hello-world"
    assert _derive_slug("!!!") is None
    assert _resolve_output_path("x", tmp_path, None, None).parent == tmp_path / ".tasks"
    assert (
        _resolve_output_path(None, None, tmp_path, tmp_path / "x.json")
        == tmp_path / "x.json"
    )
    with pytest.raises(ValueError):
        _resolve_output_path(None, None, None, None)
    with pytest.raises(ValueError):
        _resolve_output_path("x", tmp_path, tmp_path, None)
    with pytest.raises(ValueError):
        _resolve_output_path("x", None, None, tmp_path / "x.txt")


def test_generate_packet_validation_and_atomic_output(tmp_path: Path) -> None:
    path = write_skill(tmp_path)
    record = {**profile(), "path": str(path), "source": "project"}
    data = {"summary": "Test packet", "tasks": []}
    # The published schema is intentionally exercised through a minimal invalid packet.
    with pytest.raises(GenerationValidationError):
        generate_task_json({}, skills_index=[record])
    with pytest.raises(ValueError):
        generate_task_json(data, skills_index=[record], provider=object())
    output = tmp_path / "out.json"
    with pytest.raises((GenerationValidationError, SummarySlugError)):
        generate_task_json(data, skills_index=[record], output_file=output)


def test_generate_packet_success_and_collision(tmp_path: Path) -> None:
    path = write_skill(tmp_path)
    record = {**profile(), "path": str(path), "source": "project"}
    task = {
        "purpose": "Run the direct selection contract tests",
        "context": (
            "This context is deliberately long enough to satisfy the packet schema "
            "while describing the migration and its required validation behavior "
            "for the worker. It explains the direct selection contract, frozen "
            "inventory boundary, meaningful tests, and final lint and type "
            "verification."
        ),
        "filesToRead": ["src/lib/shared/skill_metadata.py"],
        "filesToWrite": ["tests/test_direct.py"],
        "skills": ["skill-script-python-test-writer"],
        "executionInstructions": [{"step": 1, "action": "Run the tests"}],
        "expectedOutput": "A tested implementation",
    }
    data = {"summary": "Test packet", "tasks": [task]}
    output = tmp_path / "out.json"
    assert (
        generate_task_json(
            data,
            skills_index=[record],
            inventory_project_root=tmp_path,
            output_file=output,
        )
        == output
    )
    with pytest.raises(OSError, match="already exists"):
        generate_task_json(
            data,
            skills_index=[record],
            inventory_project_root=tmp_path,
            output_file=output,
        )


def test_semantic_loaders_and_contract_errors(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(EvaluationError):
        load_fixture(missing)
    missing.write_text("[]", encoding="utf-8")
    with pytest.raises(EvaluationError):
        load_fixture(missing)
    missing.write_text("{}", encoding="utf-8")
    assert load_responses(missing) == {}
    root_file = tmp_path / "skill.md"
    root_file.write_text("x", encoding="utf-8")
    base = {"inventory": [{"name": "a", "path": "skill.md"}], "cases": []}
    with pytest.raises(EvaluationError):
        evaluate_fixture(base, root=tmp_path, mode="bad")
    duplicate = {
        "inventory": [
            {"name": "a", "path": "skill.md"},
            {"name": "a", "path": "skill.md"},
        ],
        "cases": [],
    }
    with pytest.raises(EvaluationError, match="duplicate"):
        evaluate_fixture(duplicate, root=tmp_path)
    bad_case = {
        "inventory": [{"name": "a", "path": "skill.md"}],
        "cases": [{"id": "x", "expected": {"names": ["a"], "paths": []}}],
    }
    with pytest.raises(EvaluationError, match="differ"):
        evaluate_fixture(bad_case, root=tmp_path)


def test_evaluation_cli_and_generation_cli(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({"inventory": [], "cases": []}), encoding="utf-8")
    result = CliRunner().invoke(evaluate_main, [str(fixture), "--root", str(tmp_path)])
    assert result.exit_code == 0 and '"passed": true' in result.output
    bad = CliRunner().invoke(evaluate_main, [str(tmp_path / "bad.json")])
    assert bad.exit_code != 0 and "Error:" in bad.stderr
    inventory = tmp_path / "inventory.json"
    inventory.write_text("[]", encoding="utf-8")
    result = CliRunner().invoke(generate_main, ["--skills-file", str(inventory)])
    assert result.exit_code != 0 and "output-file" in result.stderr


def test_validate_skill_meta_core_and_cli(tmp_path: Path) -> None:
    path = write_skill(tmp_path)
    assert _extract_frontmatter(path.read_text()) is not None
    assert _extract_frontmatter("body") is None
    assert validate_frontmatter(profile()) == []
    assert validate_skill_file(path)["valid"]
    missing = validate_skill_file(tmp_path / "missing")
    assert not missing["valid"]
    result = CliRunner().invoke(meta_main, [str(path), "--format", "text", "--verbose"])
    assert result.exit_code == 0 and "VALID" in result.output
    invalid = tmp_path / "invalid.md"
    invalid.write_text("---\nname: bad name\n---\n", encoding="utf-8")
    assert not validate_skill_file(invalid)["valid"]
    result = CliRunner().invoke(meta_main, [str(invalid), "--format", "text"])
    assert result.exit_code == 1 and "INVALID" in result.output


def test_skill_validator_checks_and_cli(tmp_path: Path) -> None:
    skill = write_skill(tmp_path)
    (skill.parent / "reference").mkdir()
    (skill.parent / "reference" / "README.md").write_text("# docs", encoding="utf-8")
    assert check_frontmatter_valid(skill.parent).passed
    assert check_name_matches_dir(skill.parent).passed
    assert check_description_prefix(skill.parent).passed
    assert check_class_valid(skill.parent).passed
    assert check_docs_last_section(skill.parent).passed
    assert check_no_examples_section(skill.parent).passed
    assert check_one_sentence_per_line(skill.parent).passed
    assert check_no_declarative_voice(skill.parent).passed
    assert check_no_placeholders(skill.parent).passed
    assert check_cross_references_exist(skill.parent).passed
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "SKILL.md").write_text(
        "## Examples\nThis is used. It should fail.\n<<x>>\n[link](./missing.md)",
        encoding="utf-8",
    )
    assert not check_frontmatter_valid(bad).passed
    assert not check_docs_last_section(bad).passed
    assert not check_no_examples_section(bad).passed
    assert not check_no_declarative_voice(bad).passed
    assert not check_no_placeholders(bad).passed
    assert not check_cross_references_exist(bad).passed
    assert run_all(bad)["checks"]
    result = CliRunner().invoke(validator_main, [str(bad)])
    assert result.exit_code == 1
