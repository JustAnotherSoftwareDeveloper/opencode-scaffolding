---
description: Initialize state and execute a runbook, or resume the most recent runbook if none specified
---

Initialize state and execute a runbook. If no runbook slug is provided, use the most recent runbook in `.runbooks/`.

`$ARGUMENTS`

## Workflow

### If `$ARGUMENTS` names a runbook slug or path
1. Locate `.runbooks/<slug>/main.xml` first. If absent, fall back to legacy `.runbooks/<slug>/runbook.json` (or use the full path if given).
2. Verify the runbook has `status: approved`, or ask the user for authorization.
3. Read the runbook as the authoritative execution contract.
4. Initialize state with the selected source: `uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/main.xml` for v3/v2 XML, or `.runbooks/<runbook_id>/runbook.json` only for legacy v1. For v3, this creates or updates runbook-local `state.xml` and default manifest indexes.
5. Execute each step according to the runbook dependency graph, dispatching worker delegations serially—one delegated worker at most in flight—then reconcile state after each delegation completes.
   - Decompose steps into atomic units.
   - Load the `delegation` skill to construct bounded handoffs for the configured worker.
   - Route work via `task` to configured harness subagents.
   - Reconcile state after each step.
6. Run verification gates defined in the runbook.
7. Report completion with state summary and any remaining risks.

### If `$ARGUMENTS` is empty
1. List `.runbooks/` directory entries sorted by name.
2. Pick the most recent `.runbooks/<ts>-slug/`.
3. Read `.runbooks/<ts>-slug/main.xml` if present; otherwise read legacy `.runbooks/<ts>-slug/runbook.json`.
4. Check for existing state:
   - For v3, read `.runbooks/<ts>-slug/state.xml`.
   - For transitional v2 or legacy v1, read `.state/<ts>-slug/` only as backward compatibility.
   - If state exists and execution was in progress: resume from the active step.
   - If state exists and execution was complete: report and ask if re-execution is desired.
   - If no state exists: initialize and execute from start.
5. Proceed with execution as above.

### If no runbook is found
- Report that no runbook is available and the user should run `/build-runbook` first.

## Constraints

- Read the runbook first and treat it as the authoritative contract.
- Prefer v3 `main.xml`; use `runbook.json` only as legacy compatibility for old artifacts.
- Preserve existing user changes and unrelated files.
- Use only configured harness subagents for execution and review.
- Use embedded quality checks before claiming step success.
- Update state after every meaningful transition.
