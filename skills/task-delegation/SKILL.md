---
name: task-delegation
description: Use when validating a delegation packet and forwarding it to a worker via the task tool.
class: inline
---

# Task Delegation

Validate a delegation packet and forward it to a worker via the task tool.

## Input

The skill accepts any and all input formats with no preference — including plaintext, freeform natural language, JSON, YAML, key-value lists, or any other format. No particular input format is required, formalized, or preferred.

### Plaintext Packet Format (produced for worker)

```
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated file paths to read>

## FILES TO WRITE
<single file path, or "None">

## SKILLS
<comma-separated skill names to load>

## EXECUTION INSTRUCTIONS
<step-by-step instructions for execution>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

## Output

The result returned by the worker matching the packet's `## EXPECTED OUTPUT`.

## Execution Plan

1. **Accept arbitrary input** — Accept input in any format (plaintext, JSON, YAML, freeform natural language, key-value lists, etc.). Do not validate or reject for any specific format.
2. **Infer the 8 standard packet fields** — Analyze the input and infer content for each of the 8 standard fields (PURPOSE, DETAILS, FILES TO READ, FILES TO WRITE, SKILLS, EXECUTION INSTRUCTIONS, VERIFICATION, EXPECTED OUTPUT). Use simple heuristics such as:
   - Matching `## HEADER` patterns in plaintext input.
   - Extracting key-value pairs from structured input (JSON, YAML).
   - Matching known aliases (e.g., `instructions` → EXECUTION INSTRUCTIONS, `context` → DETAILS).
   - Extracting best-guess content from freeform text.
   Do not formalize or prefer any single inference strategy.
3. **Mark uninferable fields** — For any of the 8 fields that cannot be inferred from the input, set its value to the explicit marker: `UNKNOWN — not provided in input`.
4. **Construct complete plaintext packet** — Build a well-formed plaintext delegation packet with all 8 sections present using the Packet Template. Every section header (`## PURPOSE`, `## DETAILS`, etc.) must appear, even if its content is the UNKNOWN marker.
5. **Validate all sections present** — Confirm the constructed packet has exactly 8 sections and none are missing. If sections are absent, report a clear error describing which sections are missing and stop.
6. **Invoke the worker** — Invoke the `task` tool with `subagent_type: "worker"`, `description` set to the inferred PURPOSE content, `prompt` set to the full plaintext packet, and `command` set to the inferred PURPOSE content.
7. **Return the worker result** — Return the result from the worker unchanged.

This is a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Accept any input format without rejection — do not require, prefer, or validate for any specific format (JSON, YAML, plaintext, etc.).
- Always produce exactly 8 sections in the output packet — no more, no less.
- Mark any uninferable field with the explicit marker `UNKNOWN — not provided in input`; do not fill with default values, placeholder text, or guesses.
- Do not formalize or prefer any input format in the inference heuristics.
- After construction, do not modify, re-encode, or further transform the plaintext packet.
- If the constructed packet is missing sections, report a clear error describing which sections are absent and do not invoke the worker.