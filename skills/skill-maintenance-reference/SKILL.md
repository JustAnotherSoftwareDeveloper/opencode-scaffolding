---
name: skill-maintenance-reference
description: "Use when referencing maintenance workflows, migration procedures, validation checks, or known pitfalls for skill maintenance."
schema_version: "1.0"
cues:
  - {facet: subject, value: "skill maintenance"}
  - {facet: outcome, value: "maintenance guidance"}
  - {facet: constraint, value: "migration validation"}
relationships:
  - {role: reference, rationale: "provides passive maintenance procedures"}
class: documentation
---

# skill-maintenance-reference — Documentation Store

This skill is a passive data store for maintenance-related reference content.
It does not auto-read any files when loaded.

## Documentation Files

Read the documentation files listed below as needed for your current task.
The bulleted list provides the mapping of files to their purpose.

- `update-workflow.md` — Defines the update workflow reference, including mode determination, scope boundaries, and content integrity rules for editing existing skill directories.
- `migration-guide.md` — Provides migration procedures from the old monolithic skill-writer structure to the decomposed skill layout, including section mapping and checklist.
- `validation-checklist.md` — Lists validation and manual checklist items every authored skill must pass before being declared done.
- `gotchas.md` — Catalogues common pitfalls, mistakes, and edge cases encountered during skill authoring and maintenance.

Choose the relevant files based on what you need to learn or reference.
Read only those files.
Do not read every file — read as needed.

## Docs

See `./update-workflow.md`, `./migration-guide.md`, `./validation-checklist.md`, and `./gotchas.md` for the full reference documentation.
