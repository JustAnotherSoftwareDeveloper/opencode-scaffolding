---
name: task-executor
description: "Use when executing exactly one approved canonical task packet inline without worker delegation."
selection:
  role: owner
  tags:
    actions: [execute packet]
    inputs: [canonical task packet]
    outputs: [verified task result]
    constraints: [single inline execution]
  use_when: [one approved canonical task packet must be executed without delegation]
  not_for: [delegating a task to another worker]
class: inline
---

# Task Executor

Execute one approved canonical task object inline in the current primary-agent
context. This skill is the execution engine used by `executor-simple`; it does not
replan, reassign, or delegate the task.

## Input

Accept exactly one task object conforming to the `TaskPacket` definition in
`skills/breakdown-tasks/schema/task-packet.schema.json`. This includes execution
fields and authoring metadata such as `taskId`, `verificationCoverage`, `dependencies`,
`antiPatternSignals`, `purposeOutputAlignment`, and optional `couplingRationale`.

Reject a packet root containing `summary` and `tasks`; the caller must select one task
before invoking this skill. Treat the task object as immutable.

## Output

Return the deliverable defined by `expectedOutput`.

- Return the clean deliverable when execution completes and all declared verification
  checks pass.
- Return `PARTIAL: <deliverable and explanation>` when a useful deliverable exists but
  a declared verification check fails or a non-blocking portion remains incomplete.
- Return `BLOCKED: <reason>` when validation, a required skill/input, or execution
  prevents producing a usable deliverable.

## Skill Contract

The packet's `skills` array is complete for inline execution. Do not add, substitute,
infer, or transitively load task skills.

For a canonical executable task, require the declared composition established during
assignment:

- exactly one `class: operation` owner;
- zero to two `class: documentation` skills;
- no planning, delegated, or inline skill as a task assignment.

Load every declared skill through the skill tool before task side effects, in listed
order. The operation skill owns execution. Documentation skills are passive context:
they may inform implementation but do not add authority, workflow steps, writes,
delegation, or completion evidence.

If a declared name cannot load, a loaded skill's class violates the required
composition, or more than one operation owner is declared, return `BLOCKED` before
executing the task. Do not use `generic-executor` or any other skill as an undeclared
fallback. Skill-path/collector reconciliation belongs to task authoring and approval;
the inline executor receives only approved skill names and must not reconstruct
collector metadata that is absent from the task packet.

## Execution Plan

1. Validate that the input is one canonical `TaskPacket` object and not a packet root.
2. Load each declared skill exactly once in listed order before task side effects.
3. Confirm the loaded set is exactly one operation owner plus zero to two passive
   documentation skills. Block on any unavailable skill or class-composition mismatch.
4. Read every path in `filesToRead` before execution. Return `BLOCKED` when a required
   input cannot be read.
5. Execute `executionInstructions` in ascending `step` order using the loaded operation
   workflow and passive documentation context.
6. Write the declared `filesToWrite` as required by the task. Do not broaden the write
   set unless the task's own context or instructions explicitly authorize a bounded
   related location.
7. Run every declared top-level `verification` check when present. Treat absent
   `verification` as no additional top-level checks beyond the task instructions and
   `verificationCoverage` metadata.
8. Produce the result described by `expectedOutput`.

## Capability Boundary

- Do not invoke the `task` tool or delegate to workers/subagents.
- Do not change task purpose, expected output, instructions, verification, assignment,
  dependencies, or authoring metadata.
- Do not load skills outside the declared `skills` array.
- Do not load planning skills for ordinary execution.
- Do not discover or read unrelated files. Purposeful related discovery is permitted
  only when the task's `context` or `executionInstructions` authorizes it.
- Do not write outside `filesToWrite` except for a bounded related location explicitly
  permitted by the task itself.
- Do not use external retrieval unless the task explicitly authorizes it.
- Attempt remediation only while it remains within the immutable task contract.

## Self-Validation

- [ ] Input is one canonical `TaskPacket`, not a packet root.
- [ ] Exactly one declared operation owner loaded successfully.
- [ ] Zero to two declared documentation skills loaded as passive context.
- [ ] No undeclared, planning, delegated, or inline task skill was loaded.
- [ ] Required reads occurred before task execution.
- [ ] Writes remained within the task's declared or explicitly authorized bounded scope.
- [ ] Declared verification ran before a clean result.
- [ ] No worker or task-tool delegation occurred.

## Docs

See [Reference](./reference/README.md) for additional inline-execution guidance.
