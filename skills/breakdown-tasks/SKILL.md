---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
tags: [workflow, internal]
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
- **Filename:** `<epoch>-<slug>.json` where slug is a URL-safe truncation of the request summary (max 64 chars).
  - If the slug is empty after sanitization, use `decomposition` as fallback.
- **Collision behavior:** If the derived filename already exists in `.tasks/`, emit `BLOCKED: State file <path> already exists — remove manually or wait for next epoch second.` and halt.
- **Retention:** `.tasks/` is ephemeral working state. Files may be cleaned after the workflow completes or retained for debugging at the operator's discretion.

Set `STATE_FILE=~/.config/opencode/.tasks/<derived-filename>.json`.

Initialize the file with a JSON object containing the `summary` field (empty string placeholder) and an empty `tasks` array:

```json
{ "summary": "", "tasks": [] }
```

### 2. User Request Summary Extraction

Extract the request from `## DETAILS` and produce a one-paragraph summary (max 2000 chars) capturing the goal, scope, and constraints.
This summary populates the root-level `summary` field in the output.

### 3. Atomic Task Identification

Split the request into atomic tasks following the [Atomicity Rule](#atomicity-rule).
Each task must represent exactly one unit of work with a single `purpose` sentence and one `expectedOutput` paragraph.

#### Granularity checklist

- Consult `./reference/authoring/task-granularity.md` to ensure each task has a single action verb and a single expected output.
- Consult `./reference/authoring/core-rules.md` for the five atomicity rules that define proper task boundaries.
- Review `./reference/authoring/anti-patterns.md` for common work-boundary mistakes before finalizing task boundaries.

Populate all remaining task fields for each task: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.

#### 3a. Task Structure Validation

Call `uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"`.

- **Exit 0:** Proceed.
- **Exit 1:** Review errors on stderr, fix violations, and re-invoke.
  Repeat until exit code 0.
- **Exit 2 (internal/parse error):** Surface the issue to the caller.
  Do not retry.

### 4. Available Skills Discovery

Run `uv run --directory ~/.config/opencode/scripts/python collect-skills`.
Capture stdout and parse the JSON array into a list of skill objects (`name`, `description`, `class`, `location`, `source`).
Hold the list in working memory for the remainder of execution.
If the command exits non-zero, report `BLOCKED: Unable to discover available skills — collect-skills invocation failed.`
If the output is an empty array, proceed with an empty skill index.

### 5. Full Output Assembly

Read the current state from `"$STATE_FILE"`.
Build a JSON object with `summary` (string) and `tasks` (array of packet objects in sequential order).

Populate `skills` for each task using the following LLM-based matching process:

1. **Analyze each task independently.** Consider its purpose, context, files to read/write, and execution instructions in isolation. Each task receives its own skill assignment; do not reuse or inherit assignments across tasks. Tasks in the same domain may receive the same skill assignment. Independence means each task evaluates its own match, not that assignments must be unique.

2. **Identify required domain/expertise.** From the task's purpose and context, determine what domain knowledge, technical skills, or specialized expertise a worker would need to complete it successfully. Consider file types, tooling, languages, frameworks, or conventions referenced in the task.

3. **Cross-reference enriched skill index.** For each task, scan the discovered skill list against the task's required expertise. Use every available metadata field — `name`, `description`, `class`, `location`, and `tags` — to evaluate relevance. The `tags` field (when present) provides quick categorical matching (e.g., "python", "testing", "cli", "documentation", "node").

4. **Select best-matching skills (typically 1-N).** Select the best-matching skills (typically 1-N). Zero skills is acceptable only when no skill in the index matches the task's domain or expertise requirements. When multiple skills match, prefer the most specific over the most general. If a skill's `class` constrains its invocation context (e.g., `delegated`), consider whether the task's execution mode is compatible.

5. **Document rationale.** For each skill assigned to a task, append a one-sentence rationale as a comment or adjacent note explaining why it was matched. This supports auditability and future refinement of the skill index.

**Rule: Per-task independence.** Each task's skill assignment is independent of all others. When clear skill matches exist, assign them. Zero skills is appropriate only when no skill in the index fits. Never merge or split tasks to accommodate skill availability.

Write the assembled output object back into `"$STATE_FILE"`, overwriting the previous content.

### 6. Final Validation and State Emission

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
- Skill assignment should match available skills. Zero skills is acceptable only when no matching skill exists in the index.
- Task atomicity over skill availability.
  Do not merge or split tasks to match skill scope.

## Docs

See `./reference/README.md` for documentation of supporting files.
