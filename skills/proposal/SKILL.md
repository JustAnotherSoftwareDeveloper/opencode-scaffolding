---
name: proposal
description: Create a bounded proposal before planning or execution, covering scope, alternatives, risks, and acceptance criteria.
---

# Proposal Skill

Use this skill before creating a runbook or editing the harness when the requested outcome is non-trivial, ambiguous, or likely to affect agents, skills, commands, permissions, or orchestration behavior.

## Inputs

- User goal or requested change.
- Relevant harness state: existing agents, skills, commands, config, runbooks, and constraints.
- Known failures, migration targets, or prior review findings.

## Output Format

Return exactly these sections:

## Goal
Restate the requested outcome in one or two sentences.

## Proposed Scope
Describe what should change and what should explicitly remain unchanged.

## Recommended Approach
Name the recommended path and why it is the smallest correct approach.

## Alternatives Considered
List viable alternatives and why they are not preferred.

## Risks And Unknowns
Call out ambiguity, compatibility risks, permission risks, and places where the harness may need review.

## Acceptance Criteria
List concrete checks that prove the proposal succeeded.

## Decision Needed
State whether execution can proceed or whether a human decision is required first.

## Rules

- Do not write an execution plan here. Planning is handled by the `plan` skill.
- Do not implement changes.
- Prefer small, reversible changes over large rewrites.
- If critical facts are missing, ask targeted questions instead of guessing.
- Treat the existing worker agents as the default delegation pool unless the proposal specifically creates new workers.
