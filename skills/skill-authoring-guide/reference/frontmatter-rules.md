# Selection Profile Fields

Every `SKILL.md` begins with YAML frontmatter containing exactly the required fields
`name`, `description`, `selection`, and `class`, plus only supported optional fields.

```yaml
---
name: example-skill
description: "Use when producing a specific result for a specific request."
selection:
  role: owner
  tags:
    actions: [produce]
    inputs: [source material]
    outputs: [validated result]
    topics: [target subject]
    environments: [repository]
    constraints: [deterministic]
  use_when:
    - the request matches the owned operation
  not_for:
    - the request belongs to a neighboring skill
  supports: [related-skill]
class: operation
---
```

## Required Fields

- `name` matches the directory and uses lowercase letters, numbers, and hyphens.
- `description` is one trimmed, single-line trigger statement of at most 1024 characters.
- `selection.role` is `owner`, `support`, or `reference`.
- `selection.tags` contains at least one non-empty group.
- `class` is one of `operation`, `delegated`, `inline`, `orchestrated`, `planning`, or `documentation`.

## Roles

- Use `owner` when the skill directly fulfills the request.
- Use `support` when the skill contributes a bounded capability to another skill.
- Use `reference` when the skill supplies guidance or context and does not own execution.

Do not use relationships, cues, facets, routing fields, or `schema_version`. Those
fields are obsolete and fail validation. Do not add empty groups or empty optional
arrays.

## Optional Fields

Use `version`, `license`, `compatibility`, `metadata`, and `permission` only when the
profile needs them. Preserve authored list order. `supports` contains canonical skill
names, excludes the current skill, and must resolve during full inventory validation.

Each string is trimmed and single-line. Arrays contain 1–32 unique items; ordinary
text is at most 128 characters, descriptions 1024, and other optional text 256.
