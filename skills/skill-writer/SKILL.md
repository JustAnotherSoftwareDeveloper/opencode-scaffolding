---
name: skill-writer
description: "Use when creating or rewriting an OpenCode skill (SKILL.md) from user requirements, source material, or an archived version."
class: operation
---

# Skill Writer

Writes a single `skills/<name>/SKILL.md`. This skill is procedural, not documentary. It consumes user requirements, archived versions, and support files, and produces a validated skill artifact.

## Inputs to Collect

Before writing, gather:

- **Purpose** — one-sentence intent for the skill
- **Source material** — any reference content, workflows, or specifications the skill must encode
- **Archived version** (if any) — prior iteration under `archive/<name>/SKILL.md`; read for shape only, not prose
- **Class guidance** — consult `REFERENCE.md` (when it exists) for taxonomy details
- **Template** — locate the matching template under `templates/<class>.SKILL.template.md`

## Class / Template Selection

Pick exactly one class. If uncertain, pause and read `REFERENCE.md`.

- **operation** — single bounded procedure, independent, no sub-delegation
- **delegated** — worker specialization, designed to receive delegation packets
- **orchestrated** — coordinates subskills or workers across phases
- **planning** — proposal/plan/runbook lifecycle

Copy the matching template (`templates/<class>.SKILL.template.md`) from `templates/`, then customise.

## Workflow

1. Determine skill name from context or `<name>` in the request.
2. Collect inputs (requirements, archive, source material).
3. Select class; locate template in `templates/`.
4. Write frontmatter — `name` (matches directory), `description` (starts "Use when"), `class`.
5. Write a thin procedural body with: trigger guidance, step-by-step workflow, quality rules, validation checklist, expected output. Keep concise. Link to `REFERENCE.md` and `templates/` for depth; do not inline reference prose.
6. Do not add optional sections (examples, gotchas, extended descriptions).
7. Verify manually — see checklist below.

## Quality Rules

- No prose copied from archived versions — shape only.
- Frontmatter is valid YAML; description begins with "Use when".
- Body is procedural: steps, conditions, decisions. Not a tutorial or guide.
- References to `REFERENCE.md` and `templates/` are forward-looking (they will exist after later tasks).
- No optional examples or extended commentary.
- Every claim about what the skill does must be derivable from the inputs collected.

## Validation Checklist

Manually verify before finishing:

- `name` in frontmatter matches the directory name under `skills/`
- `description` starts with "Use when" and captures the trigger intent
- `class` is one of: operation, delegated, orchestrated, planning
- No prose copied from archive or templates — original writing
- Body references `REFERENCE.md` and/or `templates/` if applicable, without inlining their content
- No examples section present
- All steps are actionable, not descriptive

## Expected Output

```
skills/<name>/SKILL.md   # Single file — the authored skill
```

The file must be valid, original, and pass manual validation. No other files are produced.