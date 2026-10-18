"""Contract tests for skill metadata, skill indexes, and discovery edges."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from lib.collect_skills import skill_md
from lib.collect_skills.discovery import (
    discover_all_skills,
    discover_skills_from_root,
    find_git_root,
    get_standard_search_roots,
)
from lib.collect_skills.models import Skill, SkillIndex
from lib.collect_skills.parser import (
    extract_frontmatter,
    validate_skill_frontmatter,
)
from lib.collect_skills.skill_md import parse_skill_md
from lib.shared.git import find_git_root as find_shared_git_root
from lib.skill_metadata import (
    SelectionProfile,
    SelectionTags,
    SkillMetadataError,
    load_skill_metadata_schema,
    normalize_skill_metadata,
)

pytestmark = pytest.mark.unit


def _profile(
    name: str = "sample-skill", **updates: object
) -> dict[str, object]:
    value: dict[str, object] = {
        "name": name,
        "description": "Use when testing metadata",
        "class": "operation",
        "selection": {"role": "owner", "tags": {"actions": ["test"]}},
    }
    value.update(updates)
    return value


def _write_skill(root: Path, name: str, **updates: object) -> Path:
    profile = _profile(name, **updates)
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "SKILL.md"
    path.write_text(
        "---\n" + yaml.safe_dump(profile, sort_keys=False) + "---\n",
        encoding="utf-8",
    )
    return path


def test_metadata_profiles_serialize_authored_optional_groups() -> None:
    """Preserve ordered selection descriptors and valid authored optionals."""
    tags = SelectionTags(actions=("test",), outputs=("report",))
    selection = SelectionProfile(
        "owner",
        tags,
        aliases=("testing",),
        use_when=("coverage work",),
        not_for=("production edits",),
        supports=("generic-executor",),
    )
    assert selection.to_dict() == {
        "role": "owner",
        "tags": {"actions": ["test"], "outputs": ["report"]},
        "aliases": ["testing"],
        "use_when": ["coverage work"],
        "not_for": ["production edits"],
        "supports": ["generic-executor"],
    }

    normalized = normalize_skill_metadata(
        _profile(
            selection={
                "role": "owner",
                "tags": {"actions": ["test"]},
                "aliases": ["testing"],
                "use_when": ["coverage work"],
                "not_for": ["source editing"],
                "supports": ["generic-executor"],
            },
            version="1",
            license="MIT",
            compatibility="OpenCode",
            metadata={"team": "automation"},
            permission="read-only",
        )
    )
    assert normalized.selection.aliases == ("testing",)
    assert normalized.selection.supports == ("generic-executor",)
    assert normalized.to_dict()["metadata"] == {"team": "automation"}
    assert load_skill_metadata_schema()["type"] == "object"


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (None, "metadata must be an object"),
        ({"name": "Bad_Name"}, "canonical skill name"),
        ({"selection": "wrong"}, "selection is required"),
        ({"selection": {"role": "owner", "extra": []}}, "unknown selection"),
        (
            {"selection": {"role": "owner", "tags": {}}},
            "at least one tag group",
        ),
        (
            {
                "selection": {
                    "role": "owner",
                    "tags": {"actions": ["x"]},
                    "supports": ["sample-skill"],
                }
            },
            "cannot contain the skill itself",
        ),
    ],
)
def test_metadata_normalizer_rejects_invalid_root_and_selection(
    value: object, message: str
) -> None:
    """Reject invalid roots and selection contracts with actionable errors."""
    data = _profile()
    if value is None:
        invalid = value
    else:
        if isinstance(value, dict):
            data.update(value)
            invalid = data
        else:
            invalid = value
    with pytest.raises(SkillMetadataError, match=message):
        normalize_skill_metadata(invalid)


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"name": "x" * 129}, "exceeds 128"),
        ({"description": "x" * 1025}, "exceeds 1024"),
        ({"version": "x" * 257}, "exceeds 256"),
        (
            {"selection": {"role": "owner", "tags": {"actions": ["x"] * 33}}},
            "exceeds 32",
        ),
        (
            {"selection": {"role": "owner", "tags": {"actions": ["x", "x"]}}},
            "must be unique",
        ),
        (
            {
                "selection": {
                    "role": "owner",
                    "tags": {"actions": ["x"]},
                    "supports": ["bad name"],
                }
            },
            "canonical skill names",
        ),
    ],
)
def test_metadata_normalizer_enforces_text_array_and_optional_limits(
    updates: dict[str, object], message: str
) -> None:
    """Reject overlong, duplicated, or malformed authored metadata values."""
    with pytest.raises(SkillMetadataError, match=message):
        normalize_skill_metadata({**_profile(), **updates})


def test_skill_projection_and_index_precedence_are_stable() -> None:
    """Serialize authored optionals and report source precedence changes."""
    base = Skill(
        "demo",
        class_="operation",
        source="global",
        path="/.claude/skills/demo",
    )
    assert base.to_dict() == {
        "name": "demo",
        "description": "",
        "selection": {},
        "class": "operation",
        "path": "/.claude/skills/demo",
        "source": "global",
    }
    index = SkillIndex()
    index.add(base)
    index.add(
        Skill(
            "demo",
            class_="operation",
            source="project",
            path="/.opencode/skills/demo",
        )
    )
    index.add(
        Skill(
            "demo", class_="operation", source="archive", path="/archive/demo"
        )
    )
    index.add(Skill("other", source="unknown"))
    assert [item.name for item in index.resolve()] == ["demo", "other"]
    assert index.filter_by_classes(("operation",))[0].source == "project"
    assert len(index.warnings) == 2

    optional = Skill(
        "with-optionals",
        class_="operation",
        version="1",
        license="MIT",
        compatibility="OpenCode",
        metadata={"owner": "team"},
        permission="read-only",
    )
    projection = optional.to_dict()
    assert projection["version"] == "1"
    assert projection["license"] == "MIT"
    assert projection["compatibility"] == "OpenCode"
    assert projection["metadata"] == {"owner": "team"}
    assert projection["permission"] == "read-only"
    warnings = index.warnings
    warnings.clear()
    assert len(index.warnings) == 2


def test_frontmatter_parsers_and_metadata_validation_cover_supported_shapes(
    tmp_path: Path,
) -> None:
    """Keep parser aliases consistent across parse and metadata errors."""
    no_frontmatter = tmp_path / "body.md"
    no_frontmatter.write_text("intro\n---\nname: ignored\n---\n")
    assert extract_frontmatter(no_frontmatter) is None
    assert parse_skill_md(no_frontmatter, "extra") is None

    empty = tmp_path / "empty.md"
    empty.write_text("---\n---\n")
    assert extract_frontmatter(empty) == {}
    scalar = tmp_path / "scalar.md"
    scalar.write_text("---\n- value\n---\n")
    with pytest.raises(ValueError, match="must be a mapping"):
        extract_frontmatter(scalar)

    malformed = tmp_path / "malformed.md"
    malformed.write_text("---\nname: [unterminated\n---\n")
    assert parse_skill_md(malformed, "extra") is None
    valid = _write_skill(tmp_path, "sample-skill", version="v1")
    parsed = parse_skill_md(valid, "extra")
    assert parsed is not None and parsed.version == "v1"
    assert parsed.path == str(valid.resolve())
    assert validate_skill_frontmatter(_profile(), "sample-skill", valid) == []
    errors = validate_skill_frontmatter(
        {"name": "Bad Name", "description": "bad\ntext", "class": "bad"},
        "another-dir",
        valid,
    )
    assert any("must match" in error for error in errors)
    assert any("single-line" in error for error in errors)
    assert any("class" in error for error in errors)
    invalid_scalars = validate_skill_frontmatter(
        {"name": 3, "description": 4, "class": "operation"},
        "sample-skill",
        valid,
    )
    assert any(
        "name' must be a non-empty string" in error for error in invalid_scalars
    )
    assert any(
        "description' must be a non-empty string" in error
        for error in invalid_scalars
    )

    unclosed = tmp_path / "unclosed.md"
    unclosed.write_text("---\nname: incomplete\n", encoding="utf-8")
    assert skill_md.extract_frontmatter(unclosed) is None
    empty_frontmatter = tmp_path / "empty-frontmatter.md"
    empty_frontmatter.write_text("---\n---\n", encoding="utf-8")
    assert skill_md.extract_frontmatter(empty_frontmatter) == {}
    scalar_frontmatter = tmp_path / "scalar-frontmatter.md"
    scalar_frontmatter.write_text("---\n- value\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        skill_md.extract_frontmatter(scalar_frontmatter)
    bad_metadata = tmp_path / "bad-metadata.md"
    bad_metadata.write_text(
        "---\nname: bad name\ndescription: bad\nclass: operation\n"
        "selection: {role: owner, tags: {actions: [test]}}\n---\n",
        encoding="utf-8",
    )
    assert skill_md.parse_skill_md(bad_metadata, "extra") is None


def test_collector_frontmatter_wrapper_matches_parser_boundaries(
    tmp_path: Path,
) -> None:
    """Preserve parser equivalence and fail-closed wrapper diagnostics."""
    valid = "---\n" + yaml.safe_dump(_profile(), sort_keys=False) + "---\n"
    cases = {
        "valid": (valid, "mapping"),
        "absent": ("Body without frontmatter.\n", "none"),
        "unclosed": ("---\nname: sample-skill\n", "none"),
        "empty": ("---\n---\n", "empty"),
        "malformed": ("---\nname: [broken\n---\n", "yaml-error"),
        "scalar": ("---\nplain-scalar\n---\n", "non-mapping"),
        "list": ("---\n- item\n---\n", "non-mapping"),
    }

    for name, (content, category) in cases.items():
        path = tmp_path / f"{name}.md"
        path.write_text(content, encoding="utf-8")
        if category in {"mapping", "none", "empty"}:
            canonical = extract_frontmatter(path)
            wrapped = skill_md.extract_frontmatter(path)
            assert wrapped == canonical
            if category == "none":
                assert canonical is None
                assert parse_skill_md(path, "extra") is None
            elif category == "empty":
                assert canonical == {}
                assert parse_skill_md(path, "extra") is None
            else:
                assert canonical == _profile()
                assert parse_skill_md(path, "extra") is not None
        elif category == "yaml-error":
            with pytest.raises(yaml.YAMLError) as canonical_error:
                extract_frontmatter(path)
            with pytest.raises(yaml.YAMLError) as wrapper_error:
                skill_md.extract_frontmatter(path)
            assert type(wrapper_error.value) is type(canonical_error.value)
            assert parse_skill_md(path, "extra") is None
        else:
            with pytest.raises(ValueError, match="must be a mapping"):
                extract_frontmatter(path)
            with pytest.raises(
                ValueError, match="SKILL.md frontmatter must be a mapping"
            ):
                skill_md.extract_frontmatter(path)
            assert parse_skill_md(path, "extra") is None

    undecodable = tmp_path / "undecodable.md"
    undecodable.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError) as canonical_error:
        extract_frontmatter(undecodable)
    with pytest.raises(UnicodeDecodeError) as wrapper_error:
        skill_md.extract_frontmatter(undecodable)
    assert type(wrapper_error.value) is type(canonical_error.value)


def test_discovery_search_roots_and_git_ancestor_rules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Find only existing standard roots and return the nearest Git parent."""
    project = tmp_path / "project"
    config = tmp_path / "home" / ".config" / "opencode"
    candidates = [
        project / ".opencode" / "skills",
        project / ".claude" / "skills",
        project / ".agents" / "skills",
        config / "skills",
        config.parent / ".claude" / "skills",
        config.parent / ".agents" / "skills",
    ]
    for candidate in candidates:
        candidate.mkdir(parents=True)
    roots = get_standard_search_roots(project, config)
    assert [source for _, source in roots] == ["project"] * 3 + ["global"] * 3

    repository = project / "repo"
    nested = repository / "nested"
    (repository / ".git").mkdir(parents=True)
    nested.mkdir()
    assert find_git_root(nested) == repository
    assert find_shared_git_root(nested) == repository
    assert find_git_root(tmp_path / "outside") is None
    assert find_shared_git_root(tmp_path / "outside") is None

    monkeypatch.chdir(project)
    relative_nested = Path("repo") / "nested"
    assert find_git_root(relative_nested) == repository.resolve()
    assert find_shared_git_root(relative_nested) == repository.resolve()


def test_discovery_resolves_precedence_archive_and_unresolved_supports(
    tmp_path: Path,
) -> None:
    """Finalize precedence and reject unresolved relationship targets."""
    project = tmp_path / "project"
    config = tmp_path / "config" / "opencode"
    project_root = project / ".opencode" / "skills"
    global_root = config / "skills"
    archive_root = project / ".opencode" / "archive" / "skills"
    _write_skill(project_root, "same")
    _write_skill(global_root, "same")
    _write_skill(archive_root, "archived")
    index = SkillIndex()
    discover_all_skills(
        index,
        project_root=project,
        config_dir=config,
        include_archive=True,
    )
    assert {item.name for item in index.resolve()} == {"same", "archived"}
    winning = next(item for item in index.resolve() if item.name == "same")
    assert winning.source == "project"

    duplicate_root = tmp_path / "duplicates"
    _write_skill(duplicate_root, "collision")
    duplicate = _write_skill(duplicate_root, "collision-alias")
    duplicate.write_text(
        duplicate.read_text(encoding="utf-8").replace(
            "collision-alias", "collision"
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="equal-precedence"):
        discover_all_skills(SkillIndex(), extra_paths=[duplicate_root])

    support_root = tmp_path / "support"
    _write_skill(
        support_root,
        "requester",
        selection={
            "role": "owner",
            "tags": {"actions": ["test"]},
            "supports": ["absent-target"],
        },
    )
    with pytest.raises(ValueError, match="unresolved skill"):
        discover_all_skills(SkillIndex(), extra_paths=[support_root])


def test_discovery_aggregates_unreadable_and_escaping_entries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Report resolution, root-read, and symlink escapes before finalization."""
    root = tmp_path / "root"
    root.mkdir()
    index = SkillIndex()
    outside = tmp_path / "outside"
    _write_skill(outside, "external")
    (root / "escaped-dir").symlink_to(outside, target_is_directory=True)
    (root / "dangling-entry").symlink_to(tmp_path / "missing-entry")
    ordinary_file = root / "ordinary.txt"
    ordinary_file.write_text("not a skill directory", encoding="utf-8")
    (root / "file-target").symlink_to(ordinary_file)
    _write_skill(root, "external-file-link")
    linked_skill = root / "external-file-link" / "SKILL.md"
    linked_skill.unlink()
    linked_skill.symlink_to(outside / "external" / "SKILL.md")
    discover_skills_from_root(root, "extra", index, verbose=True)
    errors = vars(index)["_discovery_errors"]
    assert any("cannot resolve" in error for error in errors)
    assert any("escapes search root" in error for error in errors)
    assert "Error" in capsys.readouterr().err

    unreadable = tmp_path / "unreadable"
    unreadable.mkdir()
    original_iterdir = Path.iterdir

    def fail_root(path: Path):
        if path == unreadable.resolve():
            raise OSError("permission denied")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_root)
    failure_index = SkillIndex()
    discover_skills_from_root(unreadable, "extra", failure_index)
    first_error = vars(failure_index)["_discovery_errors"][0]
    assert "cannot read search root" in first_error


def test_discovery_skips_duplicate_targets_and_non_skill_directories(
    tmp_path: Path,
) -> None:
    """Visit one resolved directory once and exclude reserved scan names."""
    root = tmp_path / "skills"
    _write_skill(root, "real")
    (root / "alias").symlink_to(root / "real", target_is_directory=True)
    for ignored in ("_private", ".hidden", "node_modules", "__pycache__"):
        (root / ignored).mkdir()
        _write_skill(root / ignored, "ignored")
    index = SkillIndex()
    discover_skills_from_root(root, "extra", index)
    assert [item.name for item in index.resolve()] == ["real"]
