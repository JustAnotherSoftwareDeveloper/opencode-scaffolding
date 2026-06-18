---
name: display-tasks
description: "Use when rendering task delegation packets as a concise Markdown summary table."
class: inline
---

# Display Tasks

Render one or more delegation packets into a Markdown table with only safe user-facing fields.

## Input

Accepts full delegation packet text. Input may be in either of two formats:

- **Plaintext packets** — One or more delegation packets delimited by `---` containing standard headers (`## PURPOSE`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, etc.).
- **JSON array** — A JSON array of objects, each object conforming to the 8-field camelCase schema produced by the breakdown-tasks skill (fields: `purpose`, `details`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `verification`, `expectedOutput`). A single JSON object (not wrapped in an array) is also accepted and treated as a one-element array.

## Output

A single Markdown table with no surrounding commentary.

### Output Format

```
| Purpose | Files | Skill |
| ------- | ----- | ----- |
| ...     | ...   | ...   |
```

One row per input packet.

## Extraction Rules

### For plaintext (`---`-delimited) packets

1. **Purpose** — Extract the text after `## PURPOSE` on the next non-blank line.
   Truncate to 80 characters if longer.
2. **Files** — Combine `## FILES TO READ` and `## FILES TO WRITE` into a compact, comma-separated list.
   Strip paths to basenames when they share a common prefix.
3. **Skill** — Extract the text after `## SKILLS` on the next non-blank line.
   If empty or absent, render `none`.

### For JSON-origin packets

1. **Purpose** — Extract from the `purpose` field text. Truncate to 80 characters if longer.
2. **Files** — Combine `filesToRead` and `filesToWrite` arrays into a compact, comma-separated list of basenames.
   Strip paths to basenames when they share a common prefix.
3. **Skill** — Extract from the `skills` array and join elements with ", ".
   If empty or absent, render `none`.

## Execution Plan

1. Normalize input —
   a. Detect whether input is valid JSON: if the trimmed input starts with `[` or `{`, attempt JSON parse.
      - If it parses as a JSON array, use each element as a packet object.
      - If it parses as a single JSON object, wrap it in an array (single packet).
   b. Otherwise, split on `---` delimiters to isolate each plaintext delegation packet.
2. Extract fields per [Extraction Rules](#extraction-rules) for each packet.
3. Produce output per [Output Format](#output-format).

## Guardrails

- Never render `## DETAILS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, or `## EXPECTED OUTPUT` in the table body, headers, or any accompanying text.
- Never render full packet bodies — only the extracted columns.
- Never add commentary, summaries, or explanations outside the table.
- Do not own workflow decisions, task state, or delegation logic.
  The delegator decides when to call this skill.
- Do not modify, validate, or execute the packet contents.
  This is a rendering helper only.
- JSON input is parsed as part of input normalization; do not validate or execute packet contents beyond rendering.
