---
name: plan
description: "Use when converting a memo and supporting documents into a copied-source workspace with executable task JSON and reviewable task Markdown."
tags:
  - task-planning
  - memo-analysis
  - task-packets
  - markdown-rendering
  - source-provenance
class: operation
---

# Plan

Create an evidence-preserving plan workspace from a primary memo and related documents.

## Normalize Input

Require a topic or summary and one primary memo path.

Accept zero or more memo-support, analysis, research, requirements, design, notes, and other source paths.

Store memo-support sources in the `memo` category.

Return `BLOCKED: Missing plan topic.` when the topic is absent.

Return `BLOCKED: Missing primary memo.` when the primary memo is absent.

## Procedure

1. Validate every source path under the workspace contract in `./reference/workspace-contract.md`.
2. Derive a lowercase kebab-case summary slug and an epoch-millisecond timestamp.
3. Create `$CWD/.plans/<epoch-ms>-<summary-slug>/` without replacing an existing directory.
4. Copy each validated source into its category directory and preserve its relative workspace path.
5. Produce schema-valid `{summary, tasks}` TaskDraftList JSON without `skills` by applying `./reference/task-authoring.md`.
6. Pipe the complete draft object to `generate-task-json --output-file "$PLAN_DIR/tasks.json"`.
7. Invoke `render-task-markdown` with `$PLAN_DIR/tasks.json` and `$PLAN_DIR/tasks.md`.
8. Validate the workspace under `./reference/workspace-contract.md`.
9. Return only the relative `.plans/<epoch-ms>-<summary-slug>/` path.

## Guardrails

- Treat `tasks.json` as the canonical task packet.
- Generate `tasks.md` only from the validated `tasks.json` output.
- Do not add fields outside the existing task-packet schema.
- Do not assign `skills` manually.
- Do not modify source documents while copying them.
- Return `BLOCKED: <reason>` for invalid sources, script failure, or validation failure.

## Self-Validation

- [ ] The workspace name matches the required timestamp and slug format.
- [ ] Every source document exists under its declared category directory.
- [ ] `tasks.json` validates through the shared task generator.
- [ ] `tasks.md` exists and renders every final task purpose in order.
- [ ] The task count and task purposes match in `tasks.json` and `tasks.md`.

## Expected Output

Create `.plans/<epoch-ms>-<summary-slug>/` with `tasks.json`, `tasks.md`, and copied categorized source documents.

Return the relative workspace path only.

## Docs

See `./reference/README.md` for documentation of supporting files.
