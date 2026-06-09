---
name: proposal
description: Use when coordinating delegated exploration, analysis, and synthesis lanes to create a bounded decision-artifact before planning or implementation.
class: orchestrated
---

# Proposal Skill (Orchestrator)

Coordinates multi-phase discovery, synthesis, and quality gates for creating bounded proposals that inform planning decisions without leaking into execution artifacts. Uses the `delegation` skill as the routing source of truth; all worker assignments flow through delegation packets constructed per `skills/delegation/templates/delegation-packet.md`.

## Delegated Backing Skills

| Lane Name | Purpose | Input From Orchestrator | Output To Orchestrator |
|-----------|---------|------------------------|------------------------|
| proposal-local-lane | Discover current harness files, skills, runbooks, conventions | Scope boundaries, file paths to inspect | Evidence list with confidence levels, skills/runbook inventory |
| proposal-historical-lane | Inspect prior proposals/plans/runbooks for related decisions | Search terms, artifact types, date range filters | Key findings table linking artifacts and decision precedents |
| proposal-external-lane | Research external frameworks/standards with cited facts | URLs or topic keywords checklist | Cited references with fit caveats and confidence ratings |
| proposal-synthesis-analyst | Merge lane outputs into decision-ready tradeoffs/risks | All delegate evidence ledgers from completed lanes | Trade-offs table, contradictions summary, candidate acceptance criteria |
| proposal-review-analyst | Validate 13-file workspace completeness/quality gates | Workspace path to review | Review report with gaps, risky sections, pass/fail determination |

## Orchestration Protocol

### When to Use This Skill

Use when creating a bounded proposal for non-trivial, ambiguous, or high-impact changes that require discovery, analysis synthesis before planning. Trigger conditions:
- Request affects agents, skills, commands, permissions, state, or orchestration behavior
- Architecture-sensitive changes requiring external-framework evaluation

### Do Not Use When

- Direct implementation without analysis is required (use worker mode directly)
- The task is trivial (typo fix, surface change)—no proposal needed for such changes

## Serial Delegation Workflow

1. **Launch exploration lanes** — Per the delegated skills, route discovery work via delegation packets:
   - Local lane: inventory current state when harness impact exists
   - Historical lane: inspect priors when similar artifacts may conflict
   - External lane: research frameworks as needed citing external standards
2. **Synthesize findings** — After lanes complete, delegate to synthesis analyst if 2+ lanes were launched or architectural tradeoffs exist.
3. **Draft proposal artifact** — Create `.proposals/<unix-timestamp>-slug/` with all 13 required files:
   - `INDEX.md`, `metadata.md`, `goal.md`, `problem-opportunity.md`
   - `scope.md`, `recommended-approach.md`, `alternatives-considered.md`
   - `risks-and-unknowns.md`, `acceptance-criteria.md`, `decision.md`
   - `clarification-questions.md`, `artifact-and-state-impact.md`, `discovery-results.md`
5. **Run embedded review** — Delegate to proposal-review-analyst for quality gate validation before user decision.

## Lane Packet Requirements (Per Delegation Skill)

For each delegated lane, construct a bounded handoff packet via the delegation template that includes:

| Item | Requirement |
|------|-------------|
| Objective | One clear, bounded goal for the lane |
| Source / file boundaries | Exact paths or URLs in scope |
| Out-of-scope | Explicit exclusions to prevent proposal-vs-plan leakage |
| Output contract | Required format with facts/inferences/assumptions and confidence levels |
| Do / do-not rules | Must reject dependency graphs, task breakdowns, implementation steps per plan runbook boundary rule |

## Evidence Ledger Mapping

Accept worker findings into `discovery-results.md` using this structure:

| Lane | Worker | Source | Claim/Fact | Inference | Assumption | Confidence | Relevance | Fit Caveat | Decision Impact |
|------|--------|--------|------------|-----------|------------|------------|-----------|------------|-----------------|

External-source facts must include `[Source: URL]` citations. Historical and local findings map to lane origin per packet receipt.

## Embedded Review Criteria

Before user decision, the review analyst checks:
- **Completeness**: All 13 files present with required content (use "None" when inapplicable)
- **Clarity**: what/why separated from how; independent testability of acceptance criteria
- **Scope boundaries**: `scope.md` explicitly states In/Out of scope items  
- **Proposal-vs-plan boundary**: No dependency graphs, task breakdowns, or implementation steps
- **Evidence quality**: Source citations with confidence and fit caveats in discovery-results.md

## Decision / Status Handling

- `[NEEDS CLARIFICATION: ...]` — Use exact syntax for blocking ambiguity; classify as `blocking` or `minor`
- Decision statuses: `draft`, `accepted`, `needs-clarification`, `rejected`, `superseded`
- Auto-accept only when explicitly authorized by user/command—otherwise report decisions for user action

## Plan-Boundary Guardrails  

Proposal artifacts are **read-only** after creation. Do not migrate, rewrite, or split historical `.proposals/*.md` files unless a future accepted proposal explicitly authorizes migration. Plans use `tasks/` directory; runbooks use isolated `steps/` XML — these never appear in proposals.

## Validation Command

```bash
uv run --project scripts/python validate-skill-framework skills/proposal/SKILL.md
```