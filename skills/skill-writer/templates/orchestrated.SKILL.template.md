---
name: <<skill-name>>
description: "Use when <<trigger description for multi-phase coordination>>."
class: orchestrated
---

# <<Skill Name>>

One-line description of the workflow this orchestrator coordinates.

## Delegated Backing Skills

- <<Skill A>> — <<purpose>>. Input from orchestrator: <<input>>. Output to orchestrator: <<output>>.
- <<Skill B>> — <<purpose>>. Input from orchestrator: <<input>>. Output to orchestrator: <<output>>.

## Phases

1. **Phase 1: <<name>>** — Owner: <<owner>>. Entry: <<entry condition>>. Action: <<action>>. Exit: <<exit condition>>.
2. **Phase 2: <<name>>** — Owner: <<owner>>. Entry: <<entry condition>>. Action: <<action>>. Exit: <<exit condition>>.
3. **Phase 3: <<name>>** — Owner: <<owner>>. Entry: <<entry condition>>. Action: <<action>>. Exit: <<exit condition>>.

## State Ownership

- <<Phase / File>> — owned by <<component>>.
- <<Phase / File>> — owned by <<component>>.

## Quality Gates / Checkpoints

- Condition: <<gate condition>>. If fail: <<action>>.
- Condition: <<gate condition>>. If fail: <<action>>.

## Failure Handling

- <<Failure mode>> — <<recovery path: retry / skip / escalate>>.
- <<Failure mode>> — <<recovery path: retry / skip / escalate>>.

## Verification Checklist

- <<verification step>>
- <<verification step>>