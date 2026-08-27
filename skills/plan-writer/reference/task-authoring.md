# Task Authoring

This file defines the plan workflow's source-to-task authoring procedure.
The shared [task-contract reference](../../task-contract/reference/README.md) owns
task identity, atomicity, one-result and verification alignment, dependency and
coupling meaning, source and proposal traceability, and authoring metadata.
Do not restate those invariants here.

Produce one root object with `summary` and `tasks`.

Produce TaskDraft objects without a `skills` field after reviewing boundaries
against the shared task contract.

Preserve material source constraints, proposal-derived scope, decisions, and
acceptance conditions in each task `context`.

Preserve source-derived requirements in each task `context`.

Use copied relative source paths in `filesToRead` when a worker must inspect a
source document. Include proposal and predecessor artifacts when they supply
material input to the task.

Include only fields accepted by the existing TaskDraftList contract.

Do not select skills by score, rank, path, threshold, or fallback. Assign skills
inline from the collected operation/documentation array after task-boundary
authoring. The passive `task-contract` record is context only and never an
executable task assignment.

Keep execution instructions ordered, concrete, and limited to one worker unit of work.

Label unresolved material as `Open Question:` in task context.

Label unverified material as `Assumption:` in task context.
