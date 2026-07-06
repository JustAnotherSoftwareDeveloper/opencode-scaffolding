---
name: skill-template-library
description: "Use when referencing skill templates, schemas, or snippets for skill authoring."
tags: [skill-authoring, reference, templates, schemas, snippets, boilerplate]
class: documentation
---

# skill-template-library — Documentation Store

This skill is a passive data store for skill-template, schema-index, and snippet-index shared reference content.
It does not auto-read any files when loaded.

## Documentation Files

Read the documentation files listed below as needed for your current task.
The bulleted list provides the mapping of files to their purpose.

- `templates/common-workflow.md` — Reusable workflow template for documenting a multi-step skill workflow.
- `templates/delegated.SKILL.template.md` — Canonical SKILL.md template for delegated-class skills (single-purpose workers dispatched by orchestration).
- `templates/documentation.SKILL.template.md` — Canonical SKILL.md template for documentation-class skills (passive reference data stores).
- `templates/inline.SKILL.template.md` — Canonical SKILL.md template for inline-class skills (single-pass, no delegation).
- `templates/operation.SKILL.template.md` — Canonical SKILL.md template for operation-class skills (imperative procedures with side effects).
- `templates/orchestrated.SKILL.template.md` — Canonical SKILL.md template for orchestrated-class skills (multi-step, multi-worker coordination).
- `templates/planning.SKILL.template.md` — Canonical SKILL.md template for planning-class skills (domain context reference, no side effects).
- `schemas/index.md` — Reference for per-skill schema patterns and class-contract documentation (see also `skills/skill-architect/class-taxonomy.md`).
- `snippets/index.md` — Index of reusable code blocks (frontmatter YAML, collation JSON, delegation packet template) for use by templates.

Choose the relevant files based on what you need to learn or reference.
Read only those files.
Do not read every file — read as needed.

## Docs

See the [Documentation Files](#documentation-files) listing above for template descriptions.
See `schemas/index.md` for schema patterns and `snippets/index.md` for code snippets.
