---
name: skill-authoring-guide
description: "Use when authoring or reviewing a readable, discriminative skill selection profile."
selection:
  role: reference
  tags:
    topics:
      - skill selection profiles
      - skill authoring
    outputs:
      - valid skill metadata
  use_when:
    - creating or reviewing direct-selection metadata
  not_for:
    - creating or updating skill implementation files
class: documentation
---

# Skill Authoring Guide

Use this guide to create or review one valid, readable profile for direct semantic
selection. Factory and template maintenance are separate operations.

## Reference Files

- [Frontmatter rules](./reference/frontmatter-rules.md) — Required fields, roles,
  groups, optionals, and bounds.
- [Tagging guide](./reference/tagging-guide.md) — How to write grouped tags, aliases,
  conditions, and supports.
- [Trigger evaluation](./reference/trigger-evaluation.md) — How to test positive,
  negative, and neighboring requests.
- [Authoring style](./reference/authoring-style.md) — Semantic prose forms, headings,
  examples, and discrimination rules for filled content.
- [Skill cross-references](./reference/cross-references.md) — Explicit skill loading
  and the canonical skill-to-document reference syntax.
- [Progressive disclosure](./reference/progressive-disclosure.md) — Compact entry
  points, deterministic conformance evidence, and `TABLE-001`'s narrow exception for
  only the exact fenced `Output Format` example in `display-tasks/SKILL.md` and its
  required single Markdown table renderer output with no surrounding commentary.

Read the relevant reference before editing. Validate the completed profile and examples
with the repository skill validator.
