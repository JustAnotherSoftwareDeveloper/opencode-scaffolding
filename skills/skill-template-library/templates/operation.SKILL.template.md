---
name: <<skill-name>>
description: "Use when <<trigger-condition>>."
schema_version: "1.0"
cues:
  - {facet: operation, value: "<<owned-operation>>", primary: true}
  - {facet: subject, value: "<<task-subject>>"}
  - {facet: outcome, value: "<<task-outcome>>"}
relationships:
  - {role: owner, rationale: "<<ownership rationale>>"}
class: operation
---

# `<<Skill Name>>`

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

## Normalize Input

Map invocation context to one internal input object.
Define required fields, defaults, and `BLOCKED: <reason>` conditions for missing required input.

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. `<<step>>`.
2. **Run script: `<script-entry-point>`** —
   Load `skill-architect` for path resolution rules per the global/project-local resolution order.
   - **Python script:** `uv run --directory <scripts-python-dir> <entry-point> <args>`
   - **Node script:** `bun run --cwd <scripts-node-dir> <entry-point> [args]`
   Capture stdout as structured output.
   Parse output and validate against expected schema.
   On non-zero exit, report `BLOCKED: Script failed — <stderr summary>`.
3. `<<step>>`.
4. `<<step>>`.
5. `<<step>>`.

## Self-Validation

Each check is a yes/no assertion.

- <<yes/no check>>.
- <<yes/no check>>.
- <<yes/no check>>.
- [ ] No Markdown tables in filled content (use bullet lists instead).

## Expected Output

Specify: artifact path/location, format, contents, and completeness criteria.
