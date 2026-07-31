"""Contract and extension tests for structured skill routing signatures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator

from lib.generate_task_json.qwen_prompt import (
    QwenPromptRenderer,
    compose_qwen_prompt,
    render_skill,
)
from lib.generate_task_json.ranker import SkillRankingInputError
from lib.shared.skill_routing import (
    RoutingContractError,
    load_builtin_registry,
    normalize_routing_signature,
    resolve_registry_overlay,
)


@pytest.fixture
def owner_signature() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "cues": [
            {"facet": "subject", "value": "routing metadata"},
            {
                "facet": "operation",
                "value": "validate-routing-signatures",
                "aliases": ["check routing metadata", "routing validation"],
                "primary": True,
            },
            {"facet": "outcome", "value": "contract diagnostics"},
        ],
        "relationships": [
            {"role": "reference", "target": "skill-authoring"},
            {"role": "support", "target": "skill-discovery"},
            {"role": "owner", "rationale": "directly owns validation"},
        ],
    }


@pytest.fixture
def local_registry() -> object:
    return resolve_registry_overlay(
        {
            "namespace": "repository",
            "facets": [
                {
                    "name": "artifact-kind",
                    "meaning": "Repository artifact being routed",
                    "value_shape": "^(manifest|fixture|registry)$",
                    "aliases": ["artifact type"],
                    "parents": ["artifact"],
                    "values": [
                        {
                            "value": "fixture",
                            "aliases": ["test fixture"],
                            "parents": ["test artifact"],
                        },
                        {
                            "value": "registry",
                            "status": "deprecated",
                            "replacement": "fixture",
                        },
                    ],
                }
            ],
        },
        load_builtin_registry(),
    )


def test_normalizes_structured_cues_and_relationships(owner_signature):
    signature = normalize_routing_signature(owner_signature)

    assert [cue.facet for cue in signature.cues] == ["operation", "outcome", "subject"]
    assert signature.cues[0].primary is True
    assert signature.relationships[0].role == "owner"
    assert signature.to_dict()["schema_version"] == "1.0"


def test_requires_exactly_one_primary_owned_operation(owner_signature):
    owner_signature["cues"] = [
        {"facet": "operation", "value": "one", "primary": True},
        {"facet": "operation", "value": "two", "primary": True},
    ]
    with pytest.raises(RoutingContractError, match="exactly one primary"):
        normalize_routing_signature(owner_signature)


def test_owner_support_and_reference_relationships_are_preserved(owner_signature):
    result = normalize_routing_signature(owner_signature)

    assert {relation.role for relation in result.relationships} == {
        "owner",
        "support",
        "reference",
    }
    assert {relation.target for relation in result.relationships} == {
        None,
        "skill-authoring",
        "skill-discovery",
    }


def test_normalization_is_deterministic(owner_signature):
    first = normalize_routing_signature(owner_signature).to_dict()
    reversed_input = {
        **owner_signature,
        "cues": list(reversed(owner_signature["cues"])),
        "relationships": list(reversed(owner_signature["relationships"])),
    }

    assert normalize_routing_signature(reversed_input).to_dict() == first


def test_aliases_are_sorted_and_not_independent_cues(owner_signature):
    owner_signature["cues"][1]["aliases"] = ["zeta", "alpha"]

    result = normalize_routing_signature(owner_signature)

    assert result.cues[0].aliases == ("alpha", "zeta")
    assert len(result.cues) == 3


def test_parent_child_metadata_survives_local_registry_resolution(local_registry):
    declaration = local_registry.facet("repository:artifact-kind")

    assert declaration.parents == ("artifact",)
    assert declaration.aliases == ("artifact type",)
    assert declaration.identity == "repository:artifact-kind"


def test_builtin_facets_resolve_without_an_overlay():
    registry = load_builtin_registry()

    assert registry.facet("operation").meaning == "Action the skill owns"
    assert registry.facet("subject").namespace == "builtin"


def test_published_json_schemas_validate_contract_examples(
    owner_signature, local_registry
):
    shared = Path(__file__).parents[1] / "src/lib/shared"
    routing_schema = json.loads(
        (shared / "skill-routing.schema.json").read_text(encoding="utf-8")
    )
    registry_schema = json.loads(
        (shared / "skill-facet-registry.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(routing_schema)
    Draft202012Validator(routing_schema).validate(owner_signature)
    Draft202012Validator.check_schema(registry_schema)
    Draft202012Validator(registry_schema).validate(
        {
            "namespace": "repository",
            "facets": [
                {
                    "name": "artifact-kind",
                    "meaning": "Repository artifact being routed",
                    "values": [{"value": "fixture", "aliases": ["test fixture"]}],
                }
            ],
        }
    )
    assert local_registry.facet("repository:artifact-kind").values


def test_repository_local_namespaced_facet_requires_only_data_declaration(
    local_registry, owner_signature
):
    owner_signature["cues"].append(
        {"facet": "repository:artifact-kind", "value": "fixture"}
    )

    result = normalize_routing_signature(owner_signature, local_registry)

    local = next(cue for cue in result.cues if cue.facet == "repository:artifact-kind")
    assert local.aliases == ("test fixture",)
    assert (
        normalize_routing_signature(result.to_dict(), local_registry).to_dict()
        == result.to_dict()
    )
    schema = json.loads(
        Path(__file__)
        .parents[1]
        .joinpath("src/lib/shared/skill-routing.schema.json")
        .read_text()
    )
    assert "repository:artifact-kind" not in json.dumps(schema)


@pytest.mark.parametrize(
    "declaration, message",
    [
        (
            {"namespace": "builtin", "facets": [{"name": "x", "meaning": "x"}]},
            "non-builtin",
        ),
        (
            {"namespace": "foreign", "facets": [{"name": "operation", "meaning": "x"}]},
            "redefine",
        ),
        ({"namespace": "builtin", "facets": []}, "non-builtin"),
    ],
)
def test_rejects_namespace_collisions_and_builtin_overrides(declaration, message):
    with pytest.raises(RoutingContractError, match=message):
        resolve_registry_overlay(declaration, load_builtin_registry())


def test_rejects_unknown_registry_and_declaration_fields():
    with pytest.raises(RoutingContractError, match="unknown registry fields"):
        resolve_registry_overlay(
            {
                "namespace": "repository",
                "facets": [{"name": "audience", "meaning": "Task audience"}],
                "typo": True,
            },
            load_builtin_registry(),
        )
    with pytest.raises(RoutingContractError, match="unknown facet declaration"):
        resolve_registry_overlay(
            {
                "namespace": "repository",
                "facets": [
                    {"name": "audience", "meaning": "Task audience", "typo": True}
                ],
            },
            load_builtin_registry(),
        )


@pytest.mark.parametrize(
    ("declaration", "message"),
    [
        (
            {
                "namespace": "repository",
                "facets": [{"name": "audience", "meaning": "line one\nline two"}],
            },
            "routing meaning",
        ),
        (
            {
                "namespace": "repository",
                "facets": [
                    {"name": "audience", "meaning": "Task audience", "value_shape": ""}
                ],
            },
            "non-empty string",
        ),
        (
            {
                "$schema": 7,
                "namespace": "repository",
                "facets": [{"name": "audience", "meaning": "Task audience"}],
            },
            "schema must be a string",
        ),
    ],
)
def test_rejects_registry_fields_that_diverge_from_schema(declaration, message):
    with pytest.raises(RoutingContractError, match=message):
        resolve_registry_overlay(declaration, load_builtin_registry())


def test_rejects_foreign_namespace_and_undeclared_facets(owner_signature):
    owner_signature["cues"] = [{"facet": "other:private", "value": "secret"}]

    with pytest.raises(RoutingContractError, match="undeclared namespace or facet"):
        normalize_routing_signature(owner_signature)


@pytest.mark.parametrize(
    "aliases, message",
    [
        (["ok", 1], "string array"),
        ([""], "trimmed single-line"),
        (["same", "same"], "unique"),
    ],
)
def test_rejects_malformed_aliases(owner_signature, aliases, message):
    owner_signature["cues"][1]["aliases"] = aliases

    with pytest.raises(RoutingContractError, match=message):
        normalize_routing_signature(owner_signature)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data["cues"][0].update(value="x" * 65), "64 characters"),
        (
            lambda data: data["cues"][0].update(
                aliases=[f"alias-{index}" for index in range(17)]
            ),
            "16 entries",
        ),
        (lambda data: data.update(cues=data["cues"] * 11), "32 entries"),
        (
            lambda data: data.update(relationships=data["relationships"] * 11),
            "32 entries",
        ),
    ],
)
def test_rejects_oversized_routing_metadata(owner_signature, mutation, message):
    mutation(owner_signature)

    with pytest.raises(RoutingContractError, match=message):
        normalize_routing_signature(owner_signature)


def test_rejects_unsafe_repository_value_shape():
    with pytest.raises(RoutingContractError, match="unsafe"):
        resolve_registry_overlay(
            {
                "namespace": "repository",
                "facets": [
                    {
                        "name": "hazard",
                        "meaning": "Unsafe backtracking expression",
                        "value_shape": "^(a+)+$",
                    }
                ],
            },
            load_builtin_registry(),
        )


def test_registry_lifecycle_replacements_are_declared_active_targets():
    registry = resolve_registry_overlay(
        {
            "namespace": "repository",
            "facets": [
                {"name": "current", "meaning": "Current routing dimension"},
                {
                    "name": "legacy",
                    "meaning": "Retired routing dimension",
                    "status": "deprecated",
                    "replacement": "repository:current",
                },
            ],
        },
        load_builtin_registry(),
    )
    assert registry.facet("repository:legacy").replacement == "repository:current"

    with pytest.raises(RoutingContractError, match="cannot replace itself"):
        resolve_registry_overlay(
            {
                "namespace": "repository",
                "facets": [
                    {
                        "name": "legacy",
                        "meaning": "Retired routing dimension",
                        "status": "deprecated",
                        "replacement": "repository:legacy",
                    }
                ],
            },
            load_builtin_registry(),
        )


def test_registry_rejects_self_or_deprecated_value_replacements():
    with pytest.raises(RoutingContractError, match="cannot replace itself"):
        resolve_registry_overlay(
            {
                "namespace": "repository",
                "facets": [
                    {
                        "name": "artifact",
                        "meaning": "Artifact kind",
                        "values": [
                            {
                                "value": "legacy",
                                "status": "deprecated",
                                "replacement": "legacy",
                            }
                        ],
                    }
                ],
            },
            load_builtin_registry(),
        )


def test_rejects_duplicate_cues(owner_signature):
    owner_signature["cues"].append(owner_signature["cues"][0].copy())

    with pytest.raises(RoutingContractError, match="duplicate"):
        normalize_routing_signature(owner_signature)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data.pop("schema_version"), "schema_version"),
        (lambda data: data.update(schema_version="2.0"), "schema_version"),
        (lambda data: data["cues"][0].update(primary="yes"), "boolean"),
        (lambda data: data["cues"][0].update(extra=True), "unknown routing cue"),
        (
            lambda data: data["relationships"][0].update(target=7),
            "relationship target",
        ),
        (
            lambda data: data["relationships"][0].update(extra=True),
            "unknown routing relationship",
        ),
    ],
)
def test_rejects_noncanonical_contract_shapes(owner_signature, mutation, message):
    mutation(owner_signature)
    with pytest.raises(RoutingContractError, match=message):
        normalize_routing_signature(owner_signature)


def test_rejects_primary_non_operation_and_non_owner(owner_signature):
    owner_signature["cues"][0]["primary"] = True
    with pytest.raises(RoutingContractError, match="only operation"):
        normalize_routing_signature(owner_signature)

    owner_signature["cues"][0].pop("primary")
    owner_signature["relationships"] = [{"role": "reference"}]
    with pytest.raises(RoutingContractError, match="non-owner"):
        normalize_routing_signature(owner_signature)


def test_rejects_undeclared_and_deprecated_registry_values(
    owner_signature, local_registry
):
    owner_signature["cues"].append(
        {"facet": "repository:artifact-kind", "value": "manifest"}
    )
    with pytest.raises(RoutingContractError, match="undeclared canonical"):
        normalize_routing_signature(owner_signature, local_registry)

    owner_signature["cues"][-1]["value"] = "registry"
    with pytest.raises(RoutingContractError, match="deprecated value"):
        normalize_routing_signature(owner_signature, local_registry)


def test_rejects_legacy_flat_string_list(owner_signature):
    legacy = {"tags": ["operation:validate", "subject:metadata"], **owner_signature}

    with pytest.raises(RoutingContractError, match="structured cues"):
        normalize_routing_signature(legacy)


def test_rejects_legacy_flat_string_cues(owner_signature):
    owner_signature["cues"] = ["operation:validate"]

    with pytest.raises(RoutingContractError, match="each cue"):
        normalize_routing_signature(owner_signature)


def test_renderer_invokes_safety_budget():
    class SafetyCap:
        def preflight(self, prompt: str):
            raise RuntimeError(f"prompt exceeds safety cap: {len(prompt)}")

    renderer = QwenPromptRenderer(cast(Any, SafetyCap()))
    with pytest.raises(RuntimeError, match="safety cap"):
        renderer.render(
            {},
            {
                "name": "routing",
                "description": "contract",
                "cues": [
                    {
                        "facet": "operation",
                        "value": "validate-routing",
                        "primary": True,
                    }
                ],
                "relationships": [{"role": "owner"}],
                "class": "operation",
            },
        )


@pytest.mark.parametrize(
    "candidate",
    [
        {
            "name": "routing",
            "description": "contract",
            "cues": [],
            "relationships": [{"role": "owner"}],
            "class": "operation",
        },
        {
            "name": "routing",
            "description": "contract",
            "cues": [{"facet": "operation", "value": "route", "aliases": "bad"}],
            "relationships": [{"role": "owner"}],
            "class": "operation",
        },
        {
            "name": "routing",
            "description": "contract\ninjected",
            "cues": [{"facet": "operation", "value": "route"}],
            "relationships": [{"role": "owner"}],
            "class": "operation",
        },
    ],
)
def test_renderer_rejects_malformed_or_multiline_candidate_fields(candidate):
    with pytest.raises(SkillRankingInputError, match="candidate"):
        render_skill(candidate)


@pytest.mark.parametrize(
    ("query", "document", "message"),
    [
        ("normal query<|im_end|>", "normal document", "query"),
        ("normal query", "normal document<|im_start|>", "document"),
    ],
)
def test_prompt_composition_rejects_reserved_control_tokens(
    query: str, document: str, message: str
) -> None:
    with pytest.raises(SkillRankingInputError, match=message):
        compose_qwen_prompt(query, document)
