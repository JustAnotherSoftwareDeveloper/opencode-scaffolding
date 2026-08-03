# Required Frontmatter

Every `SKILL.md` must open with the current direct-selection profile containing
`name`, `description`, `selection`, and `class`.

```yaml
---
name: <<skill-name>>
description: "Use when <<trigger description>>."
selection:
  role: owner
  tags:
    actions: [<<owned action>>]
    topics: [<<material topic>>]
  use_when: [<<positive request condition>>]
  not_for: [<<nearby request not owned>>]
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

## Selection Profile

- Set `selection.role` to `owner`, `support`, or `reference`.
- Use only grouped tags that materially distinguish the request: `actions`, `inputs`,
  `outputs`, `topics`, `environments`, and `constraints`.
- Add `aliases`, `use_when`, `not_for`, and directional `supports` only when they
  improve direct semantic selection.
- Keep values concise, unique within each group, and request-facing.

## Validation

Run both shared profile validators and Markdown lint on each changed `SKILL.md`.
Validate the complete active inventory so `supports` targets resolve.
