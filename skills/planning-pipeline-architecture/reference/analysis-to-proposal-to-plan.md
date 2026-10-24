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
4. Proposal authorization is confirmed through a recorded accepted lifecycle state,
   or through `decision-ready` plus explicit authorization from the recorded
   decision authority. Recording, validation, `review-ready`, and recency do not
   authorize the transition.
5. The authorized proposal workspace and source evidence form plan sources.
6. The plan workspace records executable tasks and rendered task documentation.
7. The published proposal-derived plan enters the audit-pending state. `plan-audit`
   produces an independent, read-only report under the repository-root `.audit/`,
   recording either a pass or findings.
8. For findings, `plan-writer` makes a bounded correction to `tasks.json` and
   `tasks.md` in the same existing plan workspace, limited by the finding IDs and
   impact while preserving proposal and source context. The revised plan requires a
   mandatory read-only re-audit by `plan-audit`, with its new report under
   repository-root `.audit/`. See the
   [proposal-derived audit lifecycle](./proposal-derived-audit-lifecycle.md) for the
   full state transitions.

## Passive Boundary

This reference describes stages, artifacts, and handoffs only. It is passive and
non-transitive: it grants no executable steps, tools, writes, delegation, skill
loading, approval, or completion authority. `plan-audit` owns independent read-only
reports; `plan-writer` alone owns bounded plan correction.

## Artifacts

- Persisted analysis document.
- Supporting evidence documents.
- Proposal workspace containing `PROPOSAL.md` with Implementation Details, Verification Criteria, and Questions sections, plus copied sources.
- Plan workspace containing `tasks.json` and `tasks.md`.
- Independent audit report under repository-root `.audit/`, external to the audited
  plan; a finding-driven revised plan remains in the same existing plan workspace.

## Notes

- Each stage retains a different purpose and output contract.
- The analysis artifact supplies reasoning context.
- The proposal artifact supplies the decision record.
- The plan artifact supplies executable task planning.
- The audit artifact is a distinct report under repository-root `.audit/` and supplies
  an independent pass or finding disposition. Findings return to a bounded
  `plan-writer` correction in the same existing plan workspace, followed by mandatory
  read-only re-audit.
- Assumptions and open engineering decisions remain traceable across the lifecycle.
