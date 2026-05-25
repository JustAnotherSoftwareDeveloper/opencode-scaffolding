---
description: Generate an executable runbook from a plan slug, or the most recent plan if none specified
---

Generate a v2 XML runbook workspace from a plan slug. If no slug is provided, use the most recent plan in `.plans/`.

`$ARGUMENTS`

## Workflow

### If `$ARGUMENTS` names a plan slug or path
1. Locate `.plans/<slug>.md` (or the full path if given).
2. Verify the plan has `status: approved` in its frontmatter, or ask the user for authorization.
3. Load the `runbook` skill.
4. Create `.runbooks/<unix-timestamp>-slug/main.xml` plus one `steps/<step-id>.xml` file per executable step.
5. Validate the v2 runbook workspace: `uv run --project scripts/python validate-runbook .runbooks/<runbook_id>/main.xml`.
6. Run embedded quality check via `analysis-*` worker.
7. Report the artifact path, status, and next step (state init + execution).

### If `$ARGUMENTS` is empty
1. List `.plans/` directory entries sorted by name.
2. Pick the most recent `.plans/<ts>-slug.md`.
3. Verify it has `status: approved` (or ask for user authorization).
4. Proceed with runbook generation as above.

### If no approved plan is found
- Report that no approved plan is available and the user should run `/plan` first.

## Constraints

- Do not implement. This command creates a runbook only.
- Do not initialize state; use `/execute` for state initialization and execution.
- Use v2 XML by default. Legacy `.runbooks/<id>/runbook.json` creation is only for explicit v1 compatibility requests.
