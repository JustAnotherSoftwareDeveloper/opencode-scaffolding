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

## Skill-Assignment Anti-Patterns

- **Assign skills manually** — The LLM must produce `TaskDraft` objects without `skills`. The `assign-skills` script populates final skill arrays.
  *Why: Manual assignment bypasses the deterministic scoring backend, breaking separation of concerns. The LLM is probabilistic; the script is deterministic.*
- **Assign no skills after automation** — Every final task must have at least one skill. `assign-skills` satisfies the one-skill minimum from discovered/indexed skills; there is no synthetic fallback.
  *Why: Every worker needs at least one skill to execute; without a minimum, some tasks would be dispatched with no execution capability.*
- **Force a fallback skill** — Do not add `generic-analysis` or any other fallback manually. Skill selection is owned by `assign-skills`.
  *Why: A synthetic fallback would create misleading skill assignments and erode trust in the skill system. If no skill matches, the pipeline should surface the gap, not paper over it.*
