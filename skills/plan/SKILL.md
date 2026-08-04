---
name: plan
description: "Use when creating a source-document plan workspace that produces executable task JSON."
selection:
  role: owner
  tags:
    actions: [create plan]
    inputs: [source documents]
    outputs: [executable task JSON]
    topics: [task planning]
    constraints: [evidence preserving]
  use_when: [source documents must become an executable plan workspace]
  not_for: [general analysis or decision proposal authoring]
class: operation
---

# Plan

Create an evidence-preserving plan workspace, author tasks from source documents, and publish.

## Input Contract

Require a topic or summary and one or more source-document paths. Block when absent.

## Execution

### Workspace Setup

1. **Validate sources.** Follow [the workspace contract](reference/workspace-contract.md). Resolve every source path. Block on a missing path, a non-file path, a target outside `$CWD`, or a target inside an existing plan workspace.

2. **Create the workspace.** Derive a lowercase kebab-case summary slug and epoch-millisecond timestamp. Create `.plans/<epoch-ms>-<slug>/` without replacing an existing directory. Create category subdirectories only when sources belong to them.

3. **Copy sources.** Copy each source into its category directory. Preserve the source filename or add a deterministic collision suffix. Never modify source documents.

### Planning and Task Authoring

4. **Collect planning skills.** Run:

   ```bash
   uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning
   ```

   Capture stdout. Block on non-zero exit.

5. **Select and load planning skills.** Present the source-backed request and the planning array to the LLM. Select every materially relevant planning skill. Load each selected skill with the skill tool. Block on a name absent from the array, a stale path, or a load failure.

6. **Author tasks.** Write a schema-valid `{summary, tasks}` object. Follow [task-authoring rules](reference/task-authoring.md). Preserve copied relative source paths in `filesToRead`. Preserve source constraints in each task `context`. Do not include `skills` in any task.

### Skill Assignment and Publication

7. **Collect operation and documentation skills.** Run:

   ```bash
   uv run --directory ~/.config/opencode/scripts/python collect-skills --class operation --class documentation
   ```

   Capture stdout. Block on non-zero exit.

8. **Assign skills to each task.** Present the complete draft and the operation/documentation array to the LLM. Select one to three skills per task. Block with explicit no-match evidence when no valid assignment exists. Reconcile every selected name against the array. Do not score, rank, rerank, clip, or use lexical fallback.

9. **Inspect contracts.** Read each selected skill's `SKILL.md` at its collector-winning `path` from the array. Verify the contract matches the task.

10. **Write the completed draft.** Write the completed `{summary, tasks}` object with every task's `skills` populated to the workspace as `draft.json`.

11. **Publish.** Run from the workspace directory:

    ```bash
    uv run --directory ~/.config/opencode/scripts/python init-task-packet \
      --output-dir . < draft.json
    ```

    Derives a safe filename, writes atomically, and prints the output path. Move the published file to `tasks.json` in the workspace root. Block on non-zero exit.

12. **Validate and fix.** Run in a loop until valid:

    ```bash
    uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
      tasks.json \
      --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json \
      --auto-fix --state-file
    ```

    - Exit 0 without `"fixed": true` → done.
    - Exit 0 with `"fixed": true` → file fixed in place, read it back, retry.
    - Exit 1 → structural violations remain, read errors from stderr, fix, retry.
    - Exit 2 → unrecoverable. Block.

### Render and Validate Workspace

13. **Render tasks.md.** Run:

    ```bash
    uv run --directory ~/.config/opencode/scripts/python render-task-markdown \
      --input tasks.json \
      --output tasks.md
    ```

    Block on non-zero exit.

14. **Validate the workspace.** Confirm every task purpose appears in `tasks.md` in order. Confirm all copied sources exist. Confirm `tasks.json` is present and readable.

## Guardrails

- Collect skills twice exactly as shown. Do not swap the arrays between phases.
- Do not score, rank, rerank, clip, or use lexical fallback.
- Do not manually populate, correct, reorder, or remove `skills`.
- Fail closed. Leave no partial outputs.
- Planning loads are passive context. Only task-declared skills are executable.
- Preserve source files, source paths, task field order, and task context.

## References

- `reference/workspace-contract.md`
- `reference/task-authoring.md`
- `reference/scripts.md`
