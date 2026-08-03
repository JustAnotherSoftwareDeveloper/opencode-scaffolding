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

Use this guide to author one valid, readable profile for direct semantic selection.
Factory and template maintenance are separate operations.

## Reference Files

- `./reference/frontmatter-rules.md` — Required fields, roles, groups, optionals, and bounds.
- `./reference/tagging-guide.md` — How to write grouped tags, aliases, conditions, and supports.
- `./reference/trigger-evaluation.md` — How to test positive, negative, and neighboring requests.
- `./reference/authoring-style.md` — Prose, headings, examples, and discrimination rules.
- `./reference/progressive-disclosure.md` — How to keep the entry point compact.

Read the relevant reference before editing. Validate the completed profile and examples
with the repository skill validator.
