# Required Frontmatter

Every `SKILL.md` must open with YAML frontmatter containing `name`, `description`, `schema_version`, `cues`, `relationships`, and `class`.

```yaml
---
name: <<skill-name>>
description: "Use when <<trigger description>>."
schema_version: "1.0"
cues:
  - facet: operation
    value: <<primary-owned-operation>>
    primary: true
  - facet: subject
    value: <<material-subject>>
relationships:
  - role: owner
    rationale: <<why-this-skill-owns-the-request>>
class: <<one-of-six-classes>>
---
```

## Name

- Match `name` to the skill directory.
- Use lowercase letters, numbers, and hyphens.
- Keep the name at most 128 characters.
- Keep the name stable after publication.

## Description

- Start an executable skill description with `Use when`.
- Start a planning reference description with `Use as planning reference`.
- Describe trigger intent rather than a feature inventory.
- Keep the description trimmed, single-line, and at most 1024 characters.

## Class

Use exactly one of `operation`, `delegated`, `inline`, `orchestrated`, `planning`, or `documentation`.

## Schema version

Use exactly `schema_version: "1.0"` until a later contract version is implemented and published.
Missing or unknown versions are hard validation failures.

## Routing cues

- Use structured entries with a canonical `value`, resolved `facet`, and optional aliases.
- Declare one primary owned `operation` for every executable owner skill.
- Add the smallest sufficient set of task-grounded cues; optional facets include subject, outcome, interface, environment, and constraint.
- Resolve every non-built-in facet and value through a repository-owned namespaced registry.
- Keep aliases and hierarchy in registry metadata rather than counting them as separate entries.
- Reject undeclared facets, foreign namespaces, collisions, invalid shapes, and cues that fail the routing rubric in `./tagging-guide.md`.
- Enforce the safety ceilings without treating them as targets: at most 32 cues and 32 relationships, with at most 16 aliases per cue.
- Keep cue facets, values, and aliases at most 64 characters; relationship targets at most 128; and rationales at most 256.
- Keep cue values, aliases, relationship targets, and rationales trimmed and on one line.

## Relationships

Represent `owner`, `support`, and `reference` relationships as explicit metadata rather than tag values.

## Validation

Run the same schema and registry validation for authoring, discovery, lexical scoring, and model rendering.
Reject obsolete metadata shapes at the cutover boundary. Report the failed quality test or registry rule.
The machine contracts are `scripts/python/src/lib/shared/skill-routing.schema.json` and `scripts/python/src/lib/shared/skill-facet-registry.schema.json`.
