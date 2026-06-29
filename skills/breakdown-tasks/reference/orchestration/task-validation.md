# Task Validation

Validation checks for decomposition output correctness.
After decomposition, verify the output against these checks.
If any check fails, rework the affected packet(s) before returning.

- **JSON validity** — The entire output must be parseable as valid JSON.
- **JSON object structure** — The parsed result must be an object with `summary` (string) and `tasks` (array) properties.
- **Root key strictness** — The root object must contain only `summary` and `tasks`.
- **Schema compliance** — Every element in `tasks` must have all required keys: `id`, `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.
  Missing or extra keys are a blocker.
- **UUID v4 format** — Every `id` field must be a valid UUID v4 string matching the pattern `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` where `y` is `[89ab]`.
- **executionInstructions step numbering** — Steps must be sequential integers starting at 1 with no gaps or duplicates.
- **executionInstructions verifiability** — Each step must have a concrete, observable action.
  Steps with vague actions (`"improve"`, `"optimize"`, `"refactor"` without specifics) must be reworded.
- **filesToRead / filesToWrite — arrays of file paths** — These arrays may be empty when a task has no file inputs or outputs (e.g., an analysis task that operates on context alone, or a review task that produces no files). Each element, if present, must be a non-empty string path.
- **Type correctness** — Every field must have the correct type:
  `id` must be a string, `filesToRead` must be an array of strings, `filesToWrite` must be an array of strings, `skills` must be an array of strings, `executionInstructions` must be an array of `{step, action, verification}` objects, `verification` must be an array of strings, `purpose`, `context`, `expectedOutput` must be strings.
- **Optional fields** — `verification` is optional.
  If present, validate them against the schema.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work.
  Verify no packet bundles independent or logically separable steps under a single `purpose`. Additionally, ensure each purpose contains exactly one action verb (e.g., "create", "analyze", "fix") — multiple action verbs per purpose indicate a combined task.
- **Skill-name reasonableness** — Each entry in the `skills` array must be appropriate for the task's purpose and context.
