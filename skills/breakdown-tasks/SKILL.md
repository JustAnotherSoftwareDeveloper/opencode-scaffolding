---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items. Separates planning from execution: the LLM decomposes, the script assigns skills."
tags: [workflow, tasking, task-decomposition, task-planning, request-analysis, atomic-tasks]
class: delegated
---

# Breakdown Tasks — Delegated Worker

Decompose a request into atomic work items suitable for serial worker delegation.
Produce `TaskDraft` objects without a `skills` field.

## Input Contract

Read `## PURPOSE` and `## DETAILS`.
Return `BLOCKED: missing PURPOSE or DETAILS` if either section is missing.

## Execution Steps

1. Read `./schema/task-input.schema.json`.
2. Read `./reference/authoring/core-rules.md`, `./reference/authoring/task-granularity.md`, `./reference/authoring/anti-patterns.md`, and `./reference/authoring/context-preservation.md`.
3. Run `uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning`.
4. Read the returned planning-skill metadata.
5. Select and load zero to three applicable planning skills by name.
6. Produce a schema-valid `{summary, tasks}` object.
   Keep every task atomic.
   Copy relevant goals and constraints verbatim into each `context`.
   Do not add `skills`.
   Do not execute tasks.
7. Derive a lowercase kebab-case summary slug from `summary`.
8. Store the complete draft JSON object in `TASK_DRAFT_JSON`.
9. Pipe `TASK_DRAFT_JSON` to:

```bash
printf '%s' "$TASK_DRAFT_JSON" | uv run --directory ~/.config/opencode/scripts/python generate-task-json \
  --summary-slug "$SUMMARY_SLUG"
```

10. Return generator stdout only.

## Output Contract

Return only the `.tasks/<summary-slug>.json` path emitted by `generate-task-json`.
Match the path format requested by `## EXPECTED OUTPUT`.

## Verification

- Verify that the generated path is relative and matches `.tasks/<lowercase-kebab-case-slug>.json`.
- Verify that the path contains no Markdown formatting or explanatory text.

## Guardrails

- Do not populate `skills` manually.
- Pipe the complete root JSON object to `generate-task-json` through standard input.
- Derive the lowercase kebab-case summary slug from `summary`.
- Do not create `.tasks` or write a task-draft file manually.
- Do not bundle dependent changes.
- Return `BLOCKED: <reason>` for malformed input or generator failure.

## Cross-References

- Load selected planning skills by name.
- See `./reference/skill-assignment.md` for final task-skill assignment.
- See `./reference/scripts/generate-task-json.md` for generator behavior.

## Docs

See `./reference/README.md` for supporting documentation.
