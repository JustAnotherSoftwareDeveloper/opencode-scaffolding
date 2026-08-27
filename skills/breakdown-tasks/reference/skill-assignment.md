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

Show the request and the planning array to the LLM. Load every materially relevant profile, with no numeric cap. Load only selected names through the skill tool. A planning load is passive context and does not grant execution or write authority. An empty selection is valid when no planning concern exists.

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

Show the complete draft and the operation/documentation array to the LLM. Select one
to three semantically fitting skills per task. A no-match decision blocks. Inspect
selected contracts and reconcile each name against the array. The passive
`task-contract` documentation record is context only, not an executable assignment;
do not place it in a task's executable `skills` array.

Block on a name absent from the operation/documentation array.

## Prohibited Semantics

Do not score, rank, threshold, rerank, clip, use lexical or path fallback, or manually repair assignments. Do not recollect or rebuild metadata from names.
