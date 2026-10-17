# Error Handling And Testing

Integration tests must cover the three-stage direct-selection contract and the explicit
passive task-contract boundary.

## Required Checks

- Each request makes three distinct collector invocations, in order: `--class planning`,
  `--class operation`, then `--class documentation`. No call combines operation and
  documentation, and collection is not repeated per task.
- The documentation result is available before the pre-authoring load. The exact
  collector-winning `task-contract` record is reconciled by name, documentation class,
  and path, then loaded before task-boundary authoring.
- The task-contract load is passive, documentation-only, and non-transitive; it does
  not add workflow steps, authority, tools, writes, delegation, assignments, or
  completion evidence.
- Planning selection uses the planning result. Task assignments use the distinct
  operation and documentation results only after task boundaries are accepted; each
  task has one operation owner and zero to two documentation assignments, with zero
  valid when no documentation profile adds distinct material value.
- No reranker, selector, score/rank/threshold policy, fallback path, or manual repair is invoked.
- Planning loads are uncapped. Assigned skills are reconciled against their relevant
  class result by exact identity before and after execution.
- Copied plan sources and non-skill task fields are preserved.
- Invalid assignments, contract mismatches, and publication errors fail closed. Structural violations are retried with --auto-fix.
- Existing outputs are not replaced. No partial output remains.

Use deterministic LLM-selection fixtures or stubs; these checks cover the written
workflow contract, not semantic selection quality or runtime loader enforcement.
