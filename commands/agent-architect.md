---
description: Run Agent Architect against a goal or runbook path
agent: agent-architect
---

Use Agent Architect to handle this request:

`$ARGUMENTS`

If `$ARGUMENTS` names a readable plan or runbook file, read it first and execute it as the runbook.

If `$ARGUMENTS` is a goal rather than a file path, start with the orchestrator lifecycle:

1. Load `proposal` when the scope or approach needs judgment.
2. Load `plan` to create a concrete runbook before non-trivial execution.
3. Delegate independent work to the existing worker agents in parallel where possible.
4. Execute the smallest correct harness changes.
5. Load `review-work` and review the completed work before reporting success.
6. Load `retro` after meaningful harness changes and report high-value follow-ups.

Preserve existing worker agents and model IDs unless the request explicitly says to change them.
