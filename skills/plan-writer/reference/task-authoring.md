# Task Authoring

This file defines the plan workflow's source-to-task authoring procedure.
The loaded `task-contract` documentation skill owns task identity, atomicity,
one-result and verification alignment, dependency and coupling meaning, source and
proposal traceability, and authoring metadata. Do not restate those invariants here.

- Require the author to choose a packet slug and produce the canonical packet root.
  Preserve the slug unchanged. The canonical task-packet schema used by the
  validation workflow defines the root fields and slug constraints; do not restate
  or validate them locally.

- After reviewing task boundaries against the shared task contract, produce
  `TaskDraft` objects without a `skills` field.

- From one `PROPOSAL.md` and its copied sources, extract proposal-derived scope,
  decisions, implementation details, verification criteria, and questions. Do not
  require a separate implementation document; implementation detail lives inside
  `PROPOSAL.md` as `Implementation Details`.

- Preserve source-derived requirements, recommendation constraints, concrete
  implementation targets, compatibility, and exclusions in each task's `context`.

- When a worker must inspect a source document, include its copied relative path in
  `filesToRead`. Include proposal and predecessor artifacts when they supply
  material input to the task.

- Include only fields accepted by the existing `TaskDraftList` contract.

- Do not select skills by score, rank, path, threshold, or fallback. After task
  boundaries are accepted, assign skills inline from the distinct operation and
  documentation results. The passive `task-contract` record provides context only;
  it is never an executable task assignment.

- Keep execution instructions ordered and concrete, and limit them to one worker
  unit of work.

- Label unresolved material in task `context` as `Open Question:`.

- Label unverified material in task `context` as `Assumption:`.

- Label missing material evidence in task `context` as `Evidence Gap:`.

- Keep research questions labeled as researchable uncertainty. Do not convert a
  research question into an owner decision without evidence work.
