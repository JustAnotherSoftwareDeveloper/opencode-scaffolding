# Proposal To Plan

`proposal-to-plan` - `proposal`, `plan-writer`, `plan-audit` - Traces an authorized proposal decision through a source-preserving plan and its proposal-derived audit handoffs.

**Use when:** A decision record and its supporting evidence require a source-preserving task plan.

## Purpose

This workflow preserves decision evidence through plan publication and the audit
handoff. The proposal workspace provides decision context, scope boundaries,
requirements, and open engineering decisions for `plan-writer`.

## Passive Boundary

This reference describes workflow states, artifacts, owners, and handoffs only. It is
passive and non-transitive: it grants no executable steps, tools, writes, delegation,
skill loading, approval, or completion authority. `plan-audit` is an independent,
read-only report owner; `plan-writer` alone owns bounded plan correction. The full
proposal-derived audit lifecycle is described in the
[proposal-derived audit lifecycle](./proposal-derived-audit-lifecycle.md).

## Sequence

1. `Proposal recorded` is owned by `proposal` and is represented by the proposal
   workspace, its source set, and its authoritative baseline.
2. `Proposal authorization confirmed` is the required gate before planning. It
   requires either a recorded accepted lifecycle state or `decision-ready` plus
   explicit planning authorization from the recorded decision authority. Recording,
   publication, validation, `review-ready`, and recency do not cause this transition.
3. `Plan authored` is owned by `plan-writer` and is represented by the plan workspace
   with `tasks.json`, `tasks.md`, and preserved source context.
4. A published proposal-derived plan transitions to `Audit pending`, owned by
   `plan-audit`, with the exact plan snapshot and proposal baseline identified.
5. `plan-audit` produces either `Audit passed` or `Audit findings` in a new external
   Markdown report under repository-root `.audit/`:
   - **`Audit passed`:** the report records the pass disposition.
   - **`Audit findings`:** the read-only report identifies bounded remediation by
     stable finding ID and impact; it does not change the audited plan.
6. For findings, `plan-writer` makes a bounded correction to `tasks.json` and
   `tasks.md` in the same existing plan workspace, preserving its proposal and source
   context. The resulting revised snapshot requires a new `plan-audit` report under
   `.audit/`; this mandatory re-audit is read-only and applies to that revised
   snapshot. The full state description is in the
   [proposal-derived audit lifecycle](./proposal-derived-audit-lifecycle.md).

## Artifacts

- Proposal workspace.
- Proposal source documents and any additional planning evidence.
- Plan workspace containing `tasks.json` and `tasks.md`.
- External audit report under repository-root `.audit/`, containing the pass or
  finding disposition.
- Revised plan snapshot in the same existing plan workspace when a bounded finding
  correction exists.

## Notes

- Plan source documents remain preserved within the plan workspace.
- Source-derived constraints remain present in task context.
- Open engineering decisions remain labeled as `Open Question:` in task context.
- Unverified material remains labeled as `Assumption:` in task context.
- Proposal-derived requirements, decisions, constraints, and verification criteria
  retain a `Proposal-derived:` label in plan context.
- Audit findings retain their exact finding IDs and the impact that bounds any
  plan-writer fix.
