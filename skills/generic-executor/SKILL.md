---
name: generic-executor
description: "Use when executing one bounded ordinary maintenance result or maintaining one existing skill workspace."
selection:
  role: owner
  tags:
    actions: [execute maintenance]
    inputs: [explicit specification, existing skill workspace]
    outputs: [maintenance result]
  use_when:
    [executing one bounded ordinary file-maintenance result without a specialized owner, maintaining exactly one existing skill workspace]
  not_for:
    [commands, agents, skill creation, skill taxonomy changes, family-wide skill migrations, skill review, scripts, plans, proposals, audits, destructive operations, packet orchestration, delegation, specialized-owner work]
class: operation
---

# Generic Executor

Execute exactly one bounded ordinary file-maintenance result when no specialized operation owns the output. This operation also owns bounded behavioral maintenance of exactly one existing skill workspace.

## Normalize Input

1. Require the caller to supply an explicit specification with these mandatory fields: `filesToRead`, `filesToWrite`, `instructions`, `expectedOutput`, and `verification`.
2. Reject any specification that is missing a mandatory field or that targets commands, agents, scripts, plans, proposals, audits, runbooks, or any output owned by a specialized operation.
3. Admit skill-workspace work only when it targets exactly one existing `skills/<name>/` workspace and changes only its `SKILL.md`, `reference/**`, or `tests/**` files. The specification must identify the workspace, include the relevant passive `skill-maintenance-reference` documentation in `filesToRead`, and limit its requested result to bounded behavioral maintenance.
4. Reject skill creation, taxonomy changes, family-wide migrations, and skill review, even when their files fit the workspace boundary.
5. Reject any specification with ambiguous authority: unrecognized file patterns, write targets outside the declared `filesToWrite` boundary, or instructions that require authority outside this skill's contract.
6. Return `BLOCKED: <reason>` when any input rule fails.
   Never infer, repair, or substitute missing fields.

## Procedure

1. Validate the specification object: confirm `filesToRead`, `filesToWrite`, `instructions`, `expectedOutput`, and `verification` are present and non-empty.
2. Classify the request as ordinary maintenance or one-workspace skill maintenance. For the latter, confirm that the identified workspace already exists; that every write target is its `SKILL.md`, `reference/**`, or `tests/**`; and that the relevant passive maintenance documentation is declared in `filesToRead`.
3. For ordinary maintenance, confirm every write target is an ordinary repository file (not a command, agent, script, plan, proposal, audit, runbook, or configuration file owned by a specialized operation).
4. Read every path in `filesToRead`. For one-workspace skill maintenance, read every existing target file before changing it and use the passive maintenance documentation only as documentation context.
   Return `BLOCKED: Required file '<path>' is unavailable` when a required path cannot read.
5. Execute `instructions` in order.
   Do not deviate, optimize, or reorder.
6. Write every path in `filesToWrite`.
   Do not write outside the declared boundary.
7. Run every check declared in `verification` against the completed result. For one-workspace skill maintenance, run applicable workspace tests, both shared skill validators on the changed `SKILL.md`, and Markdown lint on every changed Markdown file.
8. Produce the result described by `expectedOutput`.

## Exclusions

This skill must never act as:
- A `task-executor` replacement or packet executor.
- A skill loader or fallback for unowned requests.
- A worker delegation dispatcher.
- An automatic, lexical, nearest-match, or collector-failure fallback.
- A planning, proposal, or audit operation.
- A destructive-operation authority.
- An authority for skill creation, taxonomy changes, family-wide migrations, or skill review.
- An authority to change files outside the one selected existing skill workspace during skill maintenance.

## Self-Validation

- [ ] Specification contains all five mandatory fields and each is non-empty.
- [ ] No write target escapes `filesToWrite` or targets a specialized-owner path, except permitted body, reference, or test maintenance in one existing skill workspace.
- [ ] Every file in `filesToRead` was read before execution.
- [ ] Every instruction was executed in order without deviation.
- [ ] Every declared verification check was run and reported.
- [ ] For skill maintenance, exactly one existing workspace was changed; passive maintenance documentation was read; and applicable workspace tests, both shared validators, and Markdown lint passed.
- [ ] No worker was delegated and no task-executor packet was processed.
- [ ] No automatic, lexical, nearest-match, or collector-failure fallback was applied.

## Docs

See `./reference/README.md` for the ordinary-file and one-workspace maintenance boundaries.
