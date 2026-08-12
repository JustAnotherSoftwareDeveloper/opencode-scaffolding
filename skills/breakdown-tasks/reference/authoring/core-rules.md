# Core Rules

The layered atomicity contract has one authoring result: a decomposition that is
bounded, independently checkable, and ready for orchestration. These rules are
authoring guidance; diagnostics and compatibility decisions are identified where
they are not yet hard requirements.

## 1. Single boundary, single unit

Each task performs exactly one logical change or answers exactly one analytical
question. Define the task boundary before looking for a skill. A task may not hide
independent concerns behind a broad purpose, context, or file list.

## 2. Single purpose and single result

Each task has one purpose sentence with one action and one expected output: one
verifiable artifact or one documented finding. Verification is evidence about that
result, not a second deliverable. Purpose, output, and verification must describe
the same boundary; write the mapping explicitly when the result is a package.

## 3. Dependencies are part of the boundary

Represent dependencies with ordered tasks and explicit `filesToRead`/
`filesToWrite` paths. Serialize dependent work; independent work may be parallel.
A later task declares its dependency by listing the prior output in its
`filesToRead`. Use bounded patterns only when a prior path is genuinely unknown;
never use invented output variables. Explicit `dependencies` edges (in the packet
schema) make these relationships machine-readable for the validator.

## 4. Coupled-file exception

The default heuristic is one task per file and one conceptual change. Multiple
files are allowed when they jointly form one tightly coupled result with one shared
verification signal. The exception rationale must be inspectable in purpose,
expected output, `couplingRationale`, and verification. It does not authorize
combining implementation with tests, analysis with planning, or unrelated edits,
and it does not establish a universal one-file rule.

## 5. Skill-aware, not skill-bound

Candidate decomposition comes before skill assignment. Skills inform execution but
never define task boundaries; do not merge or split work to fit a skill. Assign only
after the candidate tasks and dependencies are stable, and assign the matching skill
to the matching task.

## 6. Staged enforcement and capacity

Treat actionable atomicity defects as warnings first when they can be repaired by
clarifying evidence. Escalate to a hard failure when the defect remains ambiguous,
violates a declared boundary, or cannot be verified. If a task is split or migrated,
revalidate the resulting task(s), dependencies, purpose/output mapping, and skill
assignment. Retain the three-task ceiling. A mandatory extra review phase is a
deferred compatibility decision, not a current requirement.
