# Anti-Patterns

Work-boundary and skill-assignment mistakes to avoid when decomposing tasks.

## Work-Boundary Anti-Patterns

- **"Add user authentication"** — Touches multiple files and produces multiple outputs.
  *Violates: Single Unit Of Work (multiple logical changes) and Single Output Artifact (writes files *and* runs tests).*
  Split into: middleware, route, model, tests, test run.
- **"Implement X and add error handling"** — Two logical changes to the same file.
  *Violates: Single Unit Of Work (two unrelated changes in one file).*
  Split into two sequential tasks.
- **"Write utils.py with three helpers"** — Three logical changes in one file write.
  *Violates: Single Unit Of Work (three independent additions).*
  Split into three sequential tasks.
- **"Refactor checkout and run tests"** — Produces two outputs.
  *Violates: Single Output Artifact (refactored code *and* test results are two different output types).*
  Split into refactor task then test-run task.
- **"Analyze codebase for security vulnerabilities"** — Broad analysis with multiple independent concerns.
  *Violates: Single Unit Of Work (each vulnerability type is an independent analysis question).*
  Split into analyze authentication, analyze input validation, analyze dependency risk.
- **"Review checkout flow and suggest improvements"** — Combines analysis and planning in one task.
  *Violates: Logical Step Pipeline (analysis must precede planning as separate pipeline stages).*
  Split into document current flow, identify issues, propose improvements.
- **"Compare all frontend frameworks and pick one"** — Multiple independent comparisons in one task.
  *Violates: Single Unit Of Work (each framework evaluation is an independent analysis question).*
  Split into evaluate framework A, evaluate framework B, compare findings and select.
- **"Analyze architecture, style, workflow rules, and migration"** — A lifecycle
  label hides several independently decidable analytical questions.
  *Violates: Single Unit Of Work and the split test.*
  Split into one task per analytical question, then add a dependent synthesis task
  only when the request requires a consolidated conclusion.
- **"Create the proposal" as one task for a multi-concern proposal** — A shared final
  document is being used to merge independent research or decisions.
  *Violates: Single Unit Of Work; output packaging does not define atomicity.*
  Split the independent findings first and reserve one dependent task for synthesis.
- **Choosing a fixed task count before inventorying concerns** — Packet size dictates
  boundaries instead of the work.
  *Violates: Boundary Before Assignment.* There is no task-count ceiling or target;
  the one-to-three constraint applies to skills per task.
- **Using template variables or placeholders in `filesToRead` or `filesToWrite`** — `{{TASK_1_PATH}}`, `<output-from-task-1>`, or similar invented syntax. These are not file paths and will not resolve at execution time. Use a bounded glob pattern instead (e.g., `.plans/*-<slug>/tasks.json`).

## Skill-Assignment Anti-Patterns

- **Assign skills before collecting operation/documentation profiles** — The LLM must collect `--class operation --class documentation` before assigning. Skills selected without seeing the collected array may be absent or stale.
- **Force a skill when no candidate matches** — Leave the skills array empty or block with no-match evidence. An unrelated skill imposes incompatible workflow and output requirements.
- **Force a fallback skill** — Do not add `generic-analysis` or any other fallback. If no skill matches, surface the gap rather than papering over it.
