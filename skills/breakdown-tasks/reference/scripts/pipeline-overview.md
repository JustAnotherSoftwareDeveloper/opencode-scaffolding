# Pipeline Overview

Collect skills twice with phase-specific filters, assign inline, and publish.

## Sequence

1. Run `collect-skills --class planning`. Feed its stdout JSON into planning selection.
2. Load every materially relevant planning skill. Draft tasks without `skills`.
3. Run `collect-skills --class operation --class documentation`. Feed its stdout JSON into task-skill assignment.
4. Select one to three skills per task inline. Inspect each contract at its collector-winning path.
5. Write the completed draft and publish with `init-task-packet --output-dir .tasks`.
6. Validate and fix with `validate-task-structure --auto-fix --state-file` in a retry loop.

## Failure Rules

- Non-zero collector exit blocks immediately.
- Name absent from the relevant array blocks.
- Stale path, contract mismatch, or invalid assignment blocks.
- No partial output is published.
