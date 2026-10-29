---
name: skill-template-library
description: "Use when referencing skill templates, schemas, or snippets for skill authoring."
selection:
  role: reference
  tags:
    actions: [reference, scaffold, select]
    inputs: [skill requirements, source material]
    outputs: [selection profile, skill scaffold]
    topics: [skill authoring, templates, schemas, snippets]
    environments: [OpenCode]
    constraints: [documentation-only, canonical examples]
  use_when: [an author needs a class-aware skill profile or canonical template]
  not_for: [executing a skill workflow, maintaining an existing skill, assigning task skills]
  supports: [skill-factory]
class: documentation
---

# skill-template-library — Documentation Store

This skill provides passive, shared skill-authoring references, including templates, schemas, and snippets. Loading it does not read any files automatically.

## Documentation Files

Read only the files relevant to your task; each entry describes its purpose.

- `reference/selection-profile.md` — Field-by-field profile contract and class-role rules.
- `templates/common-workflow.md` — Reference-only workflow documentation template.
- `templates/delegated.SKILL.template.md` — Canonical delegated-class entry-point template.
- `templates/documentation.SKILL.template.md` — Canonical documentation-class entry-point template.
- `templates/inline.SKILL.template.md` — Canonical inline-class entry-point template.
- `templates/operation.SKILL.template.md` — Canonical operation-class entry-point template.
- `templates/planning.SKILL.template.md` — Canonical planning-class entry-point template.
- `schemas/index.md` — Index of the shared metadata shape and class contracts.
- `snippets/index.md` — Index of reusable profile and workflow snippets.

## Docs

See the [Documentation Files](#documentation-files) above for file descriptions.
See `schemas/index.md` for schema patterns and `snippets/index.md` for code snippets.
