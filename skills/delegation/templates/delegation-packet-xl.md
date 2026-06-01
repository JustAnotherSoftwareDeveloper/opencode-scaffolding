# Delegated Worker Handoff

You are working as a delegated worker for <orchestrator-name>.

Load skill: <skill-name or none>

## Objective

<One bounded objective.>

## Context

<Relevant proposal, plan, state, prior findings, constraints, and assumptions.>
<For highest-risk work: include failed prior attempts, conflicting evidence, and escalation triggers.>

## Inputs

<User requirement slice, files, plan sections, state files, or other inputs to use.>

## Files in scope

- <path-or-glob the worker may read or edit>

## Files out of scope

- <path-or-glob the worker must not touch>

## Do

- <specific action>
- Report partial progress if blocked.
- Follow task-mode guardrails for analysis/review, coding/config, documentation, synthesis, and web research.

## Do not

- <specific prohibition>
- Do not bypass task-mode guardrails.
- Do not perform work outside your designated task mode.
- Do not work around blockers silently.

## State updates

- <state file the worker may update, or "none">
- Update status and work_log on each meaningful milestone.
- Do not edit orchestrator-owned state files unless explicitly listed here.

## Recovery

- If blocked or uncertain, stop and report the blocker with attempted actions and recommended escalation size/family.

## Verification

- <command, parse check, read check, or review criterion>
- Verify correctness and idempotency.

## Return

- Findings or changes
- Files touched
- Verification performed and results
- State files updated
- Blockers, risks, or unresolved questions
- Recommended next action if any
