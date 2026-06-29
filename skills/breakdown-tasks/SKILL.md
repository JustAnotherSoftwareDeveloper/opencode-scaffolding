---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.

## Input Contract

Incoming packet is a standard delegation packet.

## Execution Steps

### 1. Input Parsing and State File Initialization

#### 1a. Read Delegation Packet

Read the delegation packet's `## PURPOSE` and `## DETAILS` sections to understand the decomposition goal and the request to decompose.

#### 1b. State File Initialization

Derive the state file path using the following rules:

- **Directory:** `~/.config/opencode/.tasks/` (create if missing).
- **Filename pattern:** `<unix-epoch-seconds>-<request-summary-slug>.json`
  - `<unix-epoch-seconds>`: Output of `date +%s`.
  - `<request-summary-slug>`: Derived from the request summary by:
    1. Lowercasing the entire string.
    2. Replacing non-alphanumeric characters (except hyphens) with hyphens.
    3. Collapsing runs of multiple hyphens into one.
    4. Truncating to 64 characters.
  - If the slug is empty after sanitization, use `decomposition` as fallback.
- **Collision behavior:** If the derived filename already exists in `.tasks/`, emit `BLOCKED: State file <path> already exists — remove manually or wait for next epoch second.` and halt.
- **Retention:** `.tasks/` is ephemeral working state. Files may be cleaned after the workflow completes or retained for debugging at the operator's discretion.

Set `STATE_FILE=~/.config/opencode/.tasks/<derived-filename>.json`.

Initialize the file with a JSON object containing the `summary` field (empty string placeholder) and an empty `tasks` array:

```json
{"summary": "", "tasks": []}
```

### 2. User Request Summary Extraction

Extract the request from `## DETAILS` and produce a one-paragraph summary (max 2000 chars) capturing the goal, scope, and constraints.
This summary populates the root-level `summary` field in the output.

### 3. Available Skills Discovery

Run `uv run --directory ~/.config/opencode/scripts/python collect-skills`.
Capture stdout and parse the JSON array into a list of skill objects (`name`, `description`, `class`, `location`, `source`).
Hold the list in working memory for the remainder of execution.
If the command exits non-zero, report `BLOCKED: Unable to discover available skills — collect-skills invocation failed.`
If the output is an empty array, proceed with an empty skill index.

### 4. Atomic Task Identification

Split the request into atomic tasks following the [Atomicity Rule](#atomicity-rule).
Each task must represent exactly one unit of work with a single `purpose` sentence and one `expectedOutput` paragraph.

#### 4a. UUID Generation

Call `uv run --directory "$SCRIPTS_PYTHON" generate-uuids --state-file "$STATE_FILE"` with the number of identified tasks.
The script reads the task list from the state file, appends a UUID to each task's `id` field, and writes the result back to the state file.
Assign each UUID to one task's `id` field in the same order as the tasks were identified.

Populate all remaining task fields for each task: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.

#### 4b. Task Structure Validation

Call `uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"`.

- **Exit 0:** Proceed.
- **Exit 1:** Review errors on stderr, fix violations, and re-invoke.
  Repeat until exit code 0.
- **Exit 2 (internal/parse error):** Surface the issue to the caller.
  Do not retry.

### 5. Dependency Analysis

For each identified task, determine its prerequisites:

- Which tasks must complete before this task can begin?
- Which files must exist before this task can read them?
- Which tasks produce outputs that this task consumes?

Populate each task's `dependencies` array with the UUIDs of prerequisite tasks.
Tasks with empty `dependencies` arrays have no prerequisites and execute in parallel.

Call `uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --state-file "$STATE_FILE"` with the task list.

- **Exit 0:** Proceed.
- **Exit 1:** Review cycle or orphan-dependency errors on stderr, fix them, and re-invoke.
  Repeat until exit code 0.
- **Exit 2 (internal/parse error):** Surface the issue to the caller.
  Do not retry.

### 6. Task Ordering

Call `uv run --directory "$SCRIPTS_PYTHON" topological-sort --state-file "$STATE_FILE"` with the task list.

- **Exit 0:** Replace task list with sorted output and proceed.
- **Exit 1:** Cycle detected (cycle path in stderr).
  Fix dependencies.
  Re-run step 5 validation.
  Retry step 6.
- **Exit 2 (parse/missing fields):** Surface the issue to the caller.
  Do not retry.

See `./reference/orchestration/dependency-patterns.md` for common topologies (sequential, parallel, fan-out, fan-in).

### 7. Full Output Assembly

Read the current state from `"$STATE_FILE"`.
Build a JSON object with `summary` (string) and `tasks` (array of packet objects in dependency order from step 6).

Populate `skills` for each task by cross-referencing the task's purpose and context against the discovered skill list.
Assign the best-matching skill name(s) into the `skills` array based on description alignment.
If no match exists, set `skills` to an empty array.

Write the assembled output object back into `"$STATE_FILE"`, overwriting the previous content.

### 8. Final Validation and State Emission

Call `uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"`.

- **Exit 0:** Read `"$STATE_FILE"` and emit its raw JSON contents verbatim.
  Strip any internal metadata fields (e.g., `_stateVersion`, `_internal`) from the output object before emission if present.
  Do not add preamble, commentary, or markdown fences.
- **Exit 1:** Review schema validation errors on stderr, fix the input, and re-invoke.
  No fixed retry limit.
- **Exit 2 (internal/parse error):** Surface the issue to the caller.
  Do not retry.

Do not wrap output in ```json fences.
Do not prepend or append explanatory text.
Return only the raw JSON literal.

## Atomicity Rule

See `./reference/authoring/core-rules.md` for the five atomicity rules and `./reference/authoring/task-granularity.md` for splitting heuristics.

## Context Preservation

Copy all relevant user context into each task's `context` field so workers never need to re-read the original prompt.
The `context` field contains the relevant subset of the user request, background information and constraints, and references to prior decisions or artifacts.
See `./reference/authoring/context-preservation.md` for detailed guidelines.

## Dependency Mapping

Populate each task's `dependencies` array with UUID v4 references to prerequisite tasks.
This per-task approach enables precise dependency tracking without a separate root-level map.
See `./reference/orchestration/dependency-patterns.md` for sequential chain, fan-out, fan-in, and parallel patterns.
See `./reference/orchestration/task-validation.md` for dependency graph validation checks (acyclicity, reference validity).

## Output Contract

Return a single JSON object with a `summary` string and a `tasks` array of task packet objects.
Any output violating this contract is a BLOCKER for the receiver.
Do not include leading or trailing text, Markdown code fences, preamble sentences, postscript commentary, or any non-JSON characters.
Return only the raw JSON literal starting with `{` and ending with `}`.
Any deviation from this verbatim requirement is a blocker.
See `./schema/task-packet.schema.json` for the canonical JSON Schema defining the `BreakdownTasksOutput` object and `TaskPacket` structure.

## Task Validation

After decomposition, verify the output against the checks listed in `./reference/orchestration/task-validation.md`.
If any check fails, rework the affected packet(s) before returning.

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task.
  Omit background and rationale.
- Do not bundle dependent changes into a single task.
- Do not execute the decomposed work.
  This skill produces delegation packets only.
- Write state to ~/.config/opencode/.tasks/<filename>.json throughout the pipeline.
  This skill uses the .tasks/ state file as its canonical working state.
  The `filesToWrite` in output JSON objects belongs to the downstream worker, not this skill.
- Return BLOCKED for malformed input.
  If `## DETAILS` is missing, empty, or cannot be parsed as a decomposable request, return `BLOCKED: <reason>` immediately.
- Skill assignment is advisory, not mandatory.
  Leave `skills` empty when no match exists.
- Task atomicity over skill availability.
  Do not merge or split tasks to match skill scope.

## Docs

See `./reference/README.md` for documentation of supporting files.