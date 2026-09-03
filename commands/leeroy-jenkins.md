---
description: Author a proposal and continue only through explicitly authorized planning and mandatory plan audit
---

Apply the active proposal-to-plan lifecycle to `$ARGUMENTS` without treating automation consent as decision approval.

## Workflow

1. Require a topic, decision owner, and explicit source-document paths in `$ARGUMENTS`.
2. Load the `proposal` skill. Create one metadata-bearing `PROPOSAL.md` plus its declared copied sources.
3. Validate the proposal workspace and report its `status`, `readiness`, evidence gaps, and open decisions.
4. Stop after proposal creation unless the proposal records an accepted lifecycle state or it is `decision-ready` and the recorded decision authority explicitly authorizes planning.
5. When planning is authorized, continue to the planning handoff. Load the `plan-writer` skill. Create the plan workspace from `PROPOSAL.md` and its copied sources, and preserve proposal-derived requirements and verification criteria in task context.
6. Load the `plan-audit` skill. Run the mandatory read-only audit. Stop on `BLOCKED`, `FAIL`, or findings requiring bounded plan correction.
7. After any plan-owned correction, run the mandatory audit again. Report the proposal, plan, and audit paths with their independent lifecycle facts.

## Constraints

- Initial automation consent is not proposal acceptance, decision authority, plan approval, or permission to skip quality gates.
- Do not set proposal or plan metadata to accepted or approved.
- Do not continue through unresolved blocking evidence, state conflicts, audit findings, or missing required artifacts.
- Do not create or execute a build runbook; `commands/build-runbook.md` remains outside this proposal migration.
- Do not delegate proposal drafting, replace exact skill ownership, or use fallback assignments.
- Do not rewrite historical `.proposals/` workspaces.
