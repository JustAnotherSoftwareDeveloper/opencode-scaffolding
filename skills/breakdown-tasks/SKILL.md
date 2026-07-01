---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
tags: [workflow, internal]
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.

## Input Contract

Expect a standard delegation packet.

## Execution Steps

### 1. Input Parsing and State File Initialization

- **Step 1a:** Read the delegation packet's `## PURPOSE` and `## DETAILS` sections.
- **Step 1b:** Initialize the state file. See `./reference/state-initialization.md` for the deterministic derivation rules, collision behavior, and retention policy.

### 2. User Request Summary Extraction

Extract a one-paragraph summary (max 2000 characters) from `## DETAILS` for the `summary` field.

### 3. Atomic Task Identification

Split the request into atomic tasks following the [Atomicity Rule](#atomicity-rule).
Each task must have a single `purpose` sentence and one `expectedOutput` paragraph.

- Consult `./reference/authoring/task-granularity.md` for granularity guidelines.
- Consult `./reference/authoring/core-rules.md` for the five atomicity rules.
- Review `./reference/authoring/anti-patterns.md` for common mistakes.

Populate task fields: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.

#### 3a. Task Structure Validation

Run `uv run --directory ~/.config/opencode/scripts/python validate-task-structure --state-file "$STATE_FILE" --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json`. Handle exit codes 0, 1, and 2 as documented in `./reference/scripts/validate-task-structure.md`.

### 4. Available Skills Discovery

Run `uv run --directory ~/.config/opencode/scripts/python collect-skills` and parse the JSON array.
See `./reference/scripts/pipeline-overview.md` for error handling.

### 5. Skill Assignment

Populate `skills` for each task using the deterministic assignment procedure in `./reference/skill-assignment.md`.

### 6. Final Validation and State Emission

Run `uv run --directory ~/.config/opencode/scripts/python validate-and-format-output --state-file "$STATE_FILE" --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json`.
See `./reference/scripts/validate-and-format-output.md`.

Return the `STATE_FILE` path as a single string.

## Atomicity Rule

See `./reference/authoring/core-rules.md` for the five atomicity rules.
See `./reference/authoring/task-granularity.md` for splitting heuristics.

## Context Preservation

Copy all relevant user context into each task's `context` field.
See `./reference/authoring/context-preservation.md` for detailed guidelines.

## Output Contract

Return a single string.
The string is the path to the `.tasks` state file written during decomposition.

## Task Validation

Verify output against checks in `./reference/orchestration/task-validation.md`.

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task.
  - Omit background and rationale.
- Do not bundle dependent changes into a single task.
- Do not execute the decomposed work.
- Write state to `~/.config/opencode/.tasks/<filename>.json` throughout the pipeline.
- Return `BLOCKED` for malformed input.
- Prioritize task atomicity over skill availability.
- See `./reference/README.md` for documentation of supporting files.