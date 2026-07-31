---
name: task-executor
description: "Use when executing exactly one canonical task packet inline without worker delegation."
schema_version: "1.0"
cues:
  - {facet: operation, value: "execute-task-packet", primary: true}
  - {facet: subject, value: "canonical task packet"}
  - {facet: constraint, value: "single inline execution"}
  - {facet: outcome, value: "verified task result"}
relationships:
  - {role: owner, rationale: "owns single-packet inline execution"}
class: inline
---

# Task Executor

Execute one canonical task packet inline.

## Input

Accept exactly one task object with `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, and `expectedOutput`.

- Accept `verification` when present.
- Reject a root object containing `summary` and `tasks`.
- Reject a task with missing, invalid, duplicate, or additional fields.
- Reject task skills `task-delegation` and `dispatch-decompose` before side effects.

## Output

Return the deliverable defined by `expectedOutput`.

- Return the clean deliverable when all declared verification checks pass.
- Treat absent `verification` as no verification checks.
- Return `PARTIAL: <deliverable and explanation>` when the deliverable exists but a declared verification check fails or remains incomplete.
- Return `BLOCKED: <reason>` when validation, required input, or execution prevents producing the deliverable.

## Execution Plan

1. Validate the input object against the canonical single-task contract.
2. Reject contradictions and prohibited delegation skills before reading, writing, or executing.
3. Load every skill named in `skills` in listed order.
4. Return `BLOCKED: Skill '<name>' is unavailable` when a named skill cannot load.
5. Read every path in `filesToRead` before execution.
6. Return `BLOCKED: Required file '<path>' is unavailable` when a required path cannot read.
7. Execute `executionInstructions` in ascending `step` order.
8. Write every path in `filesToWrite` unless blocked.
9. Run every declared `verification` check against the completed deliverable.
10. Produce the result described by `expectedOutput`.

This is a single-pass process.
Treat direct loading of task-declared skills as inline context acquisition.
Do not invoke the `task` tool.
Do not delegate to workers, subagents, or delegation skills.

## Guardrails

- Treat the input task object as immutable.
- Do not load skills outside `skills`.
- Do not discover or read files outside `filesToRead` unless `context` or `executionInstructions` explicitly authorizes related discovery.
- Do not write outside `filesToWrite`.
- Do not use `webfetch` unless `executionInstructions` explicitly authorizes external retrieval.
- Stop at the first blocking contradiction, missing required file, unavailable skill, or failed instruction.
- Attempt remediation only when it remains within the task's declared reads, writes, instructions, and expected output.
- Do not continue after a blocker.

## Self-Validation

- [ ] Name matches directory name.
- [ ] Description starts with `Use when`.
- [ ] Class is `inline`.
- [ ] Input accepts one canonical task object and rejects root plans.
- [ ] Workflow loads only declared skills and reads all required files before execution.
- [ ] Workflow writes every declared output and restricts writes to `filesToWrite`.
- [ ] Workflow preserves clean, `PARTIAL:`, and `BLOCKED:` status semantics.
- [ ] Workflow contains no worker or task-tool delegation.

## Docs

See [Reference](./reference/README.md) for the task-execution contract.
