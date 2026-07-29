# Pipeline Overview

Run four phases against one frozen caller-root inventory.

## Phase A — Decomposition

1. Load relevant planning references.
2. Produce `{summary, tasks}` without skills.
3. Preserve complete task context and atomic boundaries.

## Phase B — Assignment

1. Preserve the caller root before invoking `uv --directory`.
2. Collect operation and documentation skills once.
3. Store the inventory under the caller task workspace.
4. Pass the caller root and frozen inventory to `generate-task-json`.
5. Use Qwen mode for authoritative assignment.
6. Use shadow mode with a required diagnostics path for comparison.
7. Use lexical mode only for explicit rollback.
8. Capture the generated relative path.

## Phase C — Read-Only Audit

1. Read the frozen inventory.
2. Verify assignment membership and semantic fit.
3. Verify atomicity, circular references, and cross-task consistency.
4. Block defects without mutating the generated packet.

## Phase D — Blocking Validation

1. Run `validate-task-structure` against the generated path.
2. Omit `--auto-fix`.
3. Block every validation failure.
4. Preserve ranking diagnostics as packet evidence.
5. Remove the temporary inventory after success.
6. Return the generated path under `Deliverable`.

## Failure Rules

- Keep stdout machine-readable on success.
- Send errors to stderr.
- Publish no task file after input, ranking, diagnostics, or validation failure.
- Re-run generation after an assignment defect.
- Do not repair generated assignments in later phases.
