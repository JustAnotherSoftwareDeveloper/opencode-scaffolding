---
name: todo-writer
description: "Use when writing or replacing todo entries via the todowrite tool, typically to track progress across delegation packets."
class: inline
---

# Todo Writer

Manage todo items through the `todowrite` tool.
The `todowrite` tool performs a **full replacement** of all todo entries.
Send the complete todo array in every call.

## Input

A set of delegation packets, one per todo item, or a structured description of work items to track.

- **Packet set**: One or more delegation packets (`## PURPOSE`, `## DETAILS`, etc.) where the packet `## PURPOSE` maps to the todo `content` field.
- **Array position**: The position of each packet in the input array determines its mapping to the corresponding todo entry in the output array.

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
            "description": "Todo description text; maps from the ## PURPOSE of a delegation packet"
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

1. Read all delegation packets from the input.
2. For each packet, extract `## PURPOSE` as todo `content`, preserving array order.
3. Apply caller-specified `status` and `priority` to each entry.
4. Collect all entries into a single `todos` array.
5. Invoke the `todowrite` tool once with the complete array.
6. Report completion.

This is a single-pass process.
Invoke `todowrite` exactly once per call.

## Guardrails

- Do not infer `status` or `priority` from context.
  Use only caller-provided values.
- Array order is significant.
  Position in input maps to position in output.
- `content` must be non-empty and drawn verbatim from the packet `## PURPOSE`.
  Do not rewrite, summarize, or embellish.
- Always send the full `todos` array.
  Partial updates are not supported.
- Validate each entry:
  `status` in {`pending`, `in_progress`, `completed`, `cancelled`};
  `priority` in {`high`, `medium`, `low`}.