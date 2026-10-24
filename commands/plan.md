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
6. Before each audit, ensure the repository-root `.audit/` directory exists, creating it if needed. Select a new, nonexistent report path beneath it; never reuse or overwrite an audit report.
7. Load the `plan-audit` skill. Perform the mandatory read-only audit against the authoritative proposal baseline and the new plan workspace, using the declared report path beneath `.audit/`.
8. If the audit passes, report the plan workspace, report path, and disposition. If it is blocked or identifies an upstream decision, proposal, source, or evidence need, stop and report the exact needed input and impact without changing those inputs.
9. For findings with plan-writer-owned remediation, pass the finding IDs and stated impacts, existing plan workspace, and same authoritative proposal baseline to `plan-writer` in bounded correction mode. Correct only that workspace's `tasks.json` and rerender exactly `$PLAN_DIR/tasks.md` with `--overwrite`; preserve packet identity, unrelated content, copied sources, and proposal baseline. Stop rather than widening scope for findings requiring edits outside those two plan files.
10. After each correction, perform a mandatory fresh read-only `plan-audit` against the revised plan workspace and the same authoritative proposal baseline, using another new report path beneath `.audit/`. Repeat the bounded correction and re-audit loop for further plan-writer-owned findings; stop on a pass or a blocked/upstream handoff. Report the plan workspace, all audit report paths and dispositions, and any exact blocked handoff inputs or impacts.

## Constraints

- Do not implement the proposal or execute plan tasks.
- Do not mutate proposal metadata, infer approval, auto-accept a proposal, or auto-approve a plan.
- Do not use an ad hoc worker review in place of `plan-audit`.
- Keep `plan-audit` read-only; audit reports must be new files beneath repository-root `.audit/` and remain external to the audited inputs.
- Keep audit-finding corrections within the existing plan workspace's `tasks.json` and `tasks.md`; do not replace the workspace or modify copied sources or the proposal baseline.
- Do not create a runbook or direct the user to the legacy build-runbook flow.
- If no authorized proposal is available, report the missing authorization or readiness fact without changing it.
