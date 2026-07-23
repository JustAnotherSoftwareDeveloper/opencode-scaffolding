---
name: task-delegation
description: "Use when adapting loose task information into one worker packet and forwarding it via the task tool."
tags: [delegation, packet-formatting, field-mapping, worker-dispatch, loose-input, packet-construction]
class: inline
---

# Task Delegation

Adapt loose task information into one worker packet and forward it via the task tool.

## Input

Accept any input format, including plaintext, freeform natural language, JSON, YAML, key-value lists, or mixed notes.
Use loose field mapping to produce exactly one plaintext worker packet.
Reject a full `breakdown-tasks` JSON output object unless one task is clearly selected.

### Plaintext Packet Format

```text
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated required file paths to read — purposeful related-file discovery remains permitted>

## FILES TO WRITE
<comma-separated literal paths or bounded path patterns to create, modify, or delete, or "None">

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

`task-delegation` is the canonical constructor for ordinary eight-section worker packets and the validator for ordinary worker result envelopes. Return one complete, valid worker result envelope unchanged.
Require the first non-whitespace content to be `## Worker Result`.
Parse the first exact `## File Changes`, `## Verification`, and `## Deliverable` heading lines in that order.
Require the `Worker Result` table to contain `Status`, `What was done`, `Accomplishments`, `Files modified`, `Skills loaded`, `Deviations`, `Blocker`, and `Unblock condition`.
Require `Status` to equal `COMPLETE`, `PARTIAL`, or `BLOCKED`.
Require `File Changes` to contain `Path`, `Action`, and `Details` headers plus at least one data row.
Require `Verification` to contain `Check`, `Result`, and `Details` headers plus at least one data row.
Require every file action to equal `created`, `modified`, `deleted`, `unchanged`, `not completed`, or `none`.
Require every verification result to equal `PASS`, `FAIL`, or `NOT RUN`.
Require every report-table value and data-table cell to be non-empty.
Require `Files modified` to reconcile with every `created`, `modified`, and `deleted` row and remain `None` when no such row exists.
Require `Skills loaded` to list exactly the successfully loaded skills declared in the packet; reject undeclared, missing, or sentinel skill names.
Require every created, modified, deleted, or unchanged file row to be authorized by the packet's `FILES TO WRITE`, and require each authorized target to be reconciled by an outcome row.
Require `BLOCKED` to contain non-`None` blocker fields and a `None` deliverable.
Require `COMPLETE` and `PARTIAL` to contain `None` blocker fields and a non-empty, non-`None` deliverable.
Treat all content after the first `## Deliverable` heading as arbitrary Markdown payload specified by `## EXPECTED OUTPUT`; do not parse later headings as envelope sections.

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
   Convert known empty `filesToRead`, `filesToWrite`, and `skills` arrays to `None` instead of the unknown marker.
5. **Construct complete plaintext packet** — Build a well-formed plaintext delegation packet with all 8 sections present using the Packet Template.
   Every section header (`## PURPOSE`, `## DETAILS`, etc.) must appear, even if its content is the UNKNOWN marker.
   - **FILES TO READ: list required files only.** Include the files the worker must read before starting.
     Leave purposeful related-file discovery to the worker contract.
     Avoid unbounded patterns.
     Include glob patterns only when the task explicitly requires broad file sets.
   - **FILES TO WRITE: preserve all expected writes.** If the input provides multiple `filesToWrite` entries, include every literal path or bounded path pattern as a comma-separated list.
     Do not collapse multiple outputs to one path.
6. **Validate all sections present** — Confirm the constructed packet has exactly 8 sections and none are missing.
   If sections are absent, report a clear error describing which sections are missing and stop.
7. **Invoke the worker** — Invoke the `task` tool with `subagent_type: "worker"`, `description` set to the inferred PURPOSE content, `prompt` set to the full plaintext packet, and `command` set to the inferred PURPOSE content.
8. **Validate the worker result** — Confirm the result starts with `Worker Result` and contains the remaining envelope sections in order. Validate the envelope against the original packet's declared skills, authorized writes, requested outcomes, and expected payload.
   Require exactly one valid status row before `File Changes`.
    Validate the report rows, table headers, data rows, blocker fields, reconciliation, and deliverable against the Output contract. A loaded skill alone is never evidence that the packet's required outcomes completed.
   Return `BLOCKED: task-delegation received a malformed worker result envelope.` when validation fails.
9. **Return the worker result unchanged** — Preserve the complete valid envelope without rewrapping, extracting, or modifying `Deliverable`.

This is a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Accept any single-task input format without rejecting a format category.
- Reject unresolved multi-task input.
- Always produce exactly 8 sections in the output packet — no more, no less.
- Mark any uninferable field with the explicit marker `UNKNOWN — not provided in input`; do not fill with default values, placeholder text, or guesses.
- Use loose mapping; do not require exact field names.
- Preserve every explicit required read and write target from the selected task.
- Never add write targets.
- Preserve explicit bounded write patterns without broadening them.
- Reject recursive wildcards and repository-wide write patterns.
- Permit the worker to discover task-related read context under the worker contract.
- After construction, do not modify, re-encode, or further transform the plaintext packet.
- If the constructed packet is missing sections, report a clear error describing which sections are absent and do not invoke the worker.
- Reject legacy raw payloads and `PARTIAL:` or `BLOCKED:` worker prefixes as malformed worker result envelopes.
- Never interpret `None` or `UNKNOWN — not provided in input` as a literal path or skill name.

## Docs

See `./reference/README.md` for documentation of supporting files.
