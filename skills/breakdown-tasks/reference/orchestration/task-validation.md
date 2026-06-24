# Task Validation

Validation checks for decomposition output correctness.
After decomposition, verify the output against these checks.
If any check fails, rework the affected packet(s) before returning.

- **JSON validity** — The entire output must be parseable as valid JSON.
- **JSON object structure** — The parsed result must be an object with `summary` (string) and `tasks` (array) properties.
- **Schema compliance** — Every element in `tasks` must have all required keys: `id`, `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`.
  Missing or extra keys are a blocker.
- **UUID v4 format** — Every `id` field must be a valid UUID v4 string matching the pattern `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` where `y` is `[89ab]`.
- **Dependency acyclicity** — The dependency graph formed by per-task `dependencies` arrays must be acyclic.
  Use topological sort to detect cycles.
  A cycle is a blocker.
- **Dependency reference validity** — Every UUID in a `dependencies` array must match the `id` of another task in the array.
  Orphan references are a blocker.
- **executionInstructions step numbering** — Steps must be sequential integers starting at 1 with no gaps or duplicates.
- **executionInstructions verifiability** — Each step must have a concrete, observable action.
  Steps with vague actions (`"improve"`, `"optimize"`, `"refactor"` without specifics) must be reworded.
- **filesToRead / filesToWrite non-empty** — These arrays must be non-empty unless the task truly involves no files.
  A task that reads or writes files must list them explicitly.
- **Type correctness** — Every field must have the correct type:
  `id` must be a string, `dependencies` must be an array of strings, `filesToRead` must be an array of strings, `filesToWrite` must be an array of strings, `skills` must be an array of strings, `executionInstructions` must be an array of `{step, action, verification}` objects, `verification` must be an array of strings, `purpose`, `context`, `expectedOutput` must be strings.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work.
  Verify no packet bundles independent or logically separable steps under a single `purpose`.
- **Skill-name reasonableness** — Each entry in the `skills` array must be appropriate for the task's purpose and context.