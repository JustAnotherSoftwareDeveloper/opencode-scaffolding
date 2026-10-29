# Task Identity

Task identity names one independently reviewable unit of work and the result that
gives that unit meaning.

## Identity Fields

- **`taskId`** identifies one task across authoring and handoff when present.
  Dependencies refer to that identity, not to an inferred list position.
- **`purpose`** states one actionable objective and names its immediate result.
- **`context`** carries the request facts, decisions, constraints, source references,
  and proposal references this task needs.
- **`filesToRead`** identifies source material and predecessor artifacts
  needed to understand the task.
- **`filesToWrite`** identifies the explicit output boundary through literal
  paths or bounded path patterns.
- **`expectedOutput`** describes the single deliverable that fulfills the purpose.

## Identity Boundaries

Do not infer a task's semantic boundary from its file count, workflow phase, shared
topic, destination, release, or available skill.

A list position may preserve identity in a legacy packet, but it does not define the
task's semantic boundary.

Review the purpose, expected result, verification boundary, dependencies, and any
coupling evidence together to assess task identity.

Skill names, collector paths, and assignment decisions are outside this shared
semantic owner.

## Context Fidelity

Context preserves the material subset of the request that the task needs.

Keep source-derived requirements and proposal constraints recognizable in context,
with their supporting paths or section references retained in the task's read set.

Do not treat a concern as part of the task solely because it shares a source,
destination, or final document.
