---
name: <<skill-name>>
description: "Use when <<trigger condition>>."
class: inline
---

# <<Skill Name>>

One-line summary of what this inline skill accomplishes in a single pass.

## Input

Free-form prompt or structured input expected by this skill.

- **<<field>>**: <<description>>
- **<<field>>**: <<description>>

## Output

Concrete description of what this skill produces and in what format.

### Output Format

<<Format description with inline code, bullet lists, or schema references as appropriate.>>

```
<<template or example of output>>
```

<<Optional: Additional domain-specific section between Output and Execution Plan.>>

## Execution Plan

1. <<Step 1>> — see [Input](#input).
2. <<Step 2>> — see [<<Section Reference>>](#<<section-reference>>).
3. <<Step 3>> — produce output per [Output](#output).

This is a single-pass process. Do not delegate, loop, or perform multi-phase orchestration.

## Guardrails

- <<guardrail 1>>
- <<guardrail 2>>
- <<guardrail 3>>

## Self-Validation

- `## Docs` section present with links and descriptions for all supporting files within the skill folder.

## Docs

See the generated skill's `reference/`, `templates/`, `schemas/`, and `snippets/` directories for supporting documentation.
- `./reference/frontmatter-rules.md` — Class taxonomy and frontmatter field rules
- `./reference/platform-context.md` — Platform context where skills live
- `./reference/progressive-disclosure.md` — Pushing detail to reference files
- `./reference/trigger-eval.md` — Description composition eval
- `./reference/validation-checklist.md` — Skill verification checklist
- `./reference/gotchas.md` — Common pitfalls
- `./reference/update-workflow.md` — UPDATE mode reference
- `./templates/inline.SKILL.template.md` — This template
- `./schemas/class-contract.example.json` — Example JSON Schema for class contracts
- `./schemas/class-contract.example.xsd` — Example XSD for class contracts
- `./snippets/README.md` — Reusable code snippets
- `./style-guide.md` — Editorial conventions