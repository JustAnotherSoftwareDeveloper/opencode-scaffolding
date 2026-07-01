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

- **Assign no skills** — Every task must have at least one skill. If no specific skill matches after normal matching, assign `generic-analysis` as the fallback. Zero skills is never permitted.
- **Force-assign a skill that does not match** — Do not assign a mismatched skill just to satisfy the one-skill minimum. Instead, use `generic-analysis` for genuine fallback cases where no specific skill matches.
