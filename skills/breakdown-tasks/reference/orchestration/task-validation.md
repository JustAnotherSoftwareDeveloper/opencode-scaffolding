# Task Validation

Validation checks for decomposition output correctness.
Verify output against these checks.
Rework affected packet(s) if any check fails.

The shared [task-contract references](../../../task-contract/reference/README.md)
own the meaning of task identity, atomicity, result and verification alignment,
dependencies, coupling, traceability, and authoring metadata. The checks below are
the breakdown-tasks operation's validation procedure and diagnostics; they do not
replace that passive reference.

## Layered atomicity checks

- **Boundary before assignment** — Candidate tasks and their dependencies are fixed
  before operation/documentation skills are selected. A skill may not create a task
  boundary or justify a merge.
- **Shared boundary semantics** — Review each task's purpose, expected output,
  verification, dependency edges, coupling rationale, traceability, and authoring
  metadata using the linked task-contract references. Do not let the validator
  become a second semantic owner.
- **Dependency representation** — The operation checks that dependent tasks carry
  explicit `dependencies` edges and required predecessor artifacts in `filesToRead`,
  using the shared dependency and traceability meaning. Paths are explicit or
  bounded, never invented placeholders.
- **Staged outcomes** — Report uncertain text heuristics as warnings; use a hard
  failure for declared compound signals, demonstrated independent concerns,
  boundary violations, or unverifiable results. Any split or migration outcome must
  be revalidated, including skills.
- **Named anti-patterns** — Any declared compound-task signal produces a hard split
  diagnostic. Text heuristics remain warnings because they do not prove independence.
- **Uncapped task inventory** — Confirm every independently decidable question,
  change, and produced deliverable is represented. Do not reject, merge, or pad tasks
  based on packet size. Keep verification evidence with its result unless it is an
  explicitly requested deliverable. Enforce one to three skills per task separately.

- **JSON validity** — The entire output must be parseable as valid JSON.
- **JSON object structure** — The parsed result must be an object with `summary` (string) and `tasks` (array) properties.
- **Root key strictness** — The root object must contain only `summary` and `tasks`.
- **Schema compliance** — Every element in `tasks` must have all required keys: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`. Missing or extra keys are a blocker.
- **executionInstructions step numbering** — Steps must be sequential integers starting at 1 with no gaps or duplicates.
- **executionInstructions verifiability** — Each step must have a concrete, observable action. Reword steps with vague actions (`"improve"`, `"optimize"`, `"refactor"` without specifics).
- **filesToRead / filesToWrite — arrays of file paths** — These arrays may be empty when a task has no file inputs or outputs. Each element, if present, must be a non-empty string path.
- **Type correctness** — Every field must have the correct type: `filesToRead` must be an array of strings, `filesToWrite` must be an array of strings, `skills` must be an array of strings, `executionInstructions` must be an array of `{step, action, verification}` objects, `verification` is an array of strings when present, and `purpose`, `context`, `expectedOutput` must be strings.
- **Optional fields** — `verification` is optional. If present, validate it against the schema.
- **No combined tasks** — Apply the shared atomicity contract while checking that no
  packet bundles independent or logically separable steps under a single `purpose`,
  and ensure each purpose contains exactly one action verb.
- **Skill-name reasonableness** — Each entry in the `skills` array must be appropriate for the task's purpose and context.

The layered checks are current diagnostic policy where they describe warning versus
failure behavior. Task count is derived solely from atomic coverage and must not be
silently converted into a capacity target or extra workflow stage.
