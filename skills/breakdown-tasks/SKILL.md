---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items. Separates planning from execution: the LLM decomposes, the script assigns skills."
# Tags inform assign-skills keyword matching for domain-relevant skill discovery.
tags: [workflow, tasking, task-decomposition, task-planning, request-analysis, atomic-tasks]
class: delegated
---

As a `delegated`-class skill, this worker produces a single `.tasks/<epoch>-decomposition.json` relative path. The orchestrator reads this path to dispatch individual tasks. No collation or multi-output handling is required.

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
Produce `TaskDraft` objects without a `skills` field.

## Design Principles

This skill is built on four principles:

1. **Separation of concerns** — Decomposition (LLM work) and skill assignment (script work) are distinct pipeline stages. The LLM produces structure-aware drafts; the script applies deterministic scoring. This prevents probabilistic skill selection and keeps each stage using its optimal tool.
2. **Determinism** — Canonical defaults, schema validation, and sequential state-file updates ensure reproducible output. Per-run configuration drift would produce inconsistent results.
3. **Atomicity primacy** — Task boundaries are defined by logical units of work, not by available skills. Atomicity rules take precedence over skill convenience because merged tasks lose verifiability.
4. **Progressive disclosure** — This SKILL.md is kept compact (one purpose, one output). Depth lives in `./reference/` files, which are linked with context about what problems they solve.

## Input Contract

Standard delegation packet — `## PURPOSE` and `## DETAILS`.

## Execution

### 1. Init state, discover planning skills

State initialization prevents filename collisions and gives downstream scripts a shared file handle. Planning skills are loaded so the LLM can reference domain knowledge during decomposition.

```bash
STATE_FILE=$(uv run --directory ~/.config/opencode/scripts/python init-state-file \
  --output-dir ~/.config/opencode/.tasks)
REL_FILE=".tasks/$(basename "$STATE_FILE")"
PLANNING_SKILLS=$(uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning)
```

`init-state-file` derives `<epoch>-decomposition.json`, checks collision, writes `{"summary":"","tasks":[]}`, prints absolute path. `BLOCKED` on collision or IO error.

### 2. Decompose

The LLM reads the schema to learn the `TaskDraft` format, loads applicable planning skills for domain context, applies authoring rules to ensure atomicity, and writes the result to the state file for the next pipeline stage.

- **Read schema** — `./schema/task-input.schema.json` defines the `TaskDraft` format. *(Enforces no `skills` property, preventing manual assignment.)*
- **Select planning skills** — From `$PLANNING_SKILLS`, select 0–3 whose descriptions and tags match the request domain. *(Planning skills provide domain heuristics that shape task boundaries; too many dilute focus.)*
- **Load authoring guides** — `./reference/authoring/core-rules.md`, `task-granularity.md`, `anti-patterns.md`, `context-preservation.md`. *(These encode atomicity rules, anti-pattern guards, granularity heuristics, and context rules — they prevent the most common decomposition mistakes.)*
- **Decompose and write state** — Extract summary (max 2000 chars) from `## DETAILS`. Produce `TaskDraft` objects — each with `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`, and optional `verification`. Write `{summary, tasks: [TaskDraft, ...]}` to `$STATE_FILE`. *(Writing to the state file makes the decomposition available to the `assign-skills` script downstream without re-prompting the LLM.)*

### 3. Assign skills

Skills are assigned by a deterministic script rather than the LLM to ensure consistency, avoid hallucinated assignments, and maintain a clear audit trail.

```bash
uv run --directory ~/.config/opencode/scripts/python assign-skills \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-input.schema.json
```

The script discovers all skills internally, filters to `operation` and `documentation` classes (default), validates TaskDraft input, renders skill metadata into text passages, and uses a FlashRank cross-encoder reranker to rank skills against each task draft. Floor-only gating — no upper cap, every relevant skill above floor is assigned.

> **Note:** Skills are populated automatically by `assign-skills`.

Default class filters (`operation`, `documentation`) and scoring parameters are canonical because they produce deterministic, production-consistent results. Override flags exist for debugging only — they should not be used in production runs.

### 4. Validate and return

Final schema validation catches structural errors (missing fields, wrong types, constraint violations) before the output reaches the delegator. Without this gate, malformed packets would cause worker failures downstream.

```bash
uv run --directory ~/.config/opencode/scripts/python validate-and-format-output \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

Final schema validation. If this fails, the decomposition or assignment is fundamentally broken — inspect output and re-run from step 2.

Return `$REL_FILE`.

## Atomicity Rule

Atomicity ensures each worker packet is self-contained and verifiable. These rules prevent the most common decomposition mistakes.

- See `./reference/authoring/core-rules.md` for the five atomicity rules.
- See `./reference/authoring/task-granularity.md` for splitting heuristics.

## Context Preservation

Proper context prevents worker ambiguity. The `context` field must be self-contained so workers never re-read the original prompt.

- Copy all relevant user context into each task's `context` field.
- See `./reference/authoring/context-preservation.md` for detailed guidelines.

## Output Contract

A single string: the relative `.tasks/<epoch>-decomposition.json` state file path (e.g. `.tasks/1710364234-decomposition.json`).

## Guardrails

- `TaskDraft` has no `skills` property — do not add one. *(`assign-skills` script owns skill population because it uses deterministic scoring; manual assignment would bypass this pipeline stage.)*
- Never populate `skills` manually. *(Manual assignment bypasses the weighted scoring backend, breaking the pipeline's separation of concerns.)*
- Default floor, min-skills, and class filter are canonical — don't change per-run. *(Per-run overrides introduce non-deterministic behavior and make results unreproducible.)*
- `assign-skills` guarantees at least 1 skill per task. No degraded/fallback mode. *(Every worker needs at least one skill to operate; a fallback mode would silently mask skill discovery failures.)*
- Copy the user's stated goal and constraints verbatim into each task's `context` field. Do not summarize, paraphrase, or truncate intent. Workers are stateless — they cannot re-read the original prompt, so the `context` field must be self-contained.
- Include only information necessary for a worker to execute the task. *(Over-inclusion wastes worker token capacity and distracts from the task's singular purpose.)*
- Do not bundle dependent changes into a single task. *(Atomicity rule — bundles make verification ambiguous because the output cannot be attributed to a single change.)*
- Do not execute the decomposed work. *(This skill is a planning/coordination step; executing work violates the pipeline's separation of concerns and the `delegated` class contract.)*
- Write state to `~/.config/opencode/.tasks/<filename>.json` throughout the pipeline. *(The state file is the shared artifact that connects pipeline stages. Without a fixed convention, downstream scripts cannot find their input.)*
- Return `BLOCKED` for malformed input. *(Malformed input would produce silently broken downstream tasks. Early failure is cheaper and more debuggable.)*
- Prioritize task atomicity over skill availability. *(Merging tasks to match available skill scope destroys atomicity guarantees and makes verification ambiguous.)*

## Docs

See `./reference/README.md` for a conceptual map of all reference documentation. Key entry points:

- **Authoring guides** (`./reference/authoring/`) — Atomicity rules, anti-patterns, granularity heuristics, and context-preservation guidelines. Consult these when decomposing a request to ensure each task is well-formed.
- **Pipeline scripts** (`./reference/scripts/`) — Walkthrough of the full breakdown pipeline and its design philosophy.
- **Skill assignment** (`./reference/skill-assignment.md`) — Scoring formula, class filter, and selection rules for automated skill assignment.
