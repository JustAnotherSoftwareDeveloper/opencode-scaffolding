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

Create an evidence-preserving plan workspace and assign its tasks through the same direct-selection contract as `breakdown-tasks`.

## Normalize And Preserve Sources

1. Require a topic or summary and one or more source-document paths.
2. Validate every source under `reference/workspace-contract.md`.
3. Derive a lowercase kebab-case slug and epoch-millisecond workspace name without replacing an existing directory.
4. Copy each source into its category directory, preserving its filename or adding a deterministic collision suffix. Never modify source documents.

## Direct Selection And Publication

1. Collect one full inventory snapshot containing planning, operation, and documentation profiles. Freeze it before any selection.
2. Present relevant planning profiles and the source-backed request to the LLM; load every materially relevant planning profile without a numeric cap. Record planning loads separately and block on path or load mismatch.
3. Author a schema-valid `{summary, tasks}` draft without `skills`, preserving copied relative source paths and source-derived constraints.
4. Present operation/documentation profiles and the complete draft to the LLM; select one to three task skills per task, or block with no-match evidence.
5. Inspect selected collector-winning skill contracts, reconcile all names/classes/paths against the same snapshot, and invoke the generator with the final draft and frozen inventory.
6. Generate `tasks.json` atomically, render `tasks.md` only from the validated packet, and validate the complete workspace.

## Guardrails

- Use the same direct-selection semantics as `breakdown-tasks`: no score, rank, threshold, reranker, lexical/path fallback, or manual skill assignment.
- Use one inventory snapshot for planning loads and task assignments; do not recollect.
- Preserve source files, source paths, task field order, and task context.
- Fail closed on invalid sources, missing matches, contract mismatch, validation failure, or publication failure. Never leave partial outputs.

## References

- `reference/workspace-contract.md`
- `reference/task-authoring.md`
- `reference/scripts.md`

## Self-Validation

- Workspace name, copied sources, `tasks.json`, and `tasks.md` are present.
- Every task purpose appears in order in `tasks.md`.
- The packet validates against the shared schema and assignments are snapshot-backed.
