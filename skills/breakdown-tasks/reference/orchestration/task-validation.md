# Task Validation

Validation checks for decomposition output correctness.
Verify output against these checks.
Rework affected packet(s) if any check fails.

## Layered atomicity checks

- **Boundary before assignment** — Candidate tasks and their dependencies are fixed
  before operation/documentation skills are selected. A skill may not create a task
  boundary or justify a merge.
- **One result** — Every task has one purpose, one expected output, and evidence
  that verifies that same result. The coupled-file exception is valid only when the
  files form one result, `couplingRationale` explains the boundary, and one check
  verifies the result.
- **Dependency representation** — Each dependent task identifies its predecessors
  with explicit `dependencies` edges and lists required prior artifacts in
  `filesToRead`. Paths are explicit or bounded, never invented placeholders.
- **Staged outcomes** — Report a repairable evidence gap as a warning first; use a
  hard failure for unresolved ambiguity, boundary violations, or unverifiable
  results. Any split or migration outcome must be revalidated, including skills.
- **Named anti-patterns** — A declared implementation-plus-tests, multiple-helpers,
  analysis-plus-planning, or multiple-comparisons signal produces a named split-review
  diagnostic. Text heuristics remain warnings and do not prove independence.
- **Deferred decisions** — Preserve the three-task ceiling and do not require an
  extra review phase. These are compatibility/capacity decisions, not validator
  expansion points.

- **JSON validity** — The entire output must be parseable as valid JSON.
- **JSON object structure** — The parsed result must be an object with `summary` (string) and `tasks` (array) properties.
- **Root key strictness** — The root object must contain only `summary` and `tasks`.
- **Schema compliance** — Every element in `tasks` must have all required keys: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`. Missing or extra keys are a blocker.
- **executionInstructions step numbering** — Steps must be sequential integers starting at 1 with no gaps or duplicates.
- **executionInstructions verifiability** — Each step must have a concrete, observable action. Reword steps with vague actions (`"improve"`, `"optimize"`, `"refactor"` without specifics).
- **filesToRead / filesToWrite — arrays of file paths** — These arrays may be empty when a task has no file inputs or outputs. Each element, if present, must be a non-empty string path.
- **Type correctness** — Every field must have the correct type: `filesToRead` must be an array of strings, `filesToWrite` must be an array of strings, `skills` must be an array of strings, `executionInstructions` must be an array of `{step, action, verification}` objects, `verification` is an array of strings when present, and `purpose`, `context`, `expectedOutput` must be strings.
- **Optional fields** — `verification` is optional. If present, validate it against the schema.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work. Verify no packet bundles independent or logically separable steps under a single `purpose`, and ensure each purpose contains exactly one action verb.
- **Skill-name reasonableness** — Each entry in the `skills` array must be appropriate for the task's purpose and context.

The layered checks are current diagnostic policy where they describe warning versus
failure behavior. The three-task ceiling and deferred review are compatibility
constraints; they must not be silently converted into new capacity or workflow
stages.
