---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items. Separates planning from execution: the LLM decomposes, the script assigns skills."
tags: [workflow, tasking, task-decomposition, task-planning, request-analysis, atomic-tasks]
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
Produce `TaskDraft` objects without a `skills` field.

## Input Contract

Read `## PURPOSE` and `## DETAILS`.
Return `BLOCKED` if either section is missing.

## Execution

1. Read `./schema/task-input.schema.json`.
   Select 0–3 applicable planning skills from:

```bash
uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning
```

   Read `./reference/authoring/core-rules.md`, `task-granularity.md`, `anti-patterns.md`, and `context-preservation.md`.
   Produce a schema-valid `{summary, tasks}` object.
   Keep every task atomic.
   Copy the relevant goal and constraints verbatim into each `context`.
   Do not add `skills`.
   Do not execute the tasks.

2. Derive a lowercase kebab-case summary slug.
   Pipe the complete draft JSON object to:

```bash
uv run --project ~/.config/opencode/scripts/python generate-task-json \
  --summary-slug "$SUMMARY_SLUG"
```

3. Return stdout only.

## Atomicity Rule

Prioritize atomic task boundaries over skill availability.
See `./reference/authoring/core-rules.md` and `./reference/authoring/task-granularity.md`.

## Context Preservation

Include only the information required to execute each task.
See `./reference/authoring/context-preservation.md`.

## Output Contract

A single `.tasks/<summary-slug>.json` path.

## Guardrails

- Do not populate `skills` manually.
- Provide the complete root JSON object through standard input.
- Use a lowercase kebab-case summary slug.
- Do not bundle dependent changes.
- Return `BLOCKED` for malformed input.

## Docs

See `./reference/README.md` for supporting documentation.
