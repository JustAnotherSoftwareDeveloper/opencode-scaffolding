# Error Handling And Testing

Integration tests must prove the two-call direct-selection workflow and the explicit
passive task-contract boundary.

## Required Checks

- Two collector invocations run with correct filters: `--class planning` then
  `--class operation --class documentation`.
- The collector-winning `task-contract` record is reconciled by exact name, class,
  and path and loaded before task-boundary authoring.
- The task-contract load is passive, documentation-only, and non-transitive; it does
  not add workflow steps, authority, tools, writes, delegation, assignments, or
  completion evidence.
- Planning loads come from the planning array. Task assignments come from the operation/documentation array.
- No reranker, selector, score/rank/threshold policy, fallback path, or manual repair is invoked.
- Planning loads are uncapped. Task assignment is one to three.
- Names are reconciled against the relevant phase array before and after execution.
- Copied plan sources and non-skill task fields are preserved.
- Invalid assignments, contract mismatches, and publication errors fail closed. Structural violations are retried with --auto-fix.
- Existing outputs are not replaced. No partial output remains.

Use deterministic LLM-selection fixtures or stubs; tests validate orchestration behavior, not semantic selection quality.
