---
name: planning-pipeline-architecture
description: "Use when selecting analysis, proposal, and plan stages in a planning lifecycle."
tags:
  - planning-lifecycle
  - pipeline-stages
  - stage-selection
  - analysis-workflow
  - proposal-workflow
  - plan-workflow
class: planning
---

# Planning Pipeline Architecture — Domain Planning Reference

This skill documents the planning lifecycle around analysis, proposal, and plan work.

## Domain Context

- `generic-analysis` produces an evidence-calibrated assessment with conclusions, uncertainty, and next actions.
- `proposal` produces an evidence-based decision workspace from explicit source documents.
- `plan` produces an evidence-preserving plan workspace with executable task JSON and rendered task Markdown.
- Analysis, proposal, and plan represent distinct planning stages with different entry conditions and artifacts.
- Proposal and plan workspaces preserve their source documents as part of their respective contracts.

## Key Considerations

- Analysis fits requests that require an assessment, conclusion, comparison, or recommendation.
- Proposal fits requests that require a durable decision record, approval, or feedback.
- Plan fits requests that require executable task planning from source documents.
- A persisted analysis document provides a source artifact for proposal work.
- A proposal workspace and its source evidence provide source artifacts for plan work.
- Assumptions and open questions remain visible through every later planning stage.
- The stages are selectable independently; the full lifecycle is not mandatory for every request.

## Common Workflows

- [Analysis Only](./reference/analysis-only.md) — Produces a terminal assessment without a decision or plan workspace.
- [Proposal Only](./reference/proposal-only.md) — Produces a decision workspace from existing source documents.
- [Plan Only](./reference/plan-only.md) — Produces a plan workspace from existing source documents.
- [Analysis To Proposal](./reference/analysis-to-proposal.md) — Moves from uncertain assessment to an evidence-backed decision record.
- [Analysis To Plan](./reference/analysis-to-plan.md) — Moves from documented assessment to executable planning without a decision workspace.
- [Proposal To Plan](./reference/proposal-to-plan.md) — Moves from a decision record to executable planning.
- [Analysis To Proposal To Plan](./reference/analysis-to-proposal-to-plan.md) — Connects assessment, decision, and executable planning.

## Related Skills

- `generic-analysis` — Produces evidence-calibrated assessments.
- `proposal` — Produces evidence-based decision workspaces.
- `plan` — Produces evidence-preserving plan workspaces.

## Files

- [reference/README.md](./reference/README.md) — Indexes the planning lifecycle workflow references.
- [reference/analysis-only.md](./reference/analysis-only.md) — Describes the terminal assessment workflow.
- [reference/proposal-only.md](./reference/proposal-only.md) — Describes direct decision-record creation.
- [reference/plan-only.md](./reference/plan-only.md) — Describes direct executable-plan creation.
- [reference/analysis-to-proposal.md](./reference/analysis-to-proposal.md) — Describes the assessment-to-decision workflow.
- [reference/analysis-to-plan.md](./reference/analysis-to-plan.md) — Describes the assessment-to-plan workflow.
- [reference/proposal-to-plan.md](./reference/proposal-to-plan.md) — Describes the decision-to-plan workflow.
- [reference/analysis-to-proposal-to-plan.md](./reference/analysis-to-proposal-to-plan.md) — Describes the complete planning lifecycle.

## Docs

See `./reference/README.md` for planning lifecycle workflow references.
