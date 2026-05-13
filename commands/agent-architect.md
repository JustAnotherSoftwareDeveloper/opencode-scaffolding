---
description: Run Agent Architect against a goal, proposal, plan, resume request, or lesson request
agent: agent-architect
---

Use Agent Architect to handle this request:

`$ARGUMENTS`

## Routing

If `$ARGUMENTS` names a readable `.proposals/*.md` file:

- Read the proposal.
- If it is accepted, offer or proceed to create a plan in `.plans/` when authorized.
- If it is draft or needs clarification, continue the proposal workflow.

If `$ARGUMENTS` names a readable `.plans/*.md` file:

- Read the plan first and treat it as the runbook.
- Confirm or initialize `.state/<plan_slug>/`.
- Execute only when the plan is approved or the user explicitly authorizes execution.

If `$ARGUMENTS` requests resume behavior:

- Locate `.state/<plan_slug>/metadata.json`.
- Read `.state/<plan_slug>/MAIN.md`.
- Read the active step file.
- Resume from recorded state.

If `$ARGUMENTS` requests lesson capture, or meaningful work completes with reusable guidance:

- Load `lesson-writer`.
- Create `.lessons/<unix-timestamp>-slug.md` when warranted.

If `$ARGUMENTS` is a goal rather than a file path:

- Start with `proposal` unless the task is trivial.
- Use `plan` before non-trivial execution.
- Delegate independent work to sized workers in parallel where safe.
- Use embedded quality checks with appropriately sized `analysis-*` workers before reporting success.
- Use `retro` after meaningful harness changes.

## Constraints

- Preserve existing worker agents and model IDs unless the request explicitly says to change them.
- Preserve `$ARGUMENTS` as the free-form command input.
- Do not create additional command files unless explicitly requested.
