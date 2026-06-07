# Skill Class Selection Guide

Guidance for selecting the appropriate skill class (atomic, orchestrated, documentation, planning) based on triggers and work patterns.

## Quick Decision Matrix

| If your work is... | Choose this class |
|--------------------|-------------------|
| Single bounded procedure with independent validation | `atomic` |
| Coordinates sub-skills, workers, state, or quality gates | `orchestrated` |
 | Reference material loaded via delegation for knowledge sharing | `documentation` |
| Artifact/lifecycle creation (proposal→plan→runbook) | `planning` |

## Class Contracts & Selection Criteria

### atomic — Single Bounded Procedure
**Schema:** `skills/skill-hygiene/schemas/atomic.xsd`

Use when ALL of these apply:
- One primary objective with clear success criteria
- Independent inputs → outputs transformation  
- Can be validated in isolation (self-contained)

**Anti-patterns:** Avoid for coordination work or multi-phase workflows.

### orchestrated — Coordinates Sub-Skills/Workflows
Coordinates phases, workers, state, quality gates, or multiple skills. Use when the primary job is management/routing rather than execution. See schema: `skills/skill-hygiene/schemas/orchestrated.xsd`.

**Triggers:** Multiple steps needing different specialists; conditional branching; retry loops with quality checks.

### documentation — Reference Store
Reference material loaded via delegation for knowledge sharing. Primary value comes from other skills loading it, not executing procedures. Includes freshness policy and citations. See schema: `skills/skill-hygiene/schemas/documentation.xsd`.

**Triggers:** Conventions others should reference; policies needing currency tracking; shared knowledge across workflows.

### planning — Artifact/Lifecycle Creation
Creates or reviews lifecycle artifacts (proposal→plan→runbook) and manages transitions between them. Triggers include new initiative kickoff, revision planning loops, or review orchestration. See schema: `skills/skill-hygiene/schemas/planning.xsd`.

**Triggers:** Starting a new runbook; updating an existing plan based on findings; coordinating review cycles for artifacts.

## How to Decide

1. Identify the main unit of work
2. Ask: "Does this validate in isolation?" → likely atomic  
3. Ask: "Does this coordinate other skills/phases?" → orchestrated  
4. Ask: "Will others load this via delegation?" → documentation  
5. Ask: "Is primary job artifact creation or lifecycle management?" → planning

## Reference Trigger Language for Each Class Description Field

- **atomic**: `Use when you need to <single bounded action>`
- **orchestrated**: `Use when coordinating <multiple steps/phases/skills>`
- **documentation**: `Use when creating/reviewing reference material others load via delegation`  
- **planning**: `Use when creating or reviewing proposal/plan/runbook lifecycle artifacts`