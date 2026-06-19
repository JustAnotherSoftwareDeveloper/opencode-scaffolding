---
name: skill-writer
description: "Use when creating or rewriting an OpenCode skill (SKILL.md) from user requirements, source material, or an archived version."
class: operation
---

# Skill Writer

Write a single `skills/<name>/SKILL.md`.
Consume user requirements, archived versions, and support files.
Produce a validated skill artifact.

## Inputs to Collect

Gather:

- **Purpose** — define a one-sentence intent for the skill
- **Source material** — any reference content, workflows, or specifications the skill must encode
- **Archived version** (if any) — locate under `archive/<name>/SKILL.md`.
  Read for shape only, not prose.
- **Class guidance** — consult `./REFERENCE.md` for taxonomy details
- **Template** — locate the matching template under `./templates/<class>.SKILL.template.md`

## Class / Template Selection

Consult `./REFERENCE.md` for class definitions and decision prompts.
Copy the matching template from `./templates/<class>.SKILL.template.md`.
Customise it.
For orchestrated skills, use the canonical template at `orchestrated.SKILL.template.md`.

## Workflow

1. Determine skill name from context or `<name>` in the request.
2. Collect inputs (requirements, archive, source material).
3. Select class per `./REFERENCE.md`.
   Locate template in `./templates/`.
4. Write frontmatter: `name`, `description`, `class`.
   Ensure `name` matches the directory.
   Ensure `description` starts with "Use when".
5. Read `./style-guide.md` for editorial conventions.
   Draft skill body content accordingly.
6. Write a thin procedural body with: trigger guidance, step-by-step workflow, quality rules, validation checklist, expected output.
   Link to `./REFERENCE.md` and `./templates/` for depth.
   - **For orchestrated skills**: follow the canonical template.
7. **For operation skills**: use "Normalize Input" as the first procedural step, after "When to Use".
   See `./REFERENCE.md` for rationale.
8. Do not add optional sections (examples, gotchas, extended descriptions).
9. Verify manually — see checklist below.

## Quality Rules

- Validate frontmatter YAML.
- Ensure `description` begins with "Use when".
- Keep the body procedural: steps, conditions, decisions.
  Omit tutorial explanations.
- Derive every claim from the collected inputs.
- **For orchestrated skills**: prefix Execution Steps with typed prefixes (Delegated, Inline, Decompose, Verify).
  See `./REFERENCE.md` for definitions.

## Validation Checklist

- `name` in frontmatter matches the directory name under `skills/`
- `description` starts with "Use when".
- `class` is one of operation, delegated, inline, orchestrated, planning (see `./REFERENCE.md`)
- If class is `planning`: template includes When to Use and Verification Criteria sections.
- If class is `operation`: "Normalize Input" is the first procedural step.
  No direct/delegated mode sections.
- If class is `orchestrated`: verify 7-section canonical layout and correct step prefixes.
  See `./REFERENCE.md` for exact section list.
- No general breakdown instructions outside Decompose steps.
- Body references `./REFERENCE.md` and/or `./templates/` if applicable, without inlining their content
- No prose copied from archive or templates — original writing
- No examples section present
- All steps are actionable, not descriptive
- Body conforms to `./style-guide.md` (wording, formatting, conciseness, DRY rules)
- Valid YAML frontmatter

## Expected Output

```
skills/<name>/SKILL.md
```

Passes all validation checklist items.