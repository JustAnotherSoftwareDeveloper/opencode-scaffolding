# Plan Only

`plan-only` - `plan-writer` - Produces an evidence-preserving plan workspace from explicit source documents without a proposal-derived audit by default.

**Use when:** Existing requirements, decisions, or source evidence require executable task planning without new analysis or a proposal workspace.

## Purpose

This workflow describes direct planning from a defined source set. The plan
workspace preserves the sources and contains task JSON with rendered task Markdown.

## Sequence

- Existing source documents establish the planning context.
- `plan-writer` owns the direct plan workspace and its source-preserving task
  artifacts.
- Publication of the direct plan-only artifact does not imply `Audit pending` or a
  proposal-derived re-audit obligation.
- An explicit audit request is the only additional condition that introduces an
  audit handoff; the applicable audit baseline and capability requirements remain
  separate from this direct path.

## Artifacts

- Supporting source documents.
- Plan workspace containing `tasks.json` and `tasks.md`.

## Notes

- The source set contains explicit document paths.
- Source-derived constraints remain present in task context.
- Unresolved material remains labeled as `Open Question:` in task context.
- Unverified material remains labeled as `Assumption:` in task context.
- Direct plan-only context is not relabeled as proposal-derived when no proposal
  exists.
