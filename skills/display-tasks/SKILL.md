---
name: display-tasks
description: "Use when rendering canonical breakdown-tasks output as a concise Markdown summary table."
class: inline
---

# Display Tasks

Render canonical `breakdown-tasks` output into a Markdown table with only safe user-facing fields.

## Input

Accept exactly one canonical `breakdown-tasks` JSON object.
The root object must contain only `summary` and `tasks`.
The `tasks` array must contain task objects with `id`, `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, and `expectedOutput`.
Task objects may also contain `dependencies` and `verification`.
Reject plaintext packets, bare JSON arrays, single task objects, and non-canonical fields.

## Output

A single Markdown table with no surrounding commentary.

### Output Format

```
| Purpose | Files | Skill |
| ------- | ----- | ----- |
| ...     | ...   | ...   |
```

One row per item in `tasks`.

## Extraction Rules

1. **Purpose** — Extract from `tasks[*].purpose`.
   Truncate to 80 characters if longer.
2. **Files** — Combine `tasks[*].filesToRead` and `tasks[*].filesToWrite` into a compact, comma-separated list of basenames.
   Strip paths to basenames when they share a common prefix.
3. **Skill** — Extract from `tasks[*].skills` and join elements with `, `.
   If empty or absent, render `none`.

## Execution Plan

1. Parse input as JSON.
2. Verify the parsed value is an object with `summary` and `tasks`.
3. Verify `tasks` is a non-empty array.
4. Reject the input with `BLOCKED: display-tasks requires canonical breakdown-tasks JSON output.` if any check fails.
5. Extract fields per [Extraction Rules](#extraction-rules) for each task.
6. Produce output per [Output Format](#output-format).

## Guardrails

- Never render `## DETAILS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, or `## EXPECTED OUTPUT` in the table body, headers, or any accompanying text.
- Never render full packet bodies — only the extracted columns.
- Never add commentary, summaries, or explanations outside the table.
- Do not own workflow decisions, task state, or delegation logic.
  The delegator decides when to call this skill.
- Do not modify or execute the packet contents.
  This is a rendering helper only.
- Do not accept non-canonical packet shapes.
- Do not normalize arrays, single task objects, or plaintext packets.
