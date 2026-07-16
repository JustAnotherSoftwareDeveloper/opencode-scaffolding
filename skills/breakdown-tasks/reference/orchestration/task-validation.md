# Task Validation

> **Note**: These validation rules are enforced during **Phase C (Audit)** of the
> `breakdown-tasks` worker. The Phase C audit evaluates every task's skills for
> reasonableness and atomicity. See `../../SKILL.md` (Phase C,
> Step C2) for the enforcement criteria.

Validation checks for decomposition output correctness.
Verify output against these checks.
Rework affected packet(s) if any check fails.

- **JSON validity** — The entire output must be parseable as valid JSON.
- **JSON object structure** — The parsed result must be an object with `summary` (string) and `tasks` (array) properties.
- **Root key strictness** — The root object must contain only `summary` and `tasks`.
- **Schema compliance** — Every element in `tasks` must have all required keys: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.
  Missing or extra keys are a blocker.
- **executionInstructions step numbering** — Steps must be sequential integers starting at 1 with no gaps or duplicates.
- **executionInstructions verifiability** — Each step must have a concrete, observable action.
  Reword steps with vague actions (`"improve"`, `"optimize"`, `"refactor"` without specifics).
- **filesToRead / filesToWrite — arrays of file paths** — These arrays may be empty when a task has no file inputs or outputs.
  Each element, if present, must be a non-empty string path.
- **Type correctness** — Every field must have the correct type:
  `filesToRead` must be an array of strings, `filesToWrite` must be an array of strings, `skills` must be an array of strings, `executionInstructions` must be an array of `{step, action, verification}` objects, `verification` must be an array of strings, `purpose`, `context`, `expectedOutput` must be strings.
- **Optional fields** — `verification` is optional.
  If present, validate them against the schema.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work.
  Verify no packet bundles independent or logically separable steps under a single `purpose`.
  Ensure each purpose contains exactly one action verb (e.g., "create", "analyze", "fix").
  Multiple action verbs per purpose indicate a combined task.
- **Skill-name reasonableness** — Each entry in the `skills` array must be appropriate for the task's purpose and context.
