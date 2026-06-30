---
name: todo-writer
description: "Use when writing or replacing todo entries from canonical breakdown-tasks output via the todowrite tool."
tags: [workflow, internal]
class: inline
---

# Todo Writer

Manage todo items through the `todowrite` tool.
The `todowrite` tool performs a **full replacement** of all todo entries.
Send the complete todo array in every call.

## Input

Canonical `breakdown-tasks` JSON output plus caller-provided `status` and `priority`.
The root object must contain only `summary` and `tasks`.
The `tasks` array must contain task objects with `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, and `expectedOutput`.
Task objects may also contain `verification`.
Each item in `tasks` becomes one todo item.
The `tasks[*].purpose` field maps to todo `content`.

## Output

The `todowrite` tool invoked with a `todos` array.
The tool returns success or failure.
No structured output is returned to the caller.

### Todowrite Tool Input Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "todos": {
      "type": "array",
      "minItems": 1,
      "description": "Complete array of todo entries (full replacement -- all entries must be included)",
      "items": {
        "type": "object",
        "properties": {
          "content": {
            "type": "string",
            "minLength": 1,
            "description": "Todo description text; maps from tasks[*].purpose"
          },
          "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed", "cancelled"],
            "description": "Lifecycle status of the todo item"
          },
          "priority": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Priority level of the todo item"
          }
        },
        "required": ["content", "status"]
      }
    }
  },
  "required": ["todos"]
}
```

## Execution Plan

1. Read canonical `breakdown-tasks` JSON output from the input.
2. Verify the root object contains only `summary` and `tasks`.
3. Verify the object contains a non-empty `tasks` array.
4. For each task, extract `purpose` as todo `content`, preserving array order.
5. Apply caller-specified `status` and `priority` to each entry.
6. Collect all entries into a single `todos` array.
7. Invoke the `todowrite` tool once with the complete array.
8. Report completion.

This is a single-pass process.
Invoke `todowrite` exactly once per call.

## Guardrails

- Do not infer `status` or `priority` from context.
  Use only caller-provided values.
- Array order is significant.
  Position in input maps to position in output.
- `content` must be non-empty and drawn verbatim from `tasks[*].purpose`.
  Do not rewrite, summarize, or embellish.
- Reject plaintext packets, bare arrays, single task objects, and non-canonical fields.
- Always send the full `todos` array.
  Partial updates are not supported.
- Validate each entry:
  `status` in {`pending`, `in_progress`, `completed`, `cancelled`};
  `priority` in {`high`, `medium`, `low`}.
