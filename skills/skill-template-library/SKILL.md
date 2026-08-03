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

This skill is a passive data store for skill-template, schema-index, and snippet-index shared reference content.
It does not auto-read any files when loaded.

## Documentation Files

Read the documentation files listed below as needed for your current task.
The bulleted list provides the mapping of files to their purpose.

- `reference/selection-profile.md` — Field-by-field profile contract and class-role rules.
- `templates/common-workflow.md` — Reference-only workflow documentation template.
- `templates/delegated.SKILL.template.md` — Canonical delegated-class entry-point template.
- `templates/documentation.SKILL.template.md` — Canonical documentation-class entry-point template.
- `templates/inline.SKILL.template.md` — Canonical inline-class entry-point template.
- `templates/operation.SKILL.template.md` — Canonical operation-class entry-point template.
- `templates/orchestrated.SKILL.template.md` — Canonical orchestrated-class entry-point template.
- `templates/planning.SKILL.template.md` — Canonical planning-class entry-point template.
- `schemas/index.md` — Index of the shared metadata shape and class contracts.
- `snippets/index.md` — Index of reusable profile and workflow snippets.

Choose the relevant files based on what you need to learn or reference.
Read only those files.
Do not read every file — read as needed.

## Docs

See the [Documentation Files](#documentation-files) listing above for template descriptions.
See `schemas/index.md` for schema patterns and `snippets/index.md` for code snippets.
