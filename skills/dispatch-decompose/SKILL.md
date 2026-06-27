---
name: dispatch-decompose
description: "Use when the delegator must send the full user request and clarification context to a breakdown-tasks worker and return the worker's JSON decomposition output."
class: inline
---

# Dispatch Decompose

Construct the decomposition packet for `breakdown-tasks` and invoke exactly one worker with it.
Return the worker result unchanged.

## Input

Accept the full decomposition context as plaintext.
The input must include the original user request and the complete clarification context gathered by the delegator.
The clarification context preserves question text and answers when available.

### Plaintext Packet Format Sent To Worker

```text
## PURPOSE
Decompose the request into atomic task-delegation work items.

## DETAILS
<full original user request and clarification context, verbatim>

## FILES TO READ
None

## FILES TO WRITE
None

## SKILLS
breakdown-tasks

## EXECUTION INSTRUCTIONS
Load the breakdown-tasks skill and use it to decompose the full request and clarification context into atomic delegation packets.
Return only the decomposition result.

## VERIFICATION
The output must be valid JSON parseable as an object with a required `summary` field (string, maxLength 2000) and a required `tasks` array (non-empty).
Every task in the `tasks` array must be an object containing all required fields: id, purpose, context, filesToRead, filesToWrite, skills, executionInstructions, expectedOutput.
Each `id` must be a valid UUID v4 string.
If a task has a `dependencies` array, each entry must reference a valid task `id` within the same decomposition.
Each `executionInstructions` array must be non-empty, with items containing at minimum `step` (integer ≥1) and `action` (string).
The `tags` field is not part of the schema and must not be validated or expected.

## EXPECTED OUTPUT
A JSON object containing a root-level `summary` string and a non-empty `tasks` array.
Each task in `tasks` is a delegation packet object with the following fields:
- `id` (UUID v4) — unique task identifier
- `purpose` (string) — single-sentence task goal
- `context` (string) — expanded context for the worker (up to 8000 characters)
- `filesToRead` (string array) — files the worker must read before starting
- `filesToWrite` (string array) — files the worker is expected to create or modify
- `skills` (string array) — skills the worker must load
- `executionInstructions` (object array) — ordered steps with `step` and `action`, optionally `verification`
- `verification` (string array, optional) — top-level checks on the complete deliverable
- `expectedOutput` (string) — precise description of the deliverable
- `dependencies` (string array, optional) — task IDs that must complete before this one begins
```

## Output

Return the result from the `breakdown-tasks` worker unchanged.
`PARTIAL:` is a valid success signal from the worker — preserve and forward it as-is without transformation or rejection.

## Execution Plan

1. **Accept decomposition context** from the delegator.
   Confirm it includes the original user request and the clarification context.
2. **Reject empty context.**
   If the input is absent, empty, or whitespace-only, return `BLOCKED: dispatch-decompose requires the full request and clarification context.`
3. **Construct the decomposition packet.**
   Use the packet template above.
   Insert the full input verbatim into `## DETAILS`.
   Keep `## SKILLS` hardcoded to `breakdown-tasks`.
4. **Validate the packet.**
   Confirm all 8 standard packet sections are present.
   Confirm `## DETAILS` contains the complete input verbatim.
   Confirm `## SKILLS` is exactly `breakdown-tasks`.
5. **Invoke the worker.**
   Call the `task` tool with `subagent_type: "worker"`.
   Set `description` to `Decompose request into atomic tasks`.
   Set `command` to `Decompose request into atomic tasks`.
   Set `prompt` to the complete decomposition packet.
6. **Return the worker result unchanged.**
   Do not parse, normalize, summarize, or reformat the worker output.
   If the output contains `PARTIAL:` followed by JSON, treat it as a valid completion signal and forward it as-is.
   Do not reject, re-route, or re-wrap `PARTIAL:` responses.

This is a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Always pass the complete original request and clarification context into `## DETAILS`.
- Never summarize, compress, omit, or reinterpret clarification answers.
- Never construct a decomposition packet without `## SKILLS` set to `breakdown-tasks`.
- Never invoke more than one worker.
- Never call any subagent type other than `worker`.
- Never parse or rewrite the worker result before returning it.
- Never treat `PARTIAL:` as an error — it is a valid success signal from the worker and must be forwarded unchanged.
- Never write files.

## Docs

See `./reference/README.md` for supporting notes.
