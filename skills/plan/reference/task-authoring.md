# Task Authoring

Produce one root object with `summary` and `tasks`.

Produce atomic TaskDraft objects without a `skills` field.

Preserve material memo constraints and source-derived requirements in each task `context`.

Use copied relative source paths in `filesToRead` when a worker must inspect a source document.

Include only fields accepted by the existing TaskDraftList contract.

Keep execution instructions ordered, concrete, and limited to one worker unit of work.

Label unresolved material as `Open Question:` in task context.

Label unverified material as `Assumption:` in task context.
