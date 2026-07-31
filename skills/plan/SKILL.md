---
name: plan
description: "Use when creating a source-document plan workspace that produces executable task JSON."
schema_version: "1.0"
cues:
  - {facet: operation, value: "create-plan-workspace", primary: true}
  - {facet: subject, value: "source documents"}
  - {facet: outcome, value: "executable task JSON"}
  - {facet: interface, value: "plan workspace"}
relationships:
  - {role: owner, rationale: "owns source-document planning"}
class: operation
---

# Plan

Create an evidence-preserving plan workspace from source documents.

## Normalize Input

Require either a topic or summary.

Require one or more source-document paths.

Accept an optional source category for each path.

Assign uncategorized paths to `other`.

Return `BLOCKED: Missing plan topic.` when the topic is absent.

Return `BLOCKED: Missing source documents.` when no source paths are supplied.

## Procedure

1. Validate every source path under the [workspace contract](./reference/workspace-contract.md).
2. Derive a lowercase kebab-case summary slug.
3. Derive an epoch-millisecond timestamp.
4. Create `$CWD/.plans/<epoch-ms>-<summary-slug>/` without replacing an existing directory.
5. Copy each validated source into its category directory.
6. Preserve each source filename.
7. Add a deterministic suffix to resolve a filename collision.
8. Produce schema-valid `{summary, tasks}` TaskDraftList JSON without `skills` under [task-authoring rules](./reference/task-authoring.md).
9. Pipe the complete draft object to `generate-task-json --output-file "$PLAN_DIR/tasks.json"`.
10. Render task Markdown under [script contracts](./reference/scripts.md).
11. Validate the workspace under the [workspace contract](./reference/workspace-contract.md).
12. Return only the relative `.plans/<epoch-ms>-<summary-slug>/` path.

## Guardrails

- Treat `tasks.json` as the canonical task packet.
- Generate `tasks.md` only from the validated `tasks.json` output.
- Do not add fields outside the existing task-packet schema.
- Do not assign `skills` manually.
- Do not modify source documents while copying them.
- Return `BLOCKED: <reason>` for invalid sources, script failure, or validation failure.

## Self-Validation

- [ ] The workspace name contains the required timestamp.
- [ ] The workspace name contains the required slug.
- [ ] Every source document exists under its declared category directory.
- [ ] `tasks.json` validates through the shared task generator.
- [ ] `tasks.md` exists.
- [ ] `tasks.md` renders every final task purpose in order.
- [ ] The task count matches in `tasks.json` and `tasks.md`.
- [ ] The task purposes match in `tasks.json` and `tasks.md`.

## Expected Output

Create `.plans/<epoch-ms>-<summary-slug>/`.

Create `tasks.json`.

Create `tasks.md`.

Copy categorized source documents.

Return the relative workspace path only.

## Docs

See `./reference/README.md` for documentation of supporting files.
