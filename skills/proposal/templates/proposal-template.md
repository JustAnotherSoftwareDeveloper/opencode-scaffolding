---
artifact_type: proposal
schema_version: 2
id: <unix-timestamp>-slug
title: <human title>
status: draft | needs-clarification | accepted | rejected | superseded
created_at: <iso timestamp>
updated_at: <iso timestamp>
owner: orchestrator
source_request: <short user request>
related_plan: null | ../.plans/<unix-timestamp>-slug/INDEX.md
related_runbook: null | ../.runbooks/<unix-timestamp>-slug/main.xml
---
# Proposal: <title>

## Goal

## Intent Classification

### Work Type
harness | code | docs | research | architecture | recovery | review | other

### Risk Level
low | medium | high

### Discovery Needed
none | local | external | both

### OpenCode Docs Needed
none | agents | commands | permissions | skills | tools | rules | config | multiple

### User Clarification Needed
none | optional | required

### Planning Requirement
skip | light plan | full plan

## Proposal Depth Tier
none | light | standard | deep

## Current State

## Problem / Opportunity

## In Scope

## Out of Scope

## Recommended Approach

## Alternatives Considered

## Artifact and State Impact

## Delegation Model

### Analyst Lane Selection Rationale
<!-- For deep proposals: justify which exploration/analysis lanes are required, recommended, or optional based on the depth-tier lane matrix. -->

### Delegated Analysis Summary
<!-- For deep proposals: summarize tradeoffs, risks, contradictions, framework-fit assessment, and decision impact from analysis lanes. -->

## Risks and Unknowns

## Discovery Results

### Discovery Evidence Ledger
<!-- For deep proposals: record source-backed findings with lane, worker, source, claim/fact, inference, assumption, confidence, relevance, fit caveat, and decision impact. -->

| Lane | Worker | Source | Claim / Fact | Inference | Assumption | Confidence | Relevance | Fit Caveat | Decision Impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <!-- e.g., Local explorer --> | <!-- e.g., worker-sm --> | <!-- e.g., skills/proposal/SKILL.md --> | <!-- Observed fact --> | <!-- Inferred meaning --> | <!-- Stated assumption --> | <!-- High/Medium/Low --> | <!-- Why this matters --> | <!-- Limitations or staleness --> | <!-- How this influences the approach --> |

## Clarification Questions

<!-- Use [NEEDS CLARIFICATION: ...] markers for unresolved blocking ambiguity. Tag as blocking (must resolve) or minor (can proceed with default). -->

## Planning Handoff

### Agreed Objective
<One or two sentences that become plan.objective.>

### Accepted Decisions
- <Decision and reason.>

### Scope Boundaries
In scope:
- ...

Out of scope:
- ...

### Constraints
- ...

### Acceptance Criteria to Preserve
- <Criterion that planning must map to gates/steps.>

### Risks to Monitor During Planning
- ...

### Suggested Delegation / Skills
- discovery: worker-* with generic-mode instructions
- analysis: worker-* with review-mode instructions
- implementation: worker-* with coding-mode instructions
- docs/templates: worker-* with documentation-mode instructions

### OpenCode Docs Required for Handoff / Delegation Design
- Agents: <https://opencode.ai/docs/agents/>
- Skills: <https://opencode.ai/docs/skills/>
- Permissions: <https://opencode.ai/docs/permissions/>
- Tools: <https://opencode.ai/docs/tools/>
- Rules / AGENTS.md: <https://opencode.ai/docs/rules/>
- Commands, when command handoffs are in scope: <https://opencode.ai/docs/commands/>
- Config, when agent or permission registration is in scope: <https://opencode.ai/docs/config/>

### Required Planning Analysis
- problem breakdown
- dependency graph
- parallel groups
- delegation packet inventory

## Update-vs-New Decision
<!-- When revising a related proposal, record the decision to revise, supersede, or create a new artifact, with a brief justification. -->

## Specification Quality Checklist
<!-- Before embedded review, verify: -->
- [ ] What/why is clearly separated from how
- [ ] Acceptance criteria are independently testable
- [ ] Blocking ambiguity is marked with [NEEDS CLARIFICATION: ...]
- [ ] Minor ambiguity has recommended defaults
- [ ] Given/When/Then scenarios are used for behavioral criteria
- [ ] Evidence ledger (if present) has confidence and fit caveats
- [ ] No implementation plans, task breakdowns, or runbook state

## Acceptance Criteria

<!-- Provide independently verifiable checks. Use scenarios for behavior: -->
<!-- Given <context>, When <action>, Then <outcome> -->

## Embedded Quality Check

## Decision
