# Skill-routing hard-cutover verification

**Release decision: PASS — the routing metadata hard cutover is complete.**

This verification was rerun after resolving the initial release-gate failures and completing a second security, lifecycle, distribution, and boundary audit.

## Release evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Full Python test suite | **PASS** | `uv run pytest -q --tb=short`: 661 passed, 3 skipped; coverage 89.99%, above the 85% gate. |
| Python lint and types | **PASS** | Ruff passed for `src` and `tests`; Pyright reported 0 errors, warnings, or information messages. |
| Distribution build | **PASS** | Source and wheel builds succeeded; the wheel contains both schemas and the built-in facet registry. |
| Built-in inventory | **PASS** | `collect-skills` discovered all 26 `skills/*/SKILL.md` entries. |
| Authoring metadata validation | **PASS** | `validate-skill-meta` accepted all 26 built-in skills. |
| Skill-validator routing check | **PASS** | The `frontmatter-valid` check accepted all 26 built-in skills. |
| Legacy frontmatter audit | **PASS** | Active Markdown contains no `tags:` frontmatter, and production Python contains no flat-tag metadata reads or writes. |
| Manifest identity | **PASS** | Manifest files and validation code require `task-skill-routing-signature-v2`; the old version remains only in a deliberate rejection test. |
| Representative task generation | **PASS** | Lexical `generate-task-json` completed with structured inventory and selected `skill-script-python-test-writer` plus `skill-script-python-writer`. |
| Cross-domain routing evaluation | **PASS** | `pytest -q --no-cov tests/test_skill_routing_evaluation.py`: 5 passed. |
| Diff integrity | **PASS** | `git diff --check` completed without errors. |

## Resolved blockers

- Updated the stale production manifest pin from `task-skill-fields-v1` to `task-skill-routing-signature-v2`.
- Rejected duplicate aliases and duplicate facet/value cues instead of silently normalizing them.
- Corrected skill-validator scalar checks so structured `cues` and `relationships` are validated as arrays.
- Migrated the two remaining built-in frontmatters and three active valid fixtures to `schema_version`, `cues`, and `relationships`.
- Updated renderer, manifest, validator, and module-guard tests for the authoritative hard-cut contract.
- Removed stale compatibility wording and corrected active authoring guidance that still showed `tags:`.
- Reconciled the evaluation report to ten cases across nine case families.
- Re-ran task generation from a caller-local output directory, satisfying the CLI output boundary.

## Extensive audit follow-up

- Made schema version `1.0` explicit and mandatory instead of silently defaulting or accepting unknown versions.
- Added and validated a machine-readable facet-registry schema alongside the routing-signature schema.
- Aligned Python and JSON Schema rules for canonical facet names, non-empty arrays, unique entries, trimmed single-line values, and unknown-field rejection.
- Added optional canonical value registries with aliases, hierarchy, deprecation status, and required replacements.
- Made registry alias expansion idempotent across discovery, inventory serialization, lexical scoring, and Qwen candidate construction.
- Rejected malformed regular expressions, duplicate facets, colliding aliases, undeclared values, invalid replacements, duplicate relationships, non-boolean primary markers, and primary cues on non-owner or non-operation metadata.
- Bounded registry discovery at the Git root and rejected ambiguous multiple registry files at one scope.
- Restored authoring/discovery parity for class validity and class-specific description prefixes.
- Removed the obsolete tag-frequency compatibility API from `validate-skill-meta`.
- Made malformed repository registries return validation errors rather than unhandled failures.
- Ensured repository-local facets are resolved only after candidate paths pass source-root authorization.
- Hardened Qwen rendering against empty, malformed, multiline, or incorrectly typed candidate fields.
- Updated planning fixtures to model planning skills as references rather than executable owners.
- Replaced a deprecated jsonschema format-checker API and cleared lint and type-check failures.
- Added authoritative count and length ceilings for candidate inventories, routing cues, aliases, relationships, registry facets, registry values, names, descriptions, and free-text fields.
- Rejected unsafe repository `value_shape` expressions that use lookarounds, backreferences, or quantified groups, preventing pathological regex backtracking.
- Required deprecated facets and values to point directly to declared active replacements; rejected self-replacements, deprecated chains, and replacements on active entries.
- Hardened supplied lexical inventories against malformed names, unsafe descriptions, invalid classes, duplicate names, and excessive candidate counts.
- Prevented raw Qwen prompt composition from accepting reserved control-token prefixes in instructions, queries, or documents.
- Prevented registry discovery from climbing ancestor directories when no Git repository boundary exists.
- Verified schema/runtime parity for registry meanings, value shapes, schema declarations, lifecycle fields, and safety bounds.

## Scope note

The routing release gate uses the metadata-specific `frontmatter-valid` check from `skill-validator` for all built-ins. Other general style and reference checks are separate skill-maintenance concerns and are not evidence of routing compatibility or cutover status.

## Final identity

- Routing schema version: `1.0`
- Task render version: `task-skill-routing-signature-v2`
- Planning render version: `planning-routing-signature-v2`
- Built-in inventory: 26 skills
- Cross-domain fixture: 6 candidates, 10 cases, 9 case families, including repository-local `orchard:crop-stage`

The repository now has one authoritative structured routing-signature path with no production flat-tag compatibility layer.
