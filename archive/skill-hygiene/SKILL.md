---
name: skill-hygiene
description: Use when creating or reviewing OpenCode skills, skill classes, SKILL.md frontmatter, skill trigger descriptions, skill schemas, or skill validation rules.
class: planning
---

# Skill Hygiene

Use this skill when creating, revising, or reviewing skills under `skills/<name>/SKILL.md`.

## Core Workflow

1. Confirm the work really needs a skill: repeated procedure, specialized domain knowledge, or reusable workflow.
2. Choose exactly one class before drafting:
   - `operation` — one bounded procedure with independent validation.
   - `delegated` — worker-executed backing specialist spawned by an orchestrator with explicit input/output contracts.
   - `planning` — proposal, plan, runbook, review, or lifecycle skill.
3. Use OpenCode-compatible frontmatter plus the local framework class:

   ```yaml
   ---
   name: example-skill
   description: Use when ...
   class: operation
   ---
   ```

4. Keep `SKILL.md` concise and procedural. Move long references, schemas, scripts, and checklists into supporting files.
5. Validate and review before reporting success.

## Hygiene Checklist

- `name` is lowercase alphanumeric with single hyphen separators and matches the directory.
- `description` starts with concrete trigger terms and says when to use the skill.
- Near-miss cases are excluded in the description or body.
- The body gives actionable steps, defaults, gotchas, expected outputs, and validation loops.
- Supporting files are referenced only when useful; avoid always-loading long reference dumps.
- Scripts, if any, are non-interactive, safe by default, and have clear inputs, outputs, and failure modes.
- Existing pre-framework skills are not migrated or annotated unless an approved plan says so.

## Class Contracts

The canonical class contracts are XSDs, one per class:

- `schemas/operation.xsd`
- `schemas/delegated.xsd`
- `schemas/planning.xsd`

Markdown guidance is generated on demand from XSD annotations; do not create checked-in markdown class templates or example fixtures.

## Validation Commands

```text
uv run --project scripts/python validate-skill-framework skills/skill-hygiene/SKILL.md
uv run --project scripts/python validate-skill-framework --class-schemas skills/skill-hygiene
uv run --project scripts/python validate-skill-framework --render-markdown operation
uv run --project scripts/python validate-skill-framework --all
```

## References

- `reference/authoring-checklist.md` — detailed authoring and review checklist.
- `reference/description-evals.md` — trigger description eval guidance.
- `reference/script-safety.md` — script and permission safety rules.
