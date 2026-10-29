# Error Handling And Testing

Integration tests must cover the three-stage direct-selection contract and the explicit
passive task-contract boundary.

## Required Checks

- Each request invokes the collector three times, in separate calls and in this order:
  `--class planning`, `--class operation`, then `--class documentation`. Do not combine
  operation and documentation in one call or repeat collection per task.
- Make the documentation result available before the pre-authoring load. Reconcile the
  exact collector-winning `task-contract` record by name, documentation class, and
  path, then load it before task-boundary authoring.
- Keep the `task-contract` load passive, documentation-only, and non-transitive. It
  adds no workflow steps, authority, tools, writes, delegation, assignments, or
  completion evidence.
- Use the planning result for planning selection. After task boundaries are accepted,
  use the distinct operation and documentation results for task assignments. Each task
  has one operation owner and zero to two documentation assignments; zero is valid
  when no documentation profile adds distinct material value.
- No reranker, selector, score/rank/threshold policy, fallback path, or manual repair
  is invoked.
- Planning loads are uncapped. Reconcile assigned skills against their relevant class
  result by exact identity before and after execution.
- Preserve copied plan sources and non-skill task fields.
- Fail closed on invalid assignments, contract mismatches, and publication errors.
  Retry structural violations with `--auto-fix`.
- Do not replace existing outputs. Leave no partial output.

Use deterministic LLM-selection fixtures or stubs. These checks cover the written
workflow contract, not semantic selection quality or runtime loader enforcement.
