"""Versioned, extensible routing-signature metadata.

This module is deliberately a hard-cut contract: cues are structured objects,
and no API accepts the former string-list representation.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

RoutingRole = Literal["owner", "support", "reference"]
_NAME = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_NAMESPACED = re.compile(
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
)
_SUPPORTED_SCHEMA_VERSION = "1.0"
MAX_ROUTING_CUES = 32
MAX_CUE_TEXT_LENGTH = 64
MAX_ALIASES_PER_CUE = 16
MAX_ROUTING_RELATIONSHIPS = 32
MAX_RELATIONSHIP_TARGET_LENGTH = 128
MAX_RELATIONSHIP_RATIONALE_LENGTH = 256
MAX_REGISTRY_FACETS = 128
MAX_REGISTRY_VALUES = 256
MAX_REGISTRY_LIST_ITEMS = 32
MAX_REGISTRY_TEXT_LENGTH = 256
MAX_VALUE_SHAPE_LENGTH = 256
MAX_SKILL_DESCRIPTION_LENGTH = 1024
MAX_SKILL_NAME_LENGTH = 128
MAX_SKILL_CANDIDATES = 128


class RoutingContractError(ValueError):
    """Raised when routing metadata or its vocabulary is invalid."""


@dataclass(frozen=True, order=True)
class SchemaVersion:
    major: int = 1
    minor: int = 0

    def __post_init__(self) -> None:
        if self.major < 1 or self.minor < 0:
            raise RoutingContractError("schema version must be positive")

    @property
    def value(self) -> str:
        return f"{self.major}.{self.minor}"


@dataclass(frozen=True)
class RoutingCue:
    facet: str
    value: str
    aliases: tuple[str, ...] = ()
    primary: bool = False

    def __post_init__(self) -> None:
        if not self.facet or not self.value:
            raise RoutingContractError("routing cue facet and value are required")
        if any(not alias for alias in self.aliases):
            raise RoutingContractError("routing cue aliases cannot be empty")
        if len(set(self.aliases)) != len(self.aliases):
            raise RoutingContractError("routing cue aliases must be unique")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"facet": self.facet, "value": self.value}
        if self.aliases:
            result["aliases"] = list(self.aliases)
        if self.primary:
            result["primary"] = True
        return result


@dataclass(frozen=True)
class RoutingRelationship:
    role: RoutingRole
    target: str | None = None
    rationale: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"role": self.role}
        if self.target is not None:
            result["target"] = self.target
        if self.rationale is not None:
            result["rationale"] = self.rationale
        return result


@dataclass(frozen=True)
class FacetValueDeclaration:
    value: str
    aliases: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    status: Literal["active", "deprecated"] = "active"
    replacement: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.value, "facet value", max_length=MAX_CUE_TEXT_LENGTH)
        _require_string_items(
            self.aliases,
            "facet value aliases",
            max_items=MAX_ALIASES_PER_CUE,
            max_length=MAX_CUE_TEXT_LENGTH,
        )
        _require_string_items(self.parents, "facet value parents")
        if self.value in self.aliases:
            raise RoutingContractError("facet value cannot alias itself")
        if self.status not in ("active", "deprecated"):
            raise RoutingContractError(
                "facet value status must be active or deprecated"
            )
        if self.status == "deprecated" and not self.replacement:
            raise RoutingContractError("deprecated facet values require a replacement")
        if self.status == "active" and self.replacement is not None:
            raise RoutingContractError(
                "active facet values cannot declare a replacement"
            )
        if self.replacement is not None:
            _require_text(
                self.replacement,
                "facet value replacement",
                max_length=MAX_CUE_TEXT_LENGTH,
            )


@dataclass(frozen=True)
class FacetDeclaration:
    namespace: str
    name: str
    meaning: str
    value_shape: str = "^[^\\s].*$"
    examples: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    status: Literal["active", "deprecated"] = "active"
    replacement: str | None = None
    values: tuple[FacetValueDeclaration, ...] = ()

    @property
    def identity(self) -> str:
        return (
            self.name
            if self.namespace == "builtin"
            else f"{self.namespace}:{self.name}"
        )

    def accepts(self, value: str) -> bool:
        return re.fullmatch(self.value_shape, value) is not None

    def declared_value(self, value: str) -> FacetValueDeclaration | None:
        return next((item for item in self.values if item.value == value), None)


def _require_text(value: Any, field: str, *, max_length: int | None = None) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise RoutingContractError(f"{field} must be a trimmed single-line string")
    if max_length is not None and len(value) > max_length:
        raise RoutingContractError(f"{field} exceeds {max_length} characters")
    return value


def _require_string_items(
    values: tuple[str, ...],
    field: str,
    *,
    max_items: int = MAX_REGISTRY_LIST_ITEMS,
    max_length: int = MAX_REGISTRY_TEXT_LENGTH,
) -> None:
    if len(values) > max_items:
        raise RoutingContractError(f"{field} exceeds {max_items} entries")
    if len(set(values)) != len(values):
        raise RoutingContractError(f"{field} must be unique")
    for value in values:
        _require_text(value, field, max_length=max_length)


def _string_tuple(data: Mapping[str, Any], field: str) -> tuple[str, ...]:
    raw = data.get(field, ())
    if not isinstance(raw, (list, tuple)) or not all(
        isinstance(item, str) for item in raw
    ):
        raise RoutingContractError(f"{field} must be a string array")
    result = tuple(raw)
    _require_string_items(result, field)
    return result


def _value_declaration(data: Mapping[str, Any]) -> FacetValueDeclaration:
    allowed = {"value", "aliases", "parents", "status", "replacement"}
    unknown = set(data) - allowed
    if unknown:
        raise RoutingContractError(
            f"unknown facet value fields: {', '.join(sorted(unknown))}"
        )
    return FacetValueDeclaration(
        value=_require_text(
            data.get("value"), "facet value", max_length=MAX_CUE_TEXT_LENGTH
        ),
        aliases=_string_tuple(data, "aliases"),
        parents=_string_tuple(data, "parents"),
        status=data.get("status", "active"),
        replacement=data.get("replacement"),
    )


@dataclass(frozen=True)
class RegistryResolution:
    facets: Mapping[str, FacetDeclaration]
    namespaces: tuple[str, ...] = ()

    def facet(self, identity: str) -> FacetDeclaration:
        try:
            return self.facets[identity]
        except KeyError as exc:
            raise RoutingContractError(f"undeclared facet: {identity}") from exc


@dataclass(frozen=True)
class RoutingSignature:
    schema_version: SchemaVersion
    cues: tuple[RoutingCue, ...]
    relationships: tuple[RoutingRelationship, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version.value,
            "cues": [cue.to_dict() for cue in self.cues],
            "relationships": [relation.to_dict() for relation in self.relationships],
        }


def _declaration(data: Mapping[str, Any], namespace: str) -> FacetDeclaration:
    allowed = {
        "name",
        "meaning",
        "value_shape",
        "examples",
        "aliases",
        "parents",
        "status",
        "replacement",
        "values",
    }
    unknown = set(data) - allowed
    if unknown:
        raise RoutingContractError(
            f"unknown facet declaration fields: {', '.join(sorted(unknown))}"
        )
    name = data.get("name")
    meaning = data.get("meaning")
    if (
        not isinstance(name, str)
        or len(name) > MAX_CUE_TEXT_LENGTH
        or not _NAME.fullmatch(name)
    ):
        raise RoutingContractError(f"invalid facet name: {name!r}")
    try:
        meaning = _require_text(
            meaning,
            f"facet {name!r} routing meaning",
            max_length=MAX_REGISTRY_TEXT_LENGTH,
        )
    except RoutingContractError as exc:
        raise RoutingContractError(f"facet {name!r} needs a routing meaning") from exc
    value_shape = data.get("value_shape", FacetDeclaration.value_shape)
    if not isinstance(value_shape, str) or not value_shape:
        raise RoutingContractError(
            f"facet {name!r} value_shape must be a non-empty string"
        )
    if len(value_shape) > MAX_VALUE_SHAPE_LENGTH:
        raise RoutingContractError(f"facet {name!r} value_shape is oversized")
    if (
        re.search(r"\(\?", value_shape)
        or re.search(r"\\[1-9]", value_shape)
        or re.search(r"\)[+*{]", value_shape)
    ):
        raise RoutingContractError(f"facet {name!r} value_shape is unsafe")
    try:
        re.compile(value_shape)
    except re.error as exc:
        raise RoutingContractError(f"facet {name!r} has invalid value_shape") from exc
    raw_values = data.get("values", ())
    if not isinstance(raw_values, (list, tuple)) or not all(
        isinstance(item, Mapping) for item in raw_values
    ):
        raise RoutingContractError("facet values must be an object array")
    values = tuple(_value_declaration(item) for item in raw_values)
    if len(values) > MAX_REGISTRY_VALUES:
        raise RoutingContractError(
            f"facet {name!r} exceeds {MAX_REGISTRY_VALUES} values"
        )
    canonical = [item.value for item in values]
    if len(set(canonical)) != len(canonical):
        raise RoutingContractError(f"facet {name!r} has duplicate canonical values")
    aliases = [alias for item in values for alias in item.aliases]
    if len(set(aliases)) != len(aliases) or set(aliases) & set(canonical):
        raise RoutingContractError(f"facet {name!r} has colliding value aliases")
    known_values = set(canonical)
    for item in values:
        if item.replacement is not None and item.replacement not in known_values:
            raise RoutingContractError(
                f"facet {name!r} replacement is not a declared canonical value"
            )
    status = data.get("status", "active")
    if status not in ("active", "deprecated"):
        raise RoutingContractError("facet status must be active or deprecated")
    replacement = data.get("replacement")
    if status == "deprecated" and not replacement:
        raise RoutingContractError("deprecated facets require a replacement")
    if status == "active" and replacement is not None:
        raise RoutingContractError("active facets cannot declare a replacement")
    if replacement is not None:
        _require_text(
            replacement,
            "facet replacement",
            max_length=MAX_CUE_TEXT_LENGTH,
        )
        if not (_NAME.fullmatch(replacement) or _NAMESPACED.fullmatch(replacement)):
            raise RoutingContractError("facet replacement must be a facet identity")
    examples = _string_tuple(data, "examples")
    if any(re.fullmatch(value_shape, example) is None for example in examples):
        raise RoutingContractError(f"facet {name!r} example violates value_shape")
    return FacetDeclaration(
        namespace=namespace,
        name=name,
        meaning=meaning,
        value_shape=value_shape,
        examples=examples,
        aliases=_string_tuple(data, "aliases"),
        parents=_string_tuple(data, "parents"),
        status=status,
        replacement=replacement,
        values=values,
    )


def _validate_registry_lifecycle(facets: Mapping[str, FacetDeclaration]) -> None:
    for facet in facets.values():
        if facet.replacement is not None:
            if facet.replacement == facet.identity:
                raise RoutingContractError("deprecated facet cannot replace itself")
            replacement = facets.get(facet.replacement)
            if replacement is None:
                raise RoutingContractError(
                    f"facet {facet.identity!r} replacement is not declared"
                )
            if replacement.status == "deprecated":
                raise RoutingContractError(
                    f"facet {facet.identity!r} replacement is deprecated"
                )
        values = {item.value: item for item in facet.values}
        for value in facet.values:
            if value.replacement is None:
                continue
            if value.replacement == value.value:
                raise RoutingContractError(
                    "deprecated facet value cannot replace itself"
                )
            replacement_value = values[value.replacement]
            if replacement_value.status == "deprecated":
                raise RoutingContractError(
                    f"facet {facet.identity!r} value replacement is deprecated"
                )


def load_builtin_registry(path: Path | None = None) -> RegistryResolution:
    """Load the shipped registry; the schema remains open to other facets."""
    registry_path = path or Path(__file__).with_name("skill-facets.json")
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping) or data.get("namespace") != "builtin":
        raise RoutingContractError("built-in registry must declare builtin namespace")
    if "$schema" in data and not isinstance(data["$schema"], str):
        raise RoutingContractError("registry $schema must be a string")
    unknown = set(data) - {"$schema", "namespace", "facets"}
    if unknown:
        raise RoutingContractError(
            f"unknown registry fields: {', '.join(sorted(unknown))}"
        )
    declarations = data.get("facets", [])
    if (
        not isinstance(declarations, list)
        or not declarations
        or not all(isinstance(item, Mapping) for item in declarations)
    ):
        raise RoutingContractError("built-in registry must declare facets")
    if len(declarations) > MAX_REGISTRY_FACETS:
        raise RoutingContractError(
            f"built-in registry exceeds {MAX_REGISTRY_FACETS} facets"
        )
    parsed = [_declaration(item, "builtin") for item in declarations]
    if any(len(item.identity) > MAX_CUE_TEXT_LENGTH for item in parsed):
        raise RoutingContractError("facet identity exceeds 64 characters")
    if len({item.identity for item in parsed}) != len(parsed):
        raise RoutingContractError("built-in registry contains duplicate facets")
    facets = {item.identity: item for item in parsed}
    _validate_registry_lifecycle(facets)
    return RegistryResolution(facets=facets, namespaces=("builtin",))


def resolve_registry_overlay(
    declarations: Mapping[str, Any],
    base: RegistryResolution | None = None,
) -> RegistryResolution:
    """Resolve a repository declaration and reject namespace collisions.

    The declaration shape is ``{"namespace": "repo", "facets": [...]}``.
    A repository namespace may only be declared once and cannot be ``builtin``.
    """
    if not isinstance(declarations, Mapping):
        raise RoutingContractError("repository registry must be an object")
    if "$schema" in declarations and not isinstance(declarations["$schema"], str):
        raise RoutingContractError("registry $schema must be a string")
    unknown = set(declarations) - {"$schema", "namespace", "facets"}
    if unknown:
        raise RoutingContractError(
            f"unknown registry fields: {', '.join(sorted(unknown))}"
        )
    namespace = declarations.get("namespace")
    if (
        not isinstance(namespace, str)
        or len(namespace) > MAX_CUE_TEXT_LENGTH
        or not _NAME.fullmatch(namespace)
        or namespace == "builtin"
    ):
        raise RoutingContractError(
            "repository namespace must be a non-builtin identifier"
        )
    if namespace in (base.namespaces if base else ()):
        raise RoutingContractError(f"namespace already declared: {namespace}")
    raw_facets = declarations.get("facets")
    if not isinstance(raw_facets, list) or not raw_facets:
        raise RoutingContractError("repository registry must declare facets")
    if len(raw_facets) > MAX_REGISTRY_FACETS:
        raise RoutingContractError(
            f"repository registry exceeds {MAX_REGISTRY_FACETS} facets"
        )
    result = dict(base.facets if base else {})
    for item in raw_facets:
        if not isinstance(item, Mapping):
            raise RoutingContractError("facet declarations must be objects")
        facet = _declaration(item, namespace)
        if len(facet.identity) > MAX_CUE_TEXT_LENGTH:
            raise RoutingContractError("facet identity exceeds 64 characters")
        if base and facet.name in {
            declaration.name
            for declaration in base.facets.values()
            if declaration.namespace == "builtin"
        }:
            raise RoutingContractError(f"cannot redefine built-in facet: {facet.name}")
        if facet.identity in result:
            raise RoutingContractError(f"facet collision: {facet.identity}")
        result[facet.identity] = facet
    _validate_registry_lifecycle(result)
    return RegistryResolution(
        result, tuple(sorted((*(base.namespaces if base else ()), namespace)))
    )


def normalize_routing_signature(
    data: Mapping[str, Any],
    registry: RegistryResolution | None = None,
) -> RoutingSignature:
    """Validate and deterministically normalize the structured contract."""
    if not isinstance(data, Mapping) or "tags" in data:
        raise RoutingContractError(
            "routing signature must use structured cues, not tags"
        )
    version = data.get("schema_version")
    if version != _SUPPORTED_SCHEMA_VERSION:
        raise RoutingContractError(
            f"schema_version must be {_SUPPORTED_SCHEMA_VERSION}"
        )
    raw_cues = data.get("cues")
    raw_relationships = data.get("relationships")
    if (
        not isinstance(raw_cues, list)
        or not raw_cues
        or not isinstance(raw_relationships, list)
        or not raw_relationships
    ):
        raise RoutingContractError(
            "cues and relationships are required non-empty arrays"
        )
    if len(raw_cues) > MAX_ROUTING_CUES:
        raise RoutingContractError(f"cues exceed {MAX_ROUTING_CUES} entries")
    if len(raw_relationships) > MAX_ROUTING_RELATIONSHIPS:
        raise RoutingContractError(
            f"relationships exceed {MAX_ROUTING_RELATIONSHIPS} entries"
        )
    resolved = registry or load_builtin_registry()
    cues: list[RoutingCue] = []
    for raw in raw_cues:
        if not isinstance(raw, Mapping) or isinstance(raw.get("value"), list):
            raise RoutingContractError(
                "each cue must contain one canonical string value"
            )
        unknown = set(raw) - {"facet", "value", "aliases", "primary"}
        if unknown:
            raise RoutingContractError(
                f"unknown routing cue fields: {', '.join(sorted(unknown))}"
            )
        facet = _require_text(
            raw.get("facet"), "cue facet", max_length=MAX_CUE_TEXT_LENGTH
        )
        value = _require_text(
            raw.get("value"), "cue value", max_length=MAX_CUE_TEXT_LENGTH
        )
        if facet not in resolved.facets:
            if not _NAMESPACED.fullmatch(facet):
                raise RoutingContractError(f"undeclared facet: {facet}")
            raise RoutingContractError(f"undeclared namespace or facet: {facet}")
        declaration = resolved.facet(facet)
        if declaration.status == "deprecated":
            raise RoutingContractError(f"facet is deprecated: {facet}")
        if not declaration.accepts(value):
            raise RoutingContractError(f"value does not match shape for facet {facet}")
        declared_value = declaration.declared_value(value)
        if declaration.values and declared_value is None:
            raise RoutingContractError(f"undeclared canonical value for facet {facet}")
        if declared_value and declared_value.status == "deprecated":
            raise RoutingContractError(
                f"deprecated value {value!r}; use {declared_value.replacement!r}"
            )
        aliases = raw.get("aliases", [])
        if not isinstance(aliases, list) or not all(
            isinstance(alias, str) for alias in aliases
        ):
            raise RoutingContractError("aliases must be a string array")
        if len(set(aliases)) != len(aliases):
            raise RoutingContractError("routing cue aliases must be unique")
        normalized_aliases = tuple(aliases)
        _require_string_items(
            normalized_aliases,
            "routing cue aliases",
            max_items=MAX_ALIASES_PER_CUE,
            max_length=MAX_CUE_TEXT_LENGTH,
        )
        registry_aliases = declared_value.aliases if declared_value else ()
        if len(set((*registry_aliases, *normalized_aliases))) > MAX_ALIASES_PER_CUE:
            raise RoutingContractError(
                f"routing cue aliases exceed {MAX_ALIASES_PER_CUE} entries"
            )
        if value in normalized_aliases or value in registry_aliases:
            raise RoutingContractError("routing cue value cannot alias itself")
        primary = raw.get("primary", False)
        if not isinstance(primary, bool):
            raise RoutingContractError("routing cue primary must be a boolean")
        cues.append(
            RoutingCue(
                facet,
                value,
                tuple(sorted(set((*registry_aliases, *normalized_aliases)))),
                primary,
            )
        )
    cue_identities = [(cue.facet, cue.value) for cue in cues]
    if len(set(cue_identities)) != len(cue_identities):
        raise RoutingContractError("duplicate routing cues are not allowed")
    relationships: list[RoutingRelationship] = []
    for raw in raw_relationships:
        if not isinstance(raw, Mapping) or raw.get("role") not in (
            "owner",
            "support",
            "reference",
        ):
            raise RoutingContractError(
                "relationship role must be owner, support, or reference"
            )
        unknown = set(raw) - {"role", "target", "rationale"}
        if unknown:
            raise RoutingContractError(
                f"unknown routing relationship fields: {', '.join(sorted(unknown))}"
            )
        target = raw.get("target")
        rationale = raw.get("rationale")
        if target is not None:
            _require_text(
                target,
                "relationship target",
                max_length=MAX_RELATIONSHIP_TARGET_LENGTH,
            )
        if rationale is not None:
            _require_text(
                rationale,
                "relationship rationale",
                max_length=MAX_RELATIONSHIP_RATIONALE_LENGTH,
            )
        relationships.append(RoutingRelationship(raw["role"], target, rationale))
    relationship_identities = [
        (item.role, item.target, item.rationale) for item in relationships
    ]
    if len(set(relationship_identities)) != len(relationship_identities):
        raise RoutingContractError("duplicate routing relationships are not allowed")
    if any(cue.primary and cue.facet != "operation" for cue in cues):
        raise RoutingContractError("only operation cues may be primary")
    if any(item.role == "owner" for item in relationships):
        primary = [cue for cue in cues if cue.facet == "operation" and cue.primary]
        if len(primary) != 1:
            raise RoutingContractError(
                "owner skills require exactly one primary operation cue"
            )
    elif any(cue.primary for cue in cues):
        raise RoutingContractError("non-owner skills cannot declare a primary cue")
    cues.sort(key=lambda cue: (cue.facet, cue.value, cue.aliases))
    relationships.sort(
        key=lambda relation: (
            relation.role,
            relation.target or "",
            relation.rationale or "",
        )
    )
    major, minor = (int(part) for part in version.split("."))
    return RoutingSignature(
        SchemaVersion(major, minor), tuple(cues), tuple(relationships)
    )
