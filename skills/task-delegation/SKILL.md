---
name: task-delegation
description: "Use when adapting loose task information into one worker packet and forwarding it via the task tool."
tags: [task-delegation, create, code, opencode]
class: inline
---

# Task Delegation

Adapt loose task information into one worker packet and forward it via the task tool.

## Input

Accept any input format, including plaintext, freeform natural language, JSON, YAML, key-value lists, or mixed notes.
Use loose field mapping to produce exactly one plaintext worker packet.
Reject a full `breakdown-tasks` JSON output object unless one task is clearly selected.

### Plaintext Packet Format (produced for worker)

```text
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated file paths to read — listed files are required; broad related-file discovery is permitted by default>

## FILES TO WRITE
<single file path, or "None">

## SKILLS
<comma-separated skill names to load>

## EXECUTION INSTRUCTIONS
<step-by-step instructions>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

## Output

The result returned by the worker matching the packet's `## EXPECTED OUTPUT`.

## Execution Plan

1. **Accept arbitrary input** — Accept plaintext, JSON, YAML, freeform natural language, key-value lists, or mixed notes.
2. **Reject ambiguous multi-task input** — If input is an object with `summary` and `tasks` and no single task is clearly selected, return `BLOCKED: task-delegation requires exactly one selected task.`
3. **Infer the 8 standard packet fields** — Analyze the input and infer content for PURPOSE, DETAILS, FILES TO READ, FILES TO WRITE, SKILLS, EXECUTION INSTRUCTIONS, VERIFICATION, and EXPECTED OUTPUT.
   Use loose aliases:
   - `purpose`, `goal`, `task`, `title` map to `## PURPOSE`.
   - `context`, `details`, `background`, `description` map to `## DETAILS`.
   - `filesToRead`, `read`, `sources` map to `## FILES TO READ`.
   - `filesToWrite`, `write`, `outputs` map to `## FILES TO WRITE`.
   - `skills`, `skill` map to `## SKILLS`.
   - `executionInstructions`, `instructions`, `steps` map to `## EXECUTION INSTRUCTIONS`.
   - `verification`, `checks` map to `## VERIFICATION`.
   - `expectedOutput`, `deliverable`, `output` map to `## EXPECTED OUTPUT`.
4. **Mark uninferable fields** — For any of the 8 fields that cannot be inferred from the input, set its value to the explicit marker: `UNKNOWN — not provided in input`.
5. **Construct complete plaintext packet** — Build a well-formed plaintext delegation packet with all 8 sections present using the Packet Template.
   Every section header (`## PURPOSE`, `## DETAILS`, etc.) must appear, even if its content is the UNKNOWN marker.
   - **FILES TO READ: list required files; broad related-file discovery is permitted by default.** Include the files the worker must read before discovering related content. After reading listed files, the worker may broadly discover and read related files needed for task execution. Avoid unbounded patterns. FILES TO READ may include glob patterns when broad file sets are needed.
6. **Validate all sections present** — Confirm the constructed packet has exactly 8 sections and none are missing.
   If sections are absent, report a clear error describing which sections are missing and stop.
7. **Invoke the worker** — Invoke the `task` tool with `subagent_type: "worker"`, `description` set to the inferred PURPOSE content, `prompt` set to the full plaintext packet, and `command` set to the inferred PURPOSE content.
8. **Return the worker result unchanged** — Return the result from the worker exactly as received.
   - **Preserve PARTIAL: as a valid success signal.** If the worker returns `PARTIAL:`, do not treat it as an error or a blocker. Accept it as a valid response and pass it through to the caller. The delegator will forward the partial output to subsequent steps as appropriate. Do not rewrap, prefix, or modify the PARTIAL: response.

This is a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Accept any single-task input format without rejecting a format category.
- Reject unresolved multi-task input.
- Always produce exactly 8 sections in the output packet — no more, no less.
- Mark any uninferable field with the explicit marker `UNKNOWN — not provided in input`; do not fill with default values, placeholder text, or guesses.
- Use loose mapping; do not require exact field names.
- After construction, do not modify, re-encode, or further transform the plaintext packet.
- If the constructed packet is missing sections, report a clear error describing which sections are absent and do not invoke the worker.
