# Plan Only

`plan-only` - `plan` - Produces an evidence-preserving plan workspace from explicit source documents.

**Use when:** Existing requirements, decisions, or source evidence require executable task planning without new analysis or a proposal workspace.

## Purpose

This workflow produces a task plan from a defined source set.
The plan workspace preserves the sources and records validated task JSON with rendered task Markdown.

## Sequence

1. Existing source documents establish the planning context.
2. The source set forms the basis for a plan workspace.
3. The plan workspace records executable task JSON and rendered task documentation.
4. The planning lifecycle ends with an executable plan artifact.

## Artifacts

- Supporting source documents.
- Plan workspace containing `tasks.json` and `tasks.md`.

## Notes

- The source set contains explicit document paths.
- Source-derived constraints remain present in task context.
- Unresolved material remains labeled as `Open Question:` in task context.
- Unverified material remains labeled as `Assumption:` in task context.
