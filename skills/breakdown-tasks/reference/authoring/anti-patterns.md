# Anti-Patterns

Work-boundary and skill-assignment mistakes to avoid when decomposing tasks.

## Work-Boundary Anti-Patterns

- **"Add user authentication"** — Touches multiple files and produces multiple outputs.
  Split into: middleware, route, model, tests, test run.
- **"Implement X and add error handling"** — Two logical changes to the same file.
  Split into two sequential tasks.
- **"Write utils.py with three helpers"** — Three logical changes in one file write.
  Split into three sequential tasks.
- **"Refactor checkout and run tests"** — Produces two outputs.
  Split into refactor task then test-run task.
- **"Analyze codebase for security vulnerabilities"** — Broad analysis with multiple independent concerns.
  Split into analyze authentication, analyze input validation, analyze dependency risk.
- **"Review checkout flow and suggest improvements"** — Combines analysis and planning in one task.
  Split into document current flow, identify issues, propose improvements.
- **"Compare all frontend frameworks and pick one"** — Multiple independent comparisons in one task.
  Split into evaluate framework A, evaluate framework B, compare findings and select.

## Skill-Assignment Anti-Patterns

- **Assign skills manually** — The LLM must produce `TaskDraft` objects without `skills`. The `assign-skills` script populates final skill arrays.
- **Assign no skills after automation** — Every final task must have at least one skill. `assign-skills` satisfies the one-skill minimum from discovered/indexed skills; there is no synthetic fallback.
- **Force a fallback skill** — Do not add `generic-analysis` or any other fallback manually. Skill selection is owned by `assign-skills`.
