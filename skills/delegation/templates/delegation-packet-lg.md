# Delegated Worker Handoff

You are working as a delegated worker for <orchestrator-name>.

Load skill: <skill-name or none>

## Objective

<One bounded objective.>

## Context
<Relevant proposal, plan, state, prior findings, constraints, and assumptions.>
<For complex tasks, include tradeoffs considered, alternatives ruled out, and any nuanced constraints.>

## Inputs
<User requirement slice, files, plan sections, state files, or other inputs to use.>

## Files in scope
- <path-or-glob the worker may read or edit>

## Files out of scope
- <path-or-glob the worker must not touch>

## Do
- <specific action>
- Include edge-case handling where applicable.
- Follow task-mode guardrails for analysis/review, coding/config, documentation, synthesis, and web research.

## Do not
- <specific prohibition>
- Do not bypass task-mode guardrails.
- Do not perform work outside your designated task mode.
- Do not skip verification steps.

## State updates
- <state file the worker may update, or "none">
- Update this file's status and work_log on meaningful progress.
- Do not edit orchestrator-owned state files unless explicitly listed here.

## Verification
- <command, parse check, read check, or review criterion>
- Verify idempotency where relevant: running twice produces the same result.
- Cross-check affected files after edits.

## Return
- Findings or changes
- Files touched, with line counts if edited
- Verification performed and results
- State files updated and their new status
- Blockers, risks, or unresolved questions
