---
description: Author a proposal and continue only through explicitly authorized planning and mandatory plan audit
---

Apply the active proposal-to-plan lifecycle to `$ARGUMENTS` without treating automation consent as decision approval.

## Workflow

1. Require a topic, decision owner, and explicit source-document paths in `$ARGUMENTS`.
2. Load the `proposal` skill. Create one metadata-bearing `PROPOSAL.md` plus its declared copied sources.
3. Validate the proposal workspace and report its `status`, `readiness`, evidence gaps, and open decisions.
4. Stop after proposal creation unless the proposal records an accepted lifecycle state or it is `decision-ready` and the recorded decision authority explicitly authorizes planning.
5. When planning is authorized, continue to the planning handoff. Load the `plan-writer` skill and create a new plan workspace from `PROPOSAL.md` and all its copied sources. Preserve proposal-derived requirements and verification criteria in task context; do not alter the proposal baseline.
6. Before every audit, ensure the repository-root `.audit/` directory exists, creating it if needed. Select a new, nonexistent report path beneath `.audit/`; never reuse or overwrite a report.
7. Load the `plan-audit` skill and run the mandatory read-only audit against the authoritative proposal baseline and the new plan workspace, using the declared report path beneath `.audit/`. Keep the report external to all audited inputs.
8. If the audit is `BLOCKED` or identifies an upstream decision, proposal, source, or evidence need, stop and report the report path, disposition, and exact needed input and impact without changing those inputs. If it passes without findings, report the plan workspace and audit disposition. If it does not pass and has no plan-writer-owned findings to correct, stop and report its disposition and handoff.
9. For findings with plan-writer-owned remediation, pass their finding IDs and stated impacts, the existing plan workspace, and the same authoritative proposal baseline to `plan-writer` in bounded correction mode. Correct only that workspace's `tasks.json` and rerender exactly `$PLAN_DIR/tasks.md` with `--overwrite`; preserve packet identity, unrelated content, copied sources, and the proposal baseline. Stop rather than widening scope for findings requiring edits outside those two plan files.
10. After each correction, perform a mandatory fresh read-only `plan-audit` against the revised plan workspace and the same authoritative proposal baseline, using another new report path beneath `.audit/`. Repeat the bounded correction and re-audit loop for further plan-writer-owned findings; stop on a pass or a blocked/upstream handoff. Report the proposal and plan paths, every audit report path and disposition, and any exact blocked handoff inputs or impacts.

## Constraints

- Initial automation consent is not proposal acceptance, decision authority, plan approval, or permission to skip quality gates.
- Do not set proposal or plan metadata to accepted or approved.
- Do not infer authorization from `review-ready`, validation, recency, or invocation alone.
- Keep `plan-audit` read-only; audit reports must be new files beneath repository-root `.audit/` and external to the audited inputs.
- Keep audit-finding corrections within the existing plan workspace's `tasks.json` and `tasks.md`; do not replace the workspace or modify copied sources or the proposal baseline.
- Do not continue through unresolved blocking evidence, state conflicts, upstream audit findings, or missing required artifacts.
- Do not create or execute a build runbook; `commands/build-runbook.md` remains outside this proposal migration.
- Do not delegate proposal drafting, replace exact skill ownership, or use fallback assignments.
- Do not rewrite historical `.proposals/` workspaces.
