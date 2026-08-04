---
name: breakdown-tasks
description: "Use when decomposing a request into bounded task-delegation work items and producing canonical task JSON."
selection:
  role: owner
  tags:
    actions: [decompose]
    inputs: [user request]
    outputs: [delegation task JSON]
    topics: [task decomposition]
    constraints: [atomic work items]
  use_when: [a request must be split into worker-ready tasks]
  not_for: [executing one existing task packet]
class: delegated
---

# Breakdown Tasks

Collect skills, select inline, and publish.

## Input Contract

Read `PURPOSE` and `DETAILS`. Block when either is absent.

## Execution

1. **Collect planning skills.** Run:

   ```bash
   uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning
   ```

   Capture stdout. It is a JSON array. Every record has `name`, `description`, `selection`, `class`, `path`, and `source`. Block on non-zero exit.

2. **Select and load planning skills.** Present the request and the planning array to the LLM. Select every materially relevant planning skill. Load each selected skill with the skill tool. Block on a name absent from the array, a stale path, or a load failure. An empty selection is valid only when no planning concern exists.

3. **Draft tasks.** Write a schema-valid `{summary, tasks}` object. Follow [the authoring references](reference/authoring/core-rules.md). Do not include `skills` in any task.

4. **Collect operation and documentation skills.** Run:

   ```bash
   uv run --directory ~/.config/opencode/scripts/python collect-skills --class operation --class documentation
   ```

   Capture stdout. It is a JSON array with the same shape as step 1. Block on non-zero exit.

5. **Assign skills to each task.** Present the complete draft and the operation/documentation array to the LLM. Select one to three skills per task. Block with explicit no-match evidence when no valid assignment exists. Reconcile every selected name against the array. A name absent from the array blocks. Do not score, rank, rerank, clip, or use lexical fallback.

6. **Inspect contracts.** Read each selected skill's `SKILL.md` at its collector-winning `path` from the array. Verify the contract matches the task.

7. **Write the completed draft.** Write the completed `{summary, tasks}` object with every task's `skills` populated to `/tmp/breakdown-draft.json`.

8. **Publish.** Run:

   ```bash
   uv run --directory ~/.config/opencode/scripts/python init-task-packet \
     --output-dir .tasks < /tmp/breakdown-draft.json
   ```

   Derives a safe filename from the summary, writes atomically, and prints the output path. Block on non-zero exit.

9. **Validate and fix.** Run in a loop until valid:

   ```bash
   uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
     "$PUBLISHED_PATH" \
     --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json \
     --auto-fix --state-file
   ```

   - Exit 0 and no `"fixed": true` → already valid, done.
   - Exit 0 and `"fixed": true` → script fixed the file in place. Read the fixed file back, then retry this step.
   - Exit 1 → structural violations remain. Read errors from stderr, fix the JSON, retry.
   - Exit 2 → unrecoverable error. Block.

## Output Contract

Return the relative published packet path.

## Guardrails

- Run both collector commands exactly as shown.
- Planning selection uses the planning array. Assignment uses the operation/documentation array. Do not swap.
- Do not recollect, rebuild metadata from names, or substitute paths.
- Do not manually populate, correct, reorder, or remove `skills`.
- Fail closed. Publish no partial output.
- Planning loads are passive context. Only task-declared skills are executable.

## References

- `reference/authoring/core-rules.md`
- `reference/authoring/task-granularity.md`
- `reference/authoring/anti-patterns.md`
- `reference/authoring/context-preservation.md`
- `reference/authoring/field-reference-table.md`
- `reference/scripts/validate-task-structure.md`
- `reference/scripts/error-handling-testing.md`
- `reference/orchestration/task-validation.md`
- `reference/maintenance/verification-best-practices.md`
