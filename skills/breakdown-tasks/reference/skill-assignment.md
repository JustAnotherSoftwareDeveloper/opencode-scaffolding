# Direct Skill Selection

Both planning and task assignment use filtered collector output. The operation and
documentation array is collected before task-boundary authoring so the shared
task-contract documentation can be loaded before the draft is written; the same
array remains the sole authority for later task assignment.

## Two Collector Calls

Run `collect-skills --class planning` before planning selection. Run
`collect-skills --class operation --class documentation` before task-boundary
authoring and assignment. The resulting array is the sole authority for both
operation/documentation phases.

## Planning Selection

Show the request and the planning array to the LLM. Load every materially relevant
profile, with no numeric cap. Load only selected names through the skill tool. A
planning load is passive context and does not grant execution or write authority. An
empty selection is valid when no planning concern exists.

Block on a name absent from the planning array.

## Shared Documentation Load

Before authoring task boundaries, reconcile and load the collector-winning
`task-contract` record with its exact `name`, `class: documentation`, and `path`.
This is a passive, documentation-only, non-transitive load. It cannot add workflow
steps, authority, tools, writes, delegation, assignment decisions, or completion
evidence. Any further task-contract reference is an explicit read, not an automatic
recursive load. Block on a missing name, stale or mismatched path, class mismatch,
or load failure.

## Task Assignment

Show the complete accepted draft and the operation/documentation array to the LLM.
For each task:

1. Select exactly one `class: operation` execution owner without changing the
   accepted task boundary.
2. When one specialized operation clearly owns the task's distinct lifecycle,
   artifact contract, orchestration flow, destructive authority, or other special
   execution semantics, select that operation.
3. When no specialized operation semantically fits, select the collector-winning
   `generic-executor` operation as the task's execution owner. A missing specialized
   match is not a blocker.
4. Select zero to two `class: documentation` skills when they materially improve
   execution context. Documentation is passive and never replaces or competes with
   the operation owner.
5. Keep the canonical `skills` field as one flat array containing the one operation
   owner followed by any selected documentation skills. Exclude the passive
   pre-authoring `task-contract` record from executable task assignments.
6. Inspect selected contracts and reconcile every selected name against the collector
   array's winning `name`, `class`, and `path`. Confirm the reconciled class
   composition is exactly one operation and zero to two documentation skills before
   publication.

If more than one specialized operation initially appears relevant, determine which
one owns the bounded result. Do not publish two operation owners. Overlapping skill
coverage is an assignment question, not evidence by itself that the accepted task
boundary should change.

`generic-executor` is a semantic fallback only. It must itself exist in the collector
array as the exact winning `class: operation` record. Block if that record is absent,
stale, substituted, mismatched, or cannot be loaded. Do not use it to conceal a
collector failure, a failed required skill load, or an unresolved assignment to a
known specialized owner.

Block on any selected name absent from the operation/documentation array, stale or
substituted path, class mismatch, failed required load, more than one operation owner,
no operation owner, or more than two documentation assignments.

## Prohibited Semantics

Do not score, rank, threshold, rerank, clip, use lexical or path fallback, or manually
repair assignments. Do not recollect or rebuild metadata from names. Do not choose
`generic-executor` merely because a specialized collector record is broken; fallback
applies only when no specialized operation semantically owns the accepted task.
