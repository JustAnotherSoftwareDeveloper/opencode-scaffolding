"""Focused contract tests for direct skill selection metadata."""

from __future__ import annotations

import copy

import pytest
from jsonschema import Draft202012Validator, ValidationError

from lib.shared.skill_metadata import (
    SkillMetadataError,
    load_skill_metadata_schema,
    normalize_skill_metadata,
)


@pytest.fixture
def profile() -> dict[str, object]:
    return {
        "name": "make-script",
        "description": "Create a deterministic script",
        "class": "operation",
        "selection": {
            "role": "owner",
            "tags": {
                "actions": ["create", "generate"],
                "inputs": ["requirements"],
                "outputs": ["script"],
            },
            "use_when": ["a script must be created"],
            "not_for": ["editing an existing script"],
            "supports": ["skill-authoring-guide"],
        },
        "version": "1.0",
        "metadata": {"team": "tools"},
    }


def test_normalizes_and_preserves_authored_order(profile):
    result = normalize_skill_metadata(profile)
    assert result.selection.tags.actions == ("create", "generate")
    assert result.selection.to_dict()["use_when"] == ["a script must be created"]
    assert result.to_dict()["metadata"] == {"team": "tools"}


def test_schema_is_valid_and_accepts_example(profile):
    schema = load_skill_metadata_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(profile)


@pytest.mark.parametrize(
    "field", ["schema_version", "cues", "relationships", "location", "score", "rank"]
)
def test_rejects_obsolete_fields(profile, field):
    candidate = copy.deepcopy(profile)
    candidate[field] = []
    with pytest.raises(SkillMetadataError, match="obsolete"):
        normalize_skill_metadata(candidate)


def test_rejects_unknown_fields_and_empty_groups(profile):
    candidate = copy.deepcopy(profile)
    candidate["selection"]["tags"]["actions"] = []
    with pytest.raises(SkillMetadataError, match="non-empty"):
        normalize_skill_metadata(candidate)
    candidate = copy.deepcopy(profile)
    candidate["unexpected"] = True
    with pytest.raises(SkillMetadataError, match="unknown metadata"):
        normalize_skill_metadata(candidate)


def test_rejects_duplicate_and_self_support(profile):
    candidate = copy.deepcopy(profile)
    candidate["selection"]["supports"] = [
        "skill-authoring-guide",
        "skill-authoring-guide",
    ]
    with pytest.raises(SkillMetadataError, match="unique"):
        normalize_skill_metadata(candidate)
    candidate["selection"]["supports"] = ["make-script"]
    with pytest.raises(SkillMetadataError, match="itself"):
        normalize_skill_metadata(candidate)


def test_schema_rejects_unknown_and_empty_root_values(profile):
    schema = load_skill_metadata_schema()
    invalid = {
        **profile,
        "selection": {**profile["selection"], "tags": {"actions": []}},
    }
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(invalid)
