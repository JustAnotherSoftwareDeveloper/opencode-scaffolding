# Task Authoring

Produce one root object with `summary` and `tasks`.

Produce atomic TaskDraft objects without a `skills` field; skills are assigned inline after collecting operation and documentation profiles.

Preserve material source constraints in each task `context`.

Preserve source-derived requirements in each task `context`.

Use copied relative source paths in `filesToRead` when a worker must inspect a source document.

Include only fields accepted by the existing TaskDraftList contract.

Do not select skills by score, rank, path, threshold, or fallback. Assign skills inline from the collected operation/documentation array.

Keep execution instructions ordered, concrete, and limited to one worker unit of work.

Label unresolved material as `Open Question:` in task context.

Label unverified material as `Assumption:` in task context.
