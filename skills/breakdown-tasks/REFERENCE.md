# Breakdown Tasks — Reference

> Atomic task unit definition, core rules, and anti-patterns for decomposing work into delegatable packets.

## Core Rules

### 1. Single Unit of Work

Each task performs exactly one logical change **or** answers exactly one analytical question.

- If a task modifies two files, makes two unrelated edits in one file, or answers two independent questions, split it.

### 2. Single Output Artifact

Each task produces exactly one verifiable result — either one output artifact **or** one documented finding.

- If a task produces two outputs (e.g., writes a file *and* runs a test, or produces two distinct findings), split verification from production.

### 3. Logical Step Pipeline

Tasks form a pipeline where each is one discrete step in a sequence.

- **Independent steps** → separate parallel-capable tasks.
- **Dependent steps** → sequential but still individually atomic.

### 4. Dependent Work Serialization

When multiple changes to the same file or multiple analysis steps on the same subject are needed, serialize them as separate sequential tasks.

- Each task lists the target file or subject in `## FILES TO READ` or `## FILES TO WRITE`.
- Run tasks in order so each sees the prior task's output.

### 5. Skill-Aware But Not Skill-Bound

Available skills inform task decomposition but do not override atomicity.
Use the discovered skill list to assign matching skills, shape task boundaries, and identify missing capabilities.
Never merge or split tasks to match skill scope.

- If a skill covers two adjacent concerns, keep them as separate atomic packets — assign the skill to the matching packet only.
- Do not adjust task granularity to fit a skill's scope; atomicity rules take precedence.

## Anti-Patterns

### Work-Boundary Anti-Patterns

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
  Split into evaluate framework A, evaluate framework B, compare findings and recommend.

### Skill-Assignment Anti-Patterns

- **"Assign no skills when skills are available"** — The decomposer has skill data but leaves `## SKILLS` empty despite obvious matches in the discovered skill list.
- **"Force-assign a skill to every packet"** — Assigning a skill to purely structural tasks just to avoid empty `## SKILLS` fields. Leave empty when no match exists.