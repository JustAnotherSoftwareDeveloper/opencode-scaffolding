---
name: skill-writer
description: "Use when creating or updating all OpenCode skill files under skills/<name>/ (SKILL.md, REFERENCE.md, style-guide.md, templates, and reference/) from user requirements, source material, or an archived version."
class: operation
---

# Skill Writer

Write or update skill files under `skills/<name>/`.
Consume user requirements, archived versions, and support files.
Produce a validated skill artifact.

## Normalize Input

1. Determine `<name>` from context or the request.
2. Check existence of `skills/<name>/`.
   - **Does not exist** → mode is CREATE.
   - **Exists** → mode is UPDATE.
3. Gather source material: requirements, reference content, class guidance, template path.
   See `./REFERENCE.md` for class definitions.
4. If an archived version exists under `archive/<name>/SKILL.md`, read for shape only (never prose).
5. Locate the matching template under `./templates/<class>.SKILL.template.md`.

## Procedure

### CREATE Path
Produce a new skill directory from scratch.

1. Select class per `./REFERENCE.md`. Copy the matching template.
2. Write frontmatter: `name`, `description`, `class`.
   Ensure `name` matches directory.
   Ensure `description` starts with "Use when".
3. Read `./style-guide.md` for editorial conventions. Draft body accordingly.
4. Write a thin procedural body with: trigger guidance, step-by-step workflow, quality rules, validation checklist, expected output.
   Link to `./REFERENCE.md` and `./templates/` for depth.
5. For operation skills: "Normalize Input" is the first procedural step, after the H1 intro.
6. Do not add optional sections (examples, gotchas, extended descriptions).
7. Verify manually — see checklist below.

### UPDATE Path
Edit one or more files in an existing skill directory.

1. Read every existing file under `skills/<name>/`: SKILL.md, REFERENCE.md, style-guide.md, templates/*, reference/*.
2. Determine which files the request targets from DETAILS or user instructions.
3. For each targeted file:
   - Read its full current content.
   - Apply targeted edits — do not rewrite the entire file unless explicitly requested.
   - Preserve existing frontmatter, structure, and prose outside the edit scope.
4. If creating a new supporting file (e.g., a new reference or template), write it following conventions from `./style-guide.md` and matching templates.
5. Re-validate all modified files against the checklist below.

## Validation Checklist

**Shared checks (CREATE + UPDATE):**

- `name` in frontmatter matches the directory name under `skills/`
- `description` starts with "Use when"
- `class` is one of operation, delegated, inline, orchestrated, planning (see `./REFERENCE.md`)
- If class is `operation`: "Normalize Input" is the first procedural step
- No general breakdown instructions outside Decompose steps
- Body references `./REFERENCE.md` and/or `./templates/` if applicable, without inlining their content
- No prose copied from archive or templates — original writing
- No examples section present
- All steps are actionable, not descriptive
- Body conforms to `./style-guide.md` (wording, formatting, conciseness, DRY rules)
- Valid YAML frontmatter

**UPDATE-specific checks:**

- Existing content not silently deleted — every edit preserves surrounding context
- Update path references current file content, not assumed content
- Targeted edits are scoped to the request — no unrelated sections modified

## Quality Rules

- Validate frontmatter YAML.
- Ensure `description` begins with "Use when".
- Keep the body procedural: steps, conditions, decisions.
  Omit tutorial explanations.
- Derive every claim from the collected inputs.

## Expected Output

```
skills/<name>/SKILL.md             created (CREATE) or edited (UPDATE)
skills/<name>/REFERENCE.md          created (CREATE) or edited if targeted (UPDATE)
skills/<name>/style-guide.md        created (CREATE) or edited if targeted (UPDATE)
skills/<name>/templates/            created (CREATE) or updated if files targeted (UPDATE)
skills/<name>/reference/            created (CREATE) or updated if files targeted (UPDATE)
```

Passes all validation checklist items.
