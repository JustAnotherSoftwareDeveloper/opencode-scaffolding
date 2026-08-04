---
name: display-tasks
description: "Use when rendering a reviewed task plan as a concise guidance-oriented Markdown summary."
selection:
  role: owner
  tags:
    actions: [render]
    inputs: [canonical task JSON]
    outputs: [Markdown task summary]
    topics: [task summaries]
  use_when: [canonical task JSON needs a safe user-facing summary]
  not_for: [changing task JSON or executing tasks]
class: inline
---

# Display Tasks

Render the semantically reviewed `breakdown-tasks` output into a concise Markdown
summary. This skill presents the plan; it does not own workflow decisions, task state,
delegation, or execution authority.

## Input

Accept exactly one canonical `breakdown-tasks` JSON object.
The root object must contain only `summary` and `tasks`.
The `tasks` array must contain task objects with `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, and `expectedOutput`.
Task objects may also contain `verification`.
Reject plaintext packets, bare JSON arrays, single task objects, and non-canonical fields.

## Output

Return a short Markdown section with one task summary per item and no raw packet body.
Use these guidance-oriented labels exactly: `Starting files`, `Suggested outputs`, and
`Minimum skills`. The labels describe the initial plan, not exhaustive resource sets.

```markdown
## Tasks

### 1. <purpose>
- Starting files: <filesToRead basenames, or none>
- Suggested outputs: <filesToWrite basenames, or none>
- Minimum skills: <skills, or none>
```

Use one numbered task section per item in `tasks`. Do not imply that listed files or
skills are exhaustive or that suggested outputs are an authorization boundary.

## Extraction Rules

1. **Purpose** — Extract from `tasks[*].purpose`.
   Truncate to 80 characters if longer.
2. **Starting files** — Extract `tasks[*].filesToRead` into a compact comma-separated
   list of basenames. Strip paths to basenames when they share a common prefix.
3. **Suggested outputs** — Extract `tasks[*].filesToWrite` the same way.
4. **Minimum skills** — Extract `tasks[*].skills` and join elements with `,`.
   If empty or absent, render `none`.

## Execution Plan

1. Parse input as JSON.
2. Verify the parsed value is an object with `summary` and `tasks`.
3. Verify `tasks` is a non-empty array.
4. Reject the input with `BLOCKED: display-tasks requires canonical breakdown-tasks JSON output.` if any check fails.
5. Extract fields per [Extraction Rules](#extraction-rules) for each task.
6. Produce output per the guidance-oriented format above.

## Guardrails

- Never render `## DETAILS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, or `## EXPECTED OUTPUT`.
- Never render full packet bodies — only the extracted summary fields.
- Never present files or skills as exhaustive, exact, or workflow-authoritative.
- Do not own workflow decisions, task state, or delegation logic.
  The delegator decides when to call this skill.
- Do not modify or execute the packet contents.
  This is a rendering helper only.
- Do not accept non-canonical packet shapes.
- Do not normalize arrays, single task objects, or plaintext packets.
