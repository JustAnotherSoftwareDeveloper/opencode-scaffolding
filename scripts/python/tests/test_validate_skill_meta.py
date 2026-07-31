"""Tests for the authoritative structured routing-signature contract."""

# ruff: noqa: E501

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import yaml

from lib.collect_skills.discovery import discover_skills_from_root
from lib.collect_skills.models import SkillIndex
from lib.collect_skills.parser import (
    parse_routing_signature,
    validate_skill_frontmatter,
)
from lib.shared.skill_routing import load_builtin_registry, resolve_registry_overlay
from lib.validate_skill_meta.core import validate_frontmatter, validate_skill_file


def signature() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "cues": [
            {"facet": "subject", "value": "routing metadata"},
            {"facet": "operation", "value": "validate-routing", "primary": True},
        ],
        "relationships": [{"role": "owner", "rationale": "owns validation"}],
    }


def frontmatter(**updates: object) -> dict[str, object]:
    data: dict[str, object] = {
        "name": "routing-skill",
        "description": "Use when validating routing metadata",
        "class": "operation",
        **signature(),
    }
    data.update(updates)
    return data


def test_valid_builtin_signature_is_accepted_by_authoring_and_discovery() -> None:
    data = frontmatter()
    assert validate_frontmatter(data) == []
    assert validate_skill_frontmatter(data, "routing-skill", Path("SKILL.md")) == []
    assert (
        parse_routing_signature(data).to_dict()
        == parse_routing_signature(data).to_dict()
    )


@pytest.mark.parametrize(
    "description",
    [
        " Use when validating routing metadata",
        "Use when validating\nrouting metadata",
        "Use when " + "x" * 1020,
    ],
)
def test_description_safety_contract_matches_authoring_and_discovery(
    description: str,
) -> None:
    data = frontmatter(description=description)

    assert validate_frontmatter(data)
    assert validate_skill_frontmatter(data, "routing-skill", Path("SKILL.md"))


def test_repository_local_facet_has_the_same_outcome_in_all_paths(
    tmp_path: Path,
) -> None:
    registry_file = tmp_path / "skill-facets.json"
    registry_file.write_text(
        '{"namespace":"repository","facets":[{"name":"artifact-kind",'
        '"meaning":"Artifact being routed","value_shape":"^(fixture|manifest)$"}]}',
        encoding="utf-8",
    )
    registry = resolve_registry_overlay(
        {
            "namespace": "repository",
            "facets": [{"name": "artifact-kind", "meaning": "Artifact"}],
        },
        load_builtin_registry(),
    )
    data = frontmatter(
        cues=[
            *cast(list[object], signature()["cues"]),
            {"facet": "repository:artifact-kind", "value": "fixture"},
        ]
    )
    assert validate_frontmatter(data, registry) == []
    assert (
        validate_skill_frontmatter(
            data, "routing-skill", tmp_path / "SKILL.md", registry
        )
        == []
    )
    assert any(
        cue.facet == "repository:artifact-kind"
        for cue in parse_routing_signature(data, registry).cues
    )


@pytest.mark.parametrize(
    ("fixture", "message"),
    [
        (
            lambda: frontmatter(cues=[{"facet": "subject", "value": "thing"}]),
            "exactly one primary",
        ),
        (
            lambda: frontmatter(
                cues=[
                    {"facet": "operation", "value": "one", "primary": True},
                    {"facet": "operation", "value": "two", "primary": True},
                ]
            ),
            "exactly one primary",
        ),
        (
            lambda: frontmatter(
                cues=[
                    {"facet": "operation", "value": "validate", "primary": True},
                    {"facet": "subject", "value": "thing", "aliases": [1]},
                ]
            ),
            "string array",
        ),
        (
            lambda: frontmatter(
                cues=[
                    {"facet": "operation", "value": "validate", "primary": True},
                    {"facet": "other:private", "value": "thing"},
                ]
            ),
            "undeclared",
        ),
        (lambda: {**frontmatter(), "tags": ["legacy-flat-tag"]}, "structured cues"),
        (
            lambda: frontmatter(
                cues=[{"facet": "operation", "value": ["validate"], "primary": True}]
            ),
            "canonical string value",
        ),
    ],
)
def test_hard_cut_routing_failures_are_actionable(fixture, message: str) -> None:  # noqa: ANN001
    data = fixture()
    errors = validate_frontmatter(data)
    assert any(message in error for error in errors)


def test_namespace_collision_is_rejected() -> None:
    with pytest.raises(ValueError, match="redefine"):
        resolve_registry_overlay(
            {
                "namespace": "repository",
                "facets": [{"name": "operation", "meaning": "collision"}],
            },
            load_builtin_registry(),
        )


def test_legacy_flat_tags_are_a_hard_failure() -> None:
    errors = validate_frontmatter(
        {
            "name": "legacy",
            "description": "Use when testing",
            "class": "operation",
            "tags": ["operation"],
        }
    )
    assert any("structured cues" in error for error in errors)


def test_file_validation_uses_structured_metadata(tmp_path: Path) -> None:
    path = tmp_path / "SKILL.md"
    path.write_text(
        "---\n" + yaml.safe_dump(frontmatter(sort_keys=False)) + "---\n",
        encoding="utf-8",
    )
    result = validate_skill_file(path)
    assert result == {"valid": True, "errors": []}


def test_discovery_accepts_the_same_repository_fixture(tmp_path: Path) -> None:
    skill_dir = tmp_path / "routing-skill"
    skill_dir.mkdir()
    (tmp_path / "skill-facets.json").write_text(
        '{"namespace":"repository","facets":[{"name":"artifact-kind","meaning":"Artifact"}]}',
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        + yaml.safe_dump(
            frontmatter(
                cues=[
                    *cast(list[object], signature()["cues"]),
                    {"facet": "repository:artifact-kind", "value": "fixture"},
                ],
                sort_keys=False,
            )
        )
        + "---\n",
        encoding="utf-8",
    )
    index = SkillIndex()
    discover_skills_from_root(tmp_path, "project", index)
    assert [skill.name for skill in index.resolve()] == ["routing-skill"]


def test_file_validation_reports_malformed_repository_registry(tmp_path: Path) -> None:
    (tmp_path / "skill-facets.json").write_text("[]", encoding="utf-8")
    path = tmp_path / "SKILL.md"
    path.write_text(
        "---\n" + yaml.safe_dump(frontmatter(sort_keys=False)) + "---\n",
        encoding="utf-8",
    )
    result = validate_skill_file(path)
    assert result["valid"] is False
    assert any(
        "repository registry must be an object" in error for error in result["errors"]
    )


def _write_skill(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "SKILL.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_file_errors_and_yaml_checks_remain_unchanged(tmp_path: Path) -> None:
    assert validate_skill_file(tmp_path / "missing.md")["errors"] == [
        f"File not found: {tmp_path / 'missing.md'}"
    ]
    assert (
        "must start with '---'"
        in validate_skill_file(_write_skill(tmp_path, "plain"))["errors"][0]
    )
    assert validate_skill_file(_write_skill(tmp_path, "---\ninvalid: [\n---\n"))[
        "errors"
    ][0].startswith("Frontmatter YAML parse error")


def test_yaml_is_available() -> None:
    assert yaml is not None
