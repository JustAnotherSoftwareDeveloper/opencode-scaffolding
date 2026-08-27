# Proposal To Plan

`proposal-to-plan` - `proposal`, `plan-writer`, `plan-audit` - Moves from a recorded decision through proposal-derived audit handoffs.

**Use when:** A decision record and its supporting evidence require a source-preserving task plan.

## Purpose

This workflow preserves decision evidence through plan publication and the audit
handoff. The proposal workspace provides decision context, scope boundaries,
requirements, and open engineering decisions for `plan-writer`.

## Sequence

- `Proposal recorded` is owned by `proposal` and is represented by the proposal
  workspace, its source set, and its authoritative baseline.
- `Plan authored` is owned by `plan-writer` and is represented by the plan workspace
  with `tasks.json`, `tasks.md`, and preserved source context.
- A published proposal-derived plan transitions to `Audit pending`, owned by
  `plan-audit`, with the exact plan snapshot and proposal baseline identified.
- `plan-audit` produces either `Audit passed` or `Audit findings` in its external
  Markdown report. Findings identify bounded remediation by finding ID; the audit
  owner does not repair the plan.
- Findings transition to a `plan-writer`-owned bounded fix, then to a revised plan
  and a mandatory re-audit. The full state description is in the
  [proposal-derived audit lifecycle](./proposal-derived-audit-lifecycle.md).

## Artifacts

- Proposal workspace.
- Proposal source documents and any additional planning evidence.
- Plan workspace containing `tasks.json` and `tasks.md`.
- External audit report containing the pass or finding disposition.
- Revised plan snapshot when a bounded finding fix exists.

## Notes

- Plan source documents remain preserved within the plan workspace.
- Source-derived constraints remain present in task context.
- Open engineering decisions remain labeled as `Open Question:` in task context.
- Unverified material remains labeled as `Assumption:` in task context.
- Proposal-derived requirements, decisions, constraints, and acceptance criteria
  retain a `Proposal-derived:` label in plan context.
- Audit findings retain their exact finding IDs and the impact that bounds any
  plan-writer fix.
