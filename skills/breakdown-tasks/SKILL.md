---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
tags: [workflow, internal, task-decomposition, delegator, planning, orchestration, skill-assignment]
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
Produce `TaskDraft` objects without a `skills` field.
Skills are populated automatically by `assign-skills`.

## Input Contract

Standard delegation packet — `## PURPOSE` and `## DETAILS`.

## Execution

### 1. Init state, discover planning skills

```bash
STATE_FILE=$(uv run --directory ~/.config/opencode/scripts/python init-state-file \
  --output-dir ~/.config/opencode/.tasks)
REL_FILE=".tasks/$(basename "$STATE_FILE")"
PLANNING_SKILLS=$(uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning)
```

`init-state-file` derives `<epoch>-decomposition.json`, checks collision, writes `{"summary":"","tasks":[]}`, prints absolute path. `BLOCKED` on collision or IO error.

### 2. Decompose

Read `./schema/task-input.schema.json` — defines the `TaskDraft` format. No `skills` property exists.

From `$PLANNING_SKILLS`, select 0–3 planning skills whose descriptions and tags match the request domain. Load each via `skill`.

Load authoring guides (`./reference/authoring/core-rules.md`, `task-granularity.md`, `anti-patterns.md`, `context-preservation.md`). Extract a summary (max 2000 chars) from `## DETAILS`. Decompose the request into `TaskDraft` objects — each with `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`, and optional `verification`.

Write `{summary, tasks: [TaskDraft, ...]}` to `$STATE_FILE`.

### 3. Assign skills

```bash
uv run --directory ~/.config/opencode/scripts/python assign-skills \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-input.schema.json
```

The script discovers all skills internally, filters to `operation` and `documentation` classes (default), validates TaskDraft input, renders skill metadata into text passages, and uses a FlashRank cross-encoder reranker to rank skills against each task draft. Floor-only gating — no upper cap, every relevant skill above floor is assigned.

Defaults are canonical. Override via `--skills-json`, `--floor`, `--min-skills`, `--skill-classes`, `--model-name` for debugging only.

### 4. Validate and return

```bash
uv run --directory ~/.config/opencode/scripts/python validate-and-format-output \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

Final schema validation. If this fails, the decomposition or assignment is fundamentally broken — inspect output and re-run from step 2.

Return `$REL_FILE`.

## Atomicity Rule

See `./reference/authoring/core-rules.md` for the five atomicity rules.
See `./reference/authoring/task-granularity.md` for splitting heuristics.

## Context Preservation

Copy all relevant user context into each task's `context` field.
See `./reference/authoring/context-preservation.md` for detailed guidelines.

## Output Contract

A single string: the relative `.tasks/<epoch>-decomposition.json` state file path (e.g. `.tasks/1710364234-decomposition.json`).

## Guardrails

- `TaskDraft` has no `skills` property — do not add one.
- Never populate `skills` manually.
- Default floor, min-skills, and class filter are canonical — don't change per-run.
- `assign-skills` guarantees at least 1 skill per task. No degraded/fallback mode.
- Preserve original intent and context.
- Include only information necessary for a worker to execute the task.
- Do not bundle dependent changes into a single task.
- Do not execute the decomposed work.
- Write state to `~/.config/opencode/.tasks/<filename>.json` throughout the pipeline.
- Return `BLOCKED` for malformed input.
- Prioritize task atomicity over skill availability.

## Docs

See `./reference/README.md` for documentation of supporting files.
