# Pipeline Overview

Normalize the request, collect skills twice with phase-specific filters, load the
shared task-contract documentation before authoring boundaries, assign inline, and
publish for dispatch.

## Sequence

1. Run `collect-skills --class planning`. Feed its stdout JSON into planning selection.
2. Load every materially relevant planning skill.
3. Run `collect-skills --class operation --class documentation`. Reconcile and load
   the collector-winning `task-contract` documentation record as passive,
   non-transitive context before drafting task boundaries.
4. Apply the decomposition method without `skills`: name the outcome, break it into
   smaller results, split compound results again, connect dependencies and handoffs,
   draft task records, and review the complete set.
5. Select one to three skills per task inline. Inspect each assigned contract at
   its collector-winning path; the passive task-contract record is not an assignment.
6. Write the completed draft and publish with `init-task-packet --output-dir .tasks`.
7. Validate and fix with `validate-task-structure --auto-fix --state-file` in a
   retry loop.

## Failure Rules

- Non-zero collector exit blocks immediately.
- Name absent from the relevant array blocks.
- Stale path, contract mismatch, or invalid assignment blocks.
- No partial output is published.
