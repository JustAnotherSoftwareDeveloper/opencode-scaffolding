# Boundary Review Signals

Use these operation-specific signals to trigger review against the loaded
`task-contract` documentation skill. The shared owner defines atomicity, dependency,
coupling, traceability, and metadata meaning; these examples do not replace that
contract.

## Hidden Independent Work

- A broad purpose contains several questions or changes.
- A lifecycle label hides analysis, implementation, and review concerns.
- A final document is used to merge independently reviewable findings.
- Implementation and a separately requested test artifact share one task.
- Research that determines later scope or acceptance is hidden inside implementation.
- Discovery, analysis, recommendation, authoring, implementation, and verification
  are bundled as one lifecycle task.
- Work is retained because an intermediate result is small or was not explicitly
  requested.

## Unsupported Coupling Signals

- The rationale names only a shared topic, file, destination, release, or skill.
- Dependency or shared-destination claims are sent back to the shared dependency
  and coupling reference for evidence review.
- Several outputs are called a package without one shared result.
- Verification checks unrelated results under one task.

## Invalid Granularity Decisions

- A fixed task count is chosen before concerns are inventoried.
- One file, step, or skill is required per task.
- Tasks are merged to fit an available skill.
- A sentence containing multiple action verbs is accepted without testing each verb
  as a separate result.
- Fine-grained tasks are merged merely because the author fears over-splitting.

## Invalid Assignment

- Skills are assigned before operation and documentation profiles are collected.
- A fallback skill is forced when no contract matches.
- A selected skill changes an already established boundary.

Use [Atomicity Examples](atomicity-examples.md) for short contrasts and
[Worked Decomposition Examples](decomposition-examples.md) for complete records,
failure routes, and set review. Use [Core Rules](core-rules.md) for the operation
procedure and the named references exposed by the loaded documentation skill for
authoritative boundary semantics.
