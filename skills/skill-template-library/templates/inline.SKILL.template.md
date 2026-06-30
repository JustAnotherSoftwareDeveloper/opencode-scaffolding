---
name: <<skill-name>>
description: "Use when <<trigger condition>>."
class: inline
---

# `<<Skill Name>>`

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

One-line summary of what this inline skill accomplishes in a single pass.

## Input

Free-form prompt or structured input expected by this skill.

- **`<<field>>`**: `<<description>>`
- **`<<field>>`**: `<<description>>`

## Output

Concrete description of what this skill produces and in what format.

### Output Format

<<Format description with inline code, bullet lists, or schema references as appropriate.>>

```text
<<template or example of output>>
```

<<Optional: Additional domain-specific section between Output and Execution Plan.>>

## Execution Plan

1. <<Step 1>> — see [Input](#input).
2. If the step involves deterministic data processing, delegate to a script:
   Load `skill-architect` for path resolution rules per the global/project-local resolution order.
   - **Python script:** `uv run --directory <scripts-python-dir> <entry-point> <args>`
   - **Node script:** `bun run --cwd <scripts-node-dir> <entry-point> [args]`
   Incorporate script output into the reasoning context.
3. <<Step 2>> — see [Output Format](#output-format).
4. <<Step 3>> — produce output per [Output](#output).

This is a single-pass process.
Do not loop or perform multi-phase orchestration.

## Guardrails

- <<guardrail 1>>
- <<guardrail 2>>
- <<guardrail 3>>

## Cross-References

- Load `skill-architect` for path resolution rules for script invocations within this skill.

## Self-Validation

- Name matches directory name.
- Description starts with "Use when".
- Class is `inline`.
- All `<<placeholders>>` are replaced.
- No remaining old-template sections.
- [ ] No Markdown tables in filled content (use bullet lists instead).

## Docs

See the [Skill Template Library](./) for the canonical template set and its documentation.
