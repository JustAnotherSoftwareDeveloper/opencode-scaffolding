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

- **Assign skills before collecting operation/documentation profiles** — The LLM must collect `--class operation --class documentation` before assigning. Skills selected without seeing the collected array may be absent or stale.
- **Force a skill when no candidate matches** — Leave the skills array empty or block with no-match evidence. An unrelated skill imposes incompatible workflow and output requirements.
- **Force a fallback skill** — Do not add `generic-analysis` or any other fallback. If no skill matches, surface the gap rather than papering over it.
