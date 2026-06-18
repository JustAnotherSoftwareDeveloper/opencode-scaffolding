---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
See `./REFERENCE.md` for atomic task definition and decomposition rules.

## Input Contract

Incoming packet is a standard delegation packet.

## Execution Steps

1. Parse the delegation packet's `## PURPOSE` and `## DETAILS` sections to understand the decomposition goal and the request to decompose.
2. Extract the request from `## DETAILS`.
   Treat `## DETAILS` as the primary input for decomposition.
3. Discover available skills.
   Run `uv run --directory ~/.config/opencode/scripts/python collect-skills`.
   Capture stdout and parse the JSON array into a list of skill objects (`name`, `description`, `class`, `location`, `source`).
   Hold the list in working memory for the remainder of execution.
   If the command exits non-zero, report `BLOCKED: Unable to discover available skills — collect-skills invocation failed.`
   If the output is an empty array, proceed with an empty skill index.
4. Decompose per `./REFERENCE.md`.
   Split the request into atomic tasks following Core Rules (single unit of work, single output artifact, logical step pipeline, dependent work serialization).
   Avoid Anti-Patterns.
   Use the available skill list to inform decomposition choices.
   Atomicity rules take precedence over skill availability.
5. Order tasks by prerequisites.
   Arrange tasks so that earlier tasks satisfy each task's dependencies.
   Order independent tasks using a stable heuristic such as alphabetical order.
6. Format each downstream packet.
   For every atomic task, produce a JSON object with exactly these 8 camelCase keys:
   `purpose`, `details`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `verification`, `expectedOutput`.
   Populate `skills` by cross-referencing the task's PURPOSE and DETAILS against the discovered skill list.
   Assign the best-matching skill name(s) into the `skills` array based on description alignment.
   If no match exists, set `skills` to an empty array.
   Use `filesToRead` as an array of path strings.
   Use `filesToWrite` as a single path string or `null`.
   Use all other keys as plain strings.
7. Collect all JSON objects into a JSON array.
   Build a JSON array literal `[...]` containing every formatted packet object in dependency order.
8. Return the JSON array as a valid JSON string.
   Do not wrap output in ```json fences.
   Do not prepend or append explanatory text.
   Do not include a leading or trailing newline beyond standard JSON formatting.
   Do not add any non-JSON characters.
   Return only the raw JSON array literal.

## Output Contract

Return a single JSON array of packet objects.
Any output violating this contract is a BLOCKER for the receiver.
The delegator rejects non-conforming output.
Do not include leading or trailing text, Markdown code fences (```json), preamble sentences, postscript commentary, or any non-JSON characters.
Return only the raw JSON array literal.
Ensure each object conforms to the JSON Schema defined below.

### Verbatim JSON Requirement

Return the JSON array as a raw, unadorned JSON literal.
Do not wrap it in Markdown code fences (```` ```json ... ``` ````).
Do not prefix it with preamble sentences.
Do not suffix it with commentary, summary, or sign-off text.
Start the output with `[`.
End it with `]`.
Any deviation from this verbatim requirement is a blocker.
The delegator discards non-conforming output.

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "purpose",
      "details",
      "filesToRead",
      "filesToWrite",
      "skills",
      "executionInstructions",
      "verification",
      "expectedOutput"
    ],
    "properties": {
      "purpose":               { "type": "string", "description": "Single sentence: what must be done" },
      "details":               { "type": "string", "description": "Full task description, constraints, and context" },
      "filesToRead":           { "type": "array", "items": { "type": "string" }, "description": "File paths the worker must read before starting" },
      "filesToWrite":          { "type": ["string", "null"], "description": "Single file path the worker must write, or null if none" },
      "skills":                { "type": "array", "items": { "type": "string" }, "description": "Advisory skill names to load, populated via skill-to-task matching" },
      "executionInstructions": { "type": "string", "description": "Step-by-step instructions for execution" },
      "verification":          { "type": "string", "description": "How to check work completed correctly" },
      "expectedOutput":        { "type": "string", "description": "What the worker should produce" }
    },
    "additionalProperties": false
  },
  "minItems": 1
}
```

## Verification

After decomposition, verify the output against these checks.
If any check fails, rework the affected packet(s) before returning.

- **JSON validity** — The entire output must be parseable as valid JSON.
  If parsing fails, the output is a blocker; do not return malformed JSON.
- **JSON array** — The parsed result must be a JSON array (not an object, string, or primitive).
  Wrap the output in `[...]` if missing and retry.
- **Schema compliance** — Every element in the array must have all 8 required camelCase keys: `purpose`, `details`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `verification`, `expectedOutput`.
  Missing, extra, or misspelled keys are a blocker.
- **Type correctness** — For every element:
  - `filesToRead` must be an array of strings.
  - `skills` must be an array of strings.
  - `filesToWrite` must be a string or `null`.
  - All other keys must be strings.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work.
  Verify no packet bundles independent or logically separable steps under a single PURPOSE.
- **Dependencies ordered** — Confirm that every task's prerequisites (files it reads, skills it needs, context it depends on) are satisfied by an earlier packet in the sequence.
  If not, reorder or split.
- **Skill-name reasonableness** — Each entry in the `skills` array must be appropriate for the task's PURPOSE and DETAILS.
  This is a reasonableness check, not a strict cross-reference — tasks may reference skills outside the discovered list.

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task.
  Omit background and rationale.
- Do not bundle dependent changes into a single task.
- **Do not execute the decomposed work** — This skill produces delegation packets only.
  Do not attempt to run the tasks, read files beyond scanning for dependency ordering, or produce any artifact other than packets.
- **Do not write files** — `filesToWrite` in the output JSON objects belongs to the downstream worker, not this skill.
  This skill writes nothing to disk.
- **Return `BLOCKED:` for malformed input** — If `## DETAILS` is missing, empty, or cannot be parsed as a decomposable request, return `BLOCKED: <reason>` immediately.
  Do not attempt to decompose an underspecified request.
- **Skill assignment is advisory, not mandatory** — Do not force-assign skills.
  Leave `skills` empty when no match exists.
- **Task atomicity over skill availability** — Do not merge or split tasks to match skill scope.