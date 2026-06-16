---
name: todo-writer
description: Use when writing or replacing todo entries via the todowrite tool, typically to track progress across delegation packets.
class: inline
---

# Todo Writer

This skill manages todo items through the `todowrite` tool. The `todowrite` tool performs a **full replacement** of all todo entries -- the complete todo array must always be sent.

## Input

A set of delegation packets, one per todo item, or a structured description of work items to track.

- **Packet set**: One or more delegation packets (`## PURPOSE`, `## DETAILS`, etc.) where the packet `## PURPOSE` maps to the todo `content` field
- **Array position**: The position of each packet in the input array determines its mapping to the corresponding todo entry in the output array

## Output

The `todowrite` tool is invoked with `todos` array. The tool returns success/failure -- no structured output is returned to the caller.

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

## Mapping Convention

When the caller supplies multiple delegation packets alongside this skill:

1. Each packet's `## PURPOSE` maps directly to a todo entry's `content` field.
2. The array position of the packet in the input corresponds to the array position of the todo entry in the output.
3. All packets/todos must be present in a single `todowrite` call -- partial updates are not supported.
4. The caller sets `status` and `priority` on each entry based on context; the skill does not infer these.

## Execution Plan

1. Read all delegation packets provided in the input.
2. For each packet, extract `## PURPOSE` as todo `content`, preserving array order.
3. Apply caller-specified `status` and `priority` to each entry.
4. Collect all entries into a single `todos` array.
5. Invoke the `todowrite` tool once with the complete array.
6. Report completion.

## Guardrails

- Do not infer `status` or `priority` from context unless explicitly instructed. Use caller-provided values.
- Array order is significant: position in the input maps to position in the output.
- `content` must be non-empty and drawn from the packet `## PURPOSE` without rewriting, summarizing, or embellishing.
- Validate each entry: `status` in {`pending`, `in_progress`, `completed`, `cancelled`}; `priority` in {`high`, `medium`, `low`}.