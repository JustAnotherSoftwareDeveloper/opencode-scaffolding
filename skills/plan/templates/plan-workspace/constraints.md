id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: "../../.proposals/<timestamp>-<proposal-slug>/INDEX.md"
---

# Constraints

## Prerequisites

- <Required state, files, or conditions that must exist before execution.>
- <External dependency versions, API availability, etc.>

## Sequencing Rules

- Phase 1 → Phase 2 (must complete validation first)
- <Any other ordering requirements>

## Hard Boundaries

- Do NOT touch: `<file>` — belongs to another system/workload.
- Environment limits: max memory/time constraints if any.

## Assumptions & Risks

| Assumption | What invalidates it | Mitigation |
|------------|---------------------|------------|
| <We assume X works> | <If Y fails> | <Fall back to Z or note in rollback> |