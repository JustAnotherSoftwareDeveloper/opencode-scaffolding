---
name: skill-writer
description: Use when creating or authoring OpenCode skills (SKILL.md files), implementing the framework's skill-hygiene conventions for operation, delegated, or planning class artifacts.
class: operation
---

# Skill Writer Skill

Use this skill when you need to write a new OpenCode skill artifact at `skills/<name>/SKILL.md` following the framework's hygiene conventions and structure expectations.

## Trigger Terms

Load `skill-writer` when:
- Creating a brand-new skill for repeated procedures, specialized knowledge, or workflow automation
- Documenting reference material that other skills will load via delegation
- The work requires a class-specific template (operation, delegated, or planning)
- You need to validate frontmatter structure before finalizing

Do **not** use for:
- Fixing bugs in existing application code
- Running one-off shell commands outside the harness
- Editing configuration files that aren't OpenCode skills

## Core Workflow

1. **Choose a class**: Select exactly one from `operation`, `delegated`, or `planning`. See `reference/class-selection.md` for decision guidance.
2. **Use appropriate template**: Copy the matching template from `templates/<class>-skill-template.md` to start.
3. **Author frontmatter**: Fill in name (directory-matched), description ("Use when..." trigger), and class only—these are required.
4. **Write procedural body**: Keep it concise with When/Why first, then actionable steps. Link to `templates/` and `reference/` for detail.
5. **Validate**: Run `uv run --project scripts/python validate-skill-framework skills/skill-writer/SKILL.md`.

## Templates Directory (`templates/`)

Each template contains a description of the skill class purpose followed by a structured markdown file with frontmatter ready to copy-and-customize:

| Template | Purpose |
|----------|---------|
| `operation-skill-template.md` | Single bounded procedure with independent validation; operation class |
| `delegated-skill-template.md` | Worker specialization for isolated execution via delegation packet |
| `planning-skill-template.md` | Proposal/plan/runbook lifecycle creation |

## Reference Directory (`reference/`)

Curated materials referenced from SKILL.md:

- `authoring-workflow.md` — Condensed checklist for skill authoring
- `class-selection.md` — Trigger patterns and class decision guide  
- `reference-docs.md` — Links to full schema definitions in harness

Read these when you need detail; keep them out of the main SKILL.md body.

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Validation fails on frontmatter | Ensure name matches directory, description starts with "Use when", no tabs in YAML block |
| Uncertainty about class selection | Review `reference/class-selection.md` or load `skill-hygiene` for the taxonomy |
| Template feels wrong for use case | It's okay to combine elements; validation only requires valid frontmatter and a body |

## Examples Directory (`examples/`)

Real-world examples demonstrating successful skill creation using the templates. Each example shows a complete, validated implementation that can be referenced or adapted:

| Example | Purpose |
|---------|---------|
| `examples/operation-example.md` | Demonstrates operation class for single bounded procedure with independent validation (e.g., schema checking) |
| `examples/delegated-example.md` | Shows worker specialization loaded via delegation packet for isolated execution |
| `examples/planning-example.md` | Illustrates proposal→plan→runbook lifecycle creation with acceptance criteria mapping |

## Expected Output

When complete, you should have:

```text
skills/<name>/SKILL.md        # The authored skill (validated)
skills/<name>/templates/      # Optional: class templates used as reference
skills/<name>/reference/      # Optional: curated checklists for others
skills/<name>/examples/       # Optional: working examples demonstrating usage
```

## Validation

Verify with:

```bash
uv run --project scripts/python validate-skill-framework skills/skill-writer/SKILL.md
# Or on a new skill:
uv run --project scripts/python validate-skill-framework skills/<name>/SKILL.md
```
