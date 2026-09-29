# Task Validation

Check the packet's structure before reviewing its request-aware task boundaries.
Rework affected packets when a structural or semantic check fails.

The loaded `task-contract` documentation skill owns the meaning of task identity,
atomicity, result and verification alignment, dependencies, coupling, traceability,
and authoring metadata. The checks below are the breakdown-tasks operation's
validation procedure and diagnostics; they do not replace that passive reference.

## Structural And Schema Checks

- **JSON validity** — Require the complete output to parse as JSON.
- **Canonical root** — Validate the complete object against the canonical
  [task-packet schema](../../schema/task-packet.schema.json). The required root
  fields are `summary`, `slug`, `tasks`, and `boundaryReview`; additional root
  fields are not allowed.
- **Required task fields** — Every task requires `taskId`, `purpose`, `context`,
  `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`,
  `expectedOutput`, `verificationCoverage`, `dependencies`,
  `antiPatternSignals`, and `purposeOutputAlignment`. Additional task fields are
  not allowed. `verification` and `couplingRationale` are optional and must
  satisfy their schema definitions when present.
- **Schema constraints** — Use the schema for field types, nested structures,
  requiredness, enums, array bounds, and string constraints. Do not substitute a
  partial local field list for schema validation.
- **Execution-step structure** — The task validator additionally requires
  `executionInstructions.step` values to be sequential integers starting at 1,
  without gaps or duplicates. The schema itself requires only an integer of at
  least 1 for each step.
- **File-array structure** — `filesToRead` and `filesToWrite` are required string
  arrays and may be empty. Reject empty or duplicate entries and placeholder
  paths.
- **Structural consistency** — Check task identity uniqueness, non-empty
  `verificationCoverage.observable`, valid dependency references, acyclic
  dependencies, and overlapping write targets unless the tasks share a matching
  coupling group or the later task depends on the earlier writer.
- **Skill-array structure** — Enforce the schema's one-to-three unique string
  entries per task. This structural limit does not establish skill suitability
  or class composition.

Structural validation checks the packet interface and structural consistency.
It does not establish semantic atomicity or accept the packet for display or
dispatch.

## Atomicity Checks

- **Mandatory closed boundary-review evidence** — Every applicable packet
  retains a request-aware boundary-review record alongside the canonical packet.
  Before skill assignment, it inventories every immediate and necessary
  intermediate result, maps each candidate to one immediate result and fixed
  predecessor outputs, and records a
  split-by-default decision. Every warning is closed as `split`,
  `accepted-indivisible`, or `not-applicable`; accepted indivisibility states one
  shared result, one verification boundary, and concrete separation harm.
- **Boundary before assignment** — Candidate tasks and their dependencies are fixed
  and accepted in the pre-assignment boundary review before operation/documentation
  skills are selected. A skill may not create a task boundary or justify a merge.
- **Shared boundary semantics** — Review each task's purpose, expected output,
  verification, dependency edges, coupling rationale, traceability, and authoring
  metadata using the loaded documentation skill's named references. Do not let the
  validator become a second semantic owner.
- **Recursive split review** — Start from the requested outcome, identify its smaller
  required results, and split each result again while it contains separate questions,
  decisions, changes, or deliverables. Hold predecessor outputs fixed when checking
  whether dependent work can be accepted or retried separately.
- **Dependency representation** — The operation checks that dependent tasks carry
  explicit `dependencies` edges and required predecessor artifacts in `filesToRead`,
  using the shared dependency and traceability meaning. Paths are explicit or
  bounded, never invented placeholders.
- **Staged outcomes and warnings** — Treat uncertain text heuristics as review
  warnings, not atomicity proof. Every warning requires a recorded closed disposition;
  an unresolved warning is a hard failure. Declared compound signals, demonstrated
  independent concerns, boundary violations, or unverifiable results require revision.
  Any split outcome must be revalidated, including skills.
- **Named anti-patterns** — Any declared compound-task signal produces a hard split
  diagnostic. Text heuristics remain warnings because they do not prove independence.
- **Uncapped task inventory** — Confirm every independently decidable question,
  change, and produced deliverable is represented. Do not reject, merge, or pad
  tasks based on packet size. Keep verification evidence with its result unless
  explicitly requested as a deliverable. Enforce one to three skills separately.
- **No combined tasks** — Apply the shared atomicity contract. No packet may bundle
  separate results under one `purpose`. Multiple actions are allowed when they only
  produce or verify one result; verb count is not a boundary test.
- **Verifiable instructions** — Require each action to name a concrete, observable
  result. Reword vague actions such as `"improve"`, `"optimize"`, or unspecified
  `"refactor"` actions.

## Assignment Fit

- **Skill-name reasonableness** — Each `skills` entry must be appropriate for the
  task's purpose and context. Schema validity does not prove that a skill fits.

## Final Request-Aware Acceptance

After candidate publication and structural validation, the delegator independently
compares the original request, retained boundary-review record, and final task set.
Acceptance for display or dispatch requires closed inventory coverage, one immediate
result per task, supported fixed-predecessor split decisions, closed warnings, usable
dependency handoffs, and concrete evidence for every retained indivisible boundary.
Failure returns the set for split or a concrete indivisibility rationale. Structural
success is not semantic atomicity approval. For every applicable packet, reject
optional adoption, backwards compatibility, migration, legacy, transition,
prior-format, absent-record acceptance, and alternate paths. Task count derives from
the results needed to satisfy the request and must not become a capacity target.
