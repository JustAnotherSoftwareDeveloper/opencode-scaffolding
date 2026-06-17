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
- **Class guidance** — consult `./REFERENCE.md` for taxonomy details
- **Template** — locate the matching template under `./templates/<class>.SKILL.template.md`

## Class / Template Selection

Consult `./REFERENCE.md` for class definitions and decision prompts. Copy the matching template from `./templates/<class>.SKILL.template.md`, then customise.

## Workflow

1. Determine skill name from context or `<name>` in the request.
2. Collect inputs (requirements, archive, source material).
3. Select class per `./REFERENCE.md`; locate template in `./templates/`.
4. Write frontmatter — `name` (matches directory), `description` (starts "Use when"), `class`.
5. Read `./style-guide.md` for editorial conventions before drafting or modifying skill body content.
6. Write a thin procedural body with: trigger guidance, step-by-step workflow, quality rules, validation checklist, expected output. Keep concise. Link to `./REFERENCE.md` and `./templates/` for depth; do not inline reference prose.
7. **For operation skills**: Use "Normalize Input" as the first procedural step (after "When to Use"). This absorbs free-form input, structured packets, files, or tool outputs into one internal procedure input and avoids separate direct/delegated modes.
8. Do not add optional sections (examples, gotchas, extended descriptions).
9. Verify manually — see checklist below.

## Quality Rules

- Frontmatter is valid YAML; description begins with "Use when".
- Body is procedural: steps, conditions, decisions. Not a tutorial or guide.
- Every claim about what the skill does must be derivable from the inputs collected.

## Validation Checklist

Manually verify before finishing:

- `name` in frontmatter matches the directory name under `skills/`
- `description` starts with "Use when" and captures the trigger intent
- `class` is one of operation, delegated, inline, orchestrated, planning (see `./REFERENCE.md`)
- If class is `operation`: "Normalize Input" is the first procedural step; no direct/delegated mode sections present
- Body references `./REFERENCE.md` and/or `./templates/` if applicable, without inlining their content
- No prose copied from archive or templates — original writing
- No examples section present
- All steps are actionable, not descriptive
- Body conforms to `./style-guide.md` (wording, formatting, conciseness, DRY rules)
- Valid YAML frontmatter

## Expected Output

```
skills/<name>/SKILL.md   # Single file — the authored skill
```

The file must be valid, original, and pass manual validation. No other files are produced.