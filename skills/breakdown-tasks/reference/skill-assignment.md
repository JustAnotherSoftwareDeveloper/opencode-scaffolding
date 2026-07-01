# Skill Assignment Procedure

Deterministic procedure for assigning skills to tasks during decomposition.
Executed in Step 5 of the breakdown-tasks workflow.

## Prerequisites

1. The skill index has been discovered and parsed (Step 4).
2. The state file has been populated with task packets (Step 3).

## Deterministic Assignment Procedure

### 5.1 Derive Required Domain/Expertise

For each task, extract the required domain/expertise from the following fields:

- `purpose` — The single-sentence task purpose.
- `context` — The relevant subset of the user request.
- `filesToRead` — Files that inform the task's domain.
- `filesToWrite` — Files that indicate the task's impact.

Identify three categories:

1. **Primary domain keywords** — e.g., `python`, `node`, `bash`, `testing`, `validation`.
2. **Required technical skills** — e.g., `refactoring`, `doc-generation`, `cli-integration`.
3. **Execution context** — e.g., `execution`, `analysis`, `documentation`.

### 5.2 Cross-Reference Skill Index

Match each task against the discovered skill index using this priority order:

1. **Description match (primary)** — Exact or semantic match between task domain/skills and the skill's `description` field.
2. **Class match (secondary)** — Only match skills whose `class` is compatible with execution tasks:
   - `operation`
   - `delegated`
   - `inline`
   - `orchestrated`
   
   Skip `documentation` and `planning` classes unless the task is analysis/reference-heavy (e.g., research, review, doc generation).
3. **Tags match (tertiary)** — Match against flat tag strings (e.g., `testing`, `create`, `node`).

### 5.3 Select and Cap Skills

1. Select the best-matching skills based on the above criteria.
2. **Cap at 3 skills per task.**
3. Prefer the most specific skill over more general ones.
4. When multiple skills have equal specificity, order alphabetically by name.
5. **If no skill matches after steps 5.1–5.3, assign `generic-analysis` as the fallback.**
   Every task must have at least one skill. Zero skills is never permitted.

### 5.4 Validate and Emit

1. Ensure the `skills` array has `uniqueItems: true`.
2. Ensure no unknown skill names are referenced.
3. Write the assembled output object back into `STATE_FILE`, overwriting the previous content.
4. **Note:** Skill-match rationale is **not** persisted in task packets.
   The schema's `additionalProperties: false` prohibits non-standard fields.

## Output Format

The final output is a JSON object with:

- `summary` (string) — The request summary from Step 2.
- `tasks` (array) — Task packet objects in sequential order, each with a `skills` array.