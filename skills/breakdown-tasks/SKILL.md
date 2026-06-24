---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
See `./reference/authoring/core-rules.md` for atomic task definition and decomposition rules.

## Input Contract

Incoming packet is a standard delegation packet.

## Execution Steps

### 1. Parse Input

Read the delegation packet's `## PURPOSE` and `## DETAILS` sections to understand the decomposition goal and the request to decompose.

### 2. Extract User Request Summary

Extract the request from `## DETAILS` and produce a one-paragraph summary (max 2000 chars) capturing the goal, scope, and constraints.
This summary populates the root-level `summary` field in the output.

### 3. Discover Available Skills

Run `uv run --directory ~/.config/opencode/scripts/python collect-skills`.
Capture stdout and parse the JSON array into a list of skill objects (`name`, `description`, `class`, `location`, `source`).
Hold the list in working memory for the remainder of execution.
If the command exits non-zero, report `BLOCKED: Unable to discover available skills — collect-skills invocation failed.`
If the output is an empty array, proceed with an empty skill index.

### 4. Atomic Task Identification

Split the request into atomic tasks following the [Atomicity Rule](#atomicity-rule).
Each task must represent exactly one unit of work with a single `purpose` sentence and one `expectedOutput` paragraph.
Assign each task a UUID v4 identifier immediately upon creation.

### 5. Dependency Analysis

For each identified task, determine its prerequisites:

- Which tasks must complete before this task can begin?
- Which files must exist before this task can read them?
- Which tasks produce outputs that this task consumes?

Populate each task's `dependencies` array with the UUIDs of prerequisite tasks.
Tasks with empty `dependencies` arrays have no prerequisites and execute in parallel.

### 6. Task Ordering and Dependency Mapping

Order tasks by their dependency relationships using topological sort.
Use the per-task `dependencies` arrays to determine execution order.
See `./reference/orchestration/dependency-patterns.md` for common topologies (sequential, parallel, fan-out, fan-in).

### 7. Format Each Downstream Packet

For every atomic task, produce a JSON object conforming to the JSON Schema in `./schema/task-packet.schema.json`.
Populate `skills` by cross-referencing the task's purpose and context against the discovered skill list.
Assign the best-matching skill name(s) into the `skills` array based on description alignment.
If no match exists, set `skills` to an empty array.

### 8. Collect and Return

Build a JSON object with `summary` (string) and `tasks` (array of packet objects in dependency order).
Return the JSON object as a valid JSON string.
Do not wrap output in ```json fences.
Do not prepend or append explanatory text.
Return only the raw JSON literal.

## Atomicity Rule

Each task must represent exactly one unit of work.
If a task would require the worker to modify two unrelated files for two different reasons, split it.
Each task must have exactly one `purpose` sentence and one `expectedOutput` paragraph.
See `./reference/authoring/core-rules.md` for the five atomicity rules and `./reference/authoring/task-granularity.md` for splitting heuristics.

## Context Preservation

Copy all relevant user context into each task's `context` field so that workers never need to re-read the original prompt.
The `context` field contains the relevant subset of the user request, background information and constraints, and references to prior decisions or artifacts.
Context fields are 2000–8000 characters.
See `./reference/authoring/context-preservation.md` for detailed guidelines.

## Dependency Mapping

Populate each task's `dependencies` array with UUID v4 references to prerequisite tasks.
This per-task approach enables precise dependency tracking without a separate root-level map.
See `./reference/orchestration/dependency-patterns.md` for sequential chain, fan-out, fan-in, and parallel patterns.
See `./reference/orchestration/task-validation.md` for dependency graph validation checks (acyclicity, reference validity).

## Output Contract

Return a single JSON object with a `summary` string and a `tasks` array of task packet objects.
Any output violating this contract is a BLOCKER for the receiver.
The delegator rejects non-conforming output.
Do not include leading or trailing text, Markdown code fences (```json), preamble sentences, postscript commentary, or any non-JSON characters.
Return only the raw JSON literal.

### Verbatim JSON Requirement

Return the JSON object as a raw, unadorned JSON literal.
Do not wrap it in Markdown code fences.
Do not prefix it with preamble sentences.
Do not suffix it with commentary, summary, or sign-off text.
Start the output with `{`.
End it with `}`.
Any deviation from this verbatim requirement is a blocker.
The delegator discards non-conforming output.

See `./schema/task-packet.schema.json` for the canonical JSON Schema defining the `BreakdownTasksOutput` object and `TaskPacket` structure, including field types, constraints, and required keys.

## Task Validation

After decomposition, verify the output against the checks listed in `./reference/orchestration/task-validation.md`.
If any check fails, rework the affected packet(s) before returning.

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task.
  Omit background and rationale.
- Do not bundle dependent changes into a single task.
- **Do not execute the decomposed work** — This skill produces delegation packets only.
  Do not attempt to run the tasks, read files beyond scanning for dependency ordering, or produce any artifact other than packets.
- **Do not write files** — `filesToWrite` in the output JSON objects belongs to the downstream worker, not this skill.
  This skill writes nothing to disk.
- **Return BLOCKED: for malformed input** — If `## DETAILS` is missing, empty, or cannot be parsed as a decomposable request, return `BLOCKED: <reason>` immediately.
  Do not attempt to decompose an underspecified request.
- **Skill assignment is advisory, not mandatory** — Do not force-assign skills.
  Leave `skills` empty when no match exists.
- **Task atomicity over skill availability** — Do not merge or split tasks to match skill scope.

## Docs

See `./reference/README.md` for documentation of supporting files.