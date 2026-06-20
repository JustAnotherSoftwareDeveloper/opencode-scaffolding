---
name: skill-writer
description: "Use when creating or updating all OpenCode skill files under skills/<name>/ (SKILL.md, style-guide.md, templates/, reference/, schemas/, and snippets/) from user requirements, source material, or an archived version."
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
   See `./reference/frontmatter-rules.md` for class definitions and `./reference/platform-context.md` for platform rules.
4. If an archived version exists under `archive/<name>/SKILL.md`, read for shape only (never prose).
5. Locate the matching template under `./templates/<class>.SKILL.template.md`.

## Procedure

### CREATE Path
Produce a new skill directory from scratch.

1. Select class per `./reference/frontmatter-rules.md`. Copy the matching template.
2. Write frontmatter: `name`, `description`, `class`.
   Ensure `name` matches directory.
   Ensure `description` starts with "Use when".
3. Read `./style-guide.md` for editorial conventions. Draft body accordingly.
4. Write a thin procedural body with: trigger guidance, step-by-step workflow, quality rules, validation checklist, expected output.
   Link to `./reference/` and `./templates/` for depth.
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
- `class` is one of operation, delegated, inline, orchestrated, planning (see `./reference/frontmatter-rules.md`)
- If class is `operation`: "Normalize Input" is the first procedural step
- No general breakdown instructions outside Decompose steps
- Body references `./reference/` and/or `./templates/` if applicable, without inlining their content
- No prose copied from archive or templates — original writing
- No examples section present
- All steps are actionable, not descriptive
- Body conforms to `./style-guide.md` (wording, formatting, conciseness, DRY rules)
- Valid YAML frontmatter
- Generated skill includes a `## Docs` section at the bottom with relative links and brief descriptions for each supporting document (reference/*, templates/, schemas/, snippets/). No links to files outside the skill's own folder.

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
- Generated skill must have a `## Docs` section at the bottom with links+descriptions for all supporting files within its folder.

## Expected Output

```
skills/<name>/SKILL.md             created (CREATE) or edited (UPDATE)
skills/<name>/style-guide.md        created (CREATE) or edited if targeted (UPDATE)
skills/<name>/templates/            created (CREATE) or updated if files targeted (UPDATE)
skills/<name>/reference/            created (CREATE) or updated if files targeted (UPDATE)
skills/<name>/schemas/              created (CREATE) or updated if files targeted (UPDATE)
skills/<name>/snippets/             created (CREATE) or updated if files targeted (UPDATE)
```

Passes all validation checklist items.

## Docs

- `./reference/frontmatter-rules.md` — Class taxonomy, frontmatter field rules (includes planning skill authoring guidance formerly in skill-architect, now deprecated)
- `./reference/platform-context.md` — Where skills live, discovery mechanism
- `./reference/progressive-disclosure.md` — Pushing detail to reference files
- `./reference/trigger-eval.md` — Description composition with positive/near-miss eval
- `./reference/validation-checklist.md` — Manual checklist for skill verification
- `./reference/gotchas.md` — Common pitfalls
- `./reference/update-workflow.md` — UPDATE mode detail
- `./reference/orchestrated-usage.md` — 7-section template walkthrough
- `./reference/collation-reference.md` — Collation JSON shape
- `./reference/worker-patterns.md` — Delegated worker patterns
- `./reference/migration-from-old-template.md` — Old template migration
- `./templates/operation.SKILL.template.md` — Operation class template
- `./templates/delegated.SKILL.template.md` — Delegated class template
- `./templates/inline.SKILL.template.md` — Inline class template
- `./templates/orchestrated.SKILL.template.md` — Orchestrated class template
- `./templates/planning.SKILL.template.md` — Planning class template
- `./schemas/class-contract.example.json` — Example JSON Schema for class contracts
- `./schemas/class-contract.example.xsd` — Example XSD for class contracts
- `./snippets/README.md` — Reusable code snippet index
- `./style-guide.md` — Editorial conventions
