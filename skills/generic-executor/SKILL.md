---
name: generic-executor
description: "Use when executing one bounded ordinary file-maintenance result without a specialized owner."
selection:
  role: owner
  tags:
    actions: [execute maintenance]
    inputs: [explicit specification]
    outputs: [maintenance result]
  use_when:
    [executing one bounded ordinary file-maintenance result without a specialized owner]
  not_for:
    [commands, agents, skills, scripts, plans, proposals, audits, destructive operations, packet orchestration, delegation, specialized-owner work]
class: operation
---

# Generic Executor

Execute exactly one bounded ordinary file-maintenance result when no specialized operation owns the output.

## Normalize Input

1. Require the caller to supply an explicit specification with these mandatory fields: `filesToRead`, `filesToWrite`, `instructions`, `expectedOutput`, and `verification`.
2. Reject any specification that is missing a mandatory field or that targets commands, agents, skills, scripts, plans, proposals, audits, runbooks, or any output owned by a specialized operation.
3. Reject any specification with ambiguous authority: unrecognized file patterns, write targets outside the declared `filesToWrite` boundary, or instructions that require authority outside this skill's contract.
4. Return `BLOCKED: <reason>` when any input rule fails.
   Never infer, repair, or substitute missing fields.

## Procedure

1. Validate the specification object: confirm `filesToRead`, `filesToWrite`, `instructions`, `expectedOutput`, and `verification` are present and non-empty.
2. Confirm every write target is an ordinary repository file (not a command, agent, skill, script, plan, proposal, audit, runbook, or configuration file owned by a specialized operation).
3. Read every path in `filesToRead`.
   Return `BLOCKED: Required file '<path>' is unavailable` when a required path cannot read.
4. Execute `instructions` in order.
   Do not deviate, optimize, or reorder.
5. Write every path in `filesToWrite`.
   Do not write outside the declared boundary.
6. Run every check declared in `verification` against the completed result.
7. Produce the result described by `expectedOutput`.

## Exclusions

This skill must never act as:
- A `task-executor` replacement or packet executor.
- A skill loader or fallback for unowned requests.
- A worker delegation dispatcher.
- An automatic, lexical, nearest-match, or collector-failure fallback.
- A planning, proposal, or audit operation.
- A destructive-operation authority.

## Self-Validation

- [ ] Specification contains all five mandatory fields and each is non-empty.
- [ ] No write target escapes `filesToWrite` or targets a specialized-owner path.
- [ ] Every file in `filesToRead` was read before execution.
- [ ] Every instruction was executed in order without deviation.
- [ ] Every declared verification check was run and reported.
- [ ] No skill was loaded, no worker was delegated, and no task-executor packet was processed.
- [ ] No automatic, lexical, nearest-match, or collector-failure fallback was applied.

## Docs

See `./reference/README.md` for the ordinary-file boundary and input summary.
