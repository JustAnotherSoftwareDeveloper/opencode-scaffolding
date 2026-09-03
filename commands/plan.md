---
description: Create and audit an engineering plan from an authorized one-document proposal
---

Create a plan from the proposal path or slug in `$ARGUMENTS`; when omitted, inspect the most recent active proposal workspace.

## Workflow

1. Resolve the selected active workspace to `.proposals/<epoch-ms>-<slug>/PROPOSAL.md`. Read an explicitly selected historical single-file proposal only when its documented compatibility boundary permits planning; never migrate it.
2. Read lifecycle `status`, `readiness`, `decision-owner`, and `source-documents` from `PROPOSAL.md` frontmatter without modifying them.
3. Authorize planning only when either the proposal records an accepted lifecycle state or it is `decision-ready` and the invocation explicitly comes from the recorded decision authority. Do not infer acceptance from `review-ready`, recency, or command invocation alone.
4. Load the `plan-writer` skill. Pass `PROPOSAL.md` plus every declared copied source as explicit source documents.
5. Create the plan-writer workspace containing copied sources, `tasks.json`, and `tasks.md`; do not invent plan `INDEX.md` or `metadata.md` artifacts.
6. Load the `plan-audit` skill. Perform the mandatory read-only audit against the authoritative proposal baseline and the new plan workspace.
7. Report the plan workspace, audit report path, audit disposition, and exact blocked handoff inputs or impacts. A findings disposition returns to bounded plan-owned correction followed by mandatory re-audit.

## Constraints

- Do not implement the proposal or execute plan tasks.
- Do not mutate proposal metadata, infer approval, auto-accept a proposal, or auto-approve a plan.
- Do not use an ad hoc worker review in place of `plan-audit`.
- Do not create a runbook or direct the user to the legacy build-runbook flow.
- If no authorized proposal is available, report the missing authorization or readiness fact without changing it.
