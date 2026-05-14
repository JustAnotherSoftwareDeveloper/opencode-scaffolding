---
description: Generate an engineering plan from a proposal slug, or the most recent proposal if none specified
---

Generate a plan from a proposal slug. If no slug is provided, use the most recent proposal in `.proposals/`.

`$ARGUMENTS`

## Workflow

### If `$ARGUMENTS` names a proposal slug or path
1. Locate `.proposals/<slug>.md` (or the full path if given).
2. Verify the proposal has `status: accepted` in its frontmatter.
3. Load the `plan` skill.
4. Create `.plans/<unix-timestamp>-slug.md` from the proposal.
5. Run embedded quality check via `analysis-*` worker.
6. Report the artifact path, status, and next step (runbook).

### If `$ARGUMENTS` is empty
1. List `.proposals/` directory entries sorted by name (timestamps are in the filename).
2. Pick the most recent `.proposals/<ts>-slug.md`.
3. Verify it has `status: accepted`.
4. Proceed with plan generation as above.

### If no accepted proposal is found
- Report that no accepted proposal is available and the user should run `/proposal` first.

## Constraints

- Do not implement. This command creates a plan only.
- Do not create a runbook; use `/build-runbook` after the plan is approved.
