# Analysis To Proposal To Plan

`analysis-to-proposal-to-plan` - `generic-analysis`, `proposal`, `plan-writer`, `plan-audit` - Connects assessment, decision recording, executable planning, and proposal-derived audit handoffs.

**Use when:** The request begins with material uncertainty, requires a durable decision, and ends with an executable plan.

## Purpose

This workflow preserves the distinction between understanding a problem, deciding on a response, and planning approved work.
Each stage adds a distinct artifact without replacing the artifact of the prior stage.

## Sequence

1. Analysis establishes the evidence-calibrated assessment.
2. The persisted assessment and supporting evidence form proposal sources.
3. The proposal workspace records the decision, trade-offs, requirements, and open engineering decisions.
4. The proposal workspace and source evidence form plan sources.
5. The plan workspace records executable tasks and rendered task documentation.
6. The published proposal-derived plan enters the audit-pending state described in
   the [proposal-derived audit lifecycle](./proposal-derived-audit-lifecycle.md).

## Artifacts

- Persisted analysis document.
- Supporting evidence documents.
- Proposal workspace containing `PROPOSAL.md` and `implementation.md`.
- Plan workspace containing `tasks.json` and `tasks.md`.

## Notes

- Each stage retains a different purpose and output contract.
- The analysis artifact supplies reasoning context.
- The proposal artifact supplies the decision record.
- The plan artifact supplies executable task planning.
- The audit artifact supplies an independent pass or finding disposition; findings
  return to a bounded `plan-writer` fix and mandatory re-audit.
- Assumptions and open engineering decisions remain traceable across the lifecycle.
