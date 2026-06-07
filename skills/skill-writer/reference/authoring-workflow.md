# Skill Authoring Workflow

Condensed checklist for creating new OpenCode skills following skill-hygiene conventions.

## Scope Validation

Before drafting, confirm the work addresses:
- Repeated procedures or specialized domain knowledge (not one-off tasks)
- One clear primary job with explicit non-goals
- Class selection that matches actual behavior

**Class reference:** `reference/class-selection.md`

## Frontmatter Requirements

| Field | Requirement |
|-------|-------------|
| `name` | Matches `skills/<name>/` exactly, lowercase alphanumeric with hyphens |
| `description` | Starts with "Use when", specific and under 1024 characters |
 | `class` | One of: `atomic`, `orchestrated`, `documentation`, or `planning` |

## Body Structure (Procedural)

Follow this minimum structure:

1. **When to use** — Clear trigger condition for loading the skill
2. **Key steps/workflow** — Actionable, imperative instructions  
3. **Validation** — How success is verified
4. **Gotchas & recovery** — Common failure modes with solutions

## Progressive Disclosure

- Keep `SKILL.md` compact (< 100 lines for most skills)
- Move long references to `reference/` subdirectory
- Link supporting files by relative path and document when to read them

> See `skill-hygiene/reference/authoring-checklist.md` for full details.

## Review & Test

- [ ] Positive trigger: skill loads correctly for intended requests  
- [ ] Near-miss negative: skill does NOT load for unrelated work
- [ ] Validate structure: `uv run --project scripts/python validate-skill-framework skills/<name>/SKILL.md`