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

- `## Docs` section present referencing the skill's reference/README.md.

## Docs

See the generated skill's `reference/README.md` for documentation of supporting files.