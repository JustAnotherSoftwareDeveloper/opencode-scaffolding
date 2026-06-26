---
name: <<skill-name>>
description: "Use when <<trigger-condition>>."
class: operation
---

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

# <<Skill Name>>

## Normalize Input

Map invocation context to one internal input object.
Define required fields, defaults, and `BLOCKED: <reason>` conditions for missing required input.

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. <<step>>.
2. **Run script: `<script-entry-point>`** —
   Resolve `<scripts-python-dir>` per the global/project-local resolution order (see platform-layout-context.md).
   Invoke via `uv run --directory <scripts-python-dir> <entry-point> <args>`.
   Capture stdout as structured output.
   Parse output and validate against expected schema.
   On non-zero exit, report `BLOCKED: Script failed — <stderr summary>`.
3. <<step>>.
4. <<step>>.
5. <<step>>.

## Self-Validation

Each check is a yes/no assertion.

- <<yes/no check>>.
- <<yes/no check>>.
- <<yes/no check>>.
- [ ] No Markdown tables in filled content (use bullet lists instead).

## Expected Output

Specify: artifact path/location, format, contents, and completeness criteria.
