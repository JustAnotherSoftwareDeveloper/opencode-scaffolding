# Task Identity

Task identity names one independently reviewable unit of work and the result that
gives that unit meaning.

## Identity Fields

- **`taskId`** identifies one task across authoring and handoff when it is present.
  Dependency references use that identity rather than an inferred list position.
- **`purpose`** states one actionable objective and names the result of that
  objective.
- **`context`** carries the relevant request facts, decisions, constraints, source
  references, and proposal references for that task without filler.
- **`filesToRead`** identifies source material and predecessor artifacts
  needed to understand the task.
- **`filesToWrite`** identifies the explicit output boundary through literal
  paths or bounded path patterns.
- **`expectedOutput`** describes the single deliverable represented by the purpose.

## Identity Boundaries

A task is not identified by its file count, workflow phase, shared topic, destination,
release, or available skill.

An ordered position can preserve legacy packet identity, but position does not explain
the task's semantic boundary.

The task's purpose, result, verification, dependencies, and coupling evidence are
read together when reviewing identity.

Skill names, collector paths, and assignment decisions are outside this shared
semantic owner.

## Context Fidelity

Context preserves the material subset of the request that the task needs.

Source-derived requirements and proposal constraints remain recognizable in context,
with their supporting paths or section references retained in the task's read set.

Context does not turn an unrelated concern into part of the task merely because
the concerns share a source, destination, or final document.
