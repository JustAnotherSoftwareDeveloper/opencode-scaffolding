# Skill Class Selection Guide

Guidance for selecting the appropriate skill class (operation, delegated, orchestrated, planning) based on triggers and work patterns.

## Quick Decision Matrix

| If your work is... | Choose this class |
|--------------------|-------------------|
| Single bounded procedure with independent validation | `operation` |
| Worker specialization executed via delegation packet | `delegated` |
| Coordinates sub-skills, workers, state, or quality gates | `orchestrated` |
| Artifact/lifecycle creation (proposal→plan→runbook) | `planning` |

## Class Contracts & Selection Criteria

### operation — Single Bounded Procedure
**Schema:** `skills/skill-hygiene/schemas/operation.xsd`

Use when ALL of these apply:
- One primary objective with clear success criteria
- Independent inputs → outputs transformation  
- Can be validated in isolation (self-contained)

**Anti-patterns:** Avoid for coordination work or multi-phase workflows.

### delegated — Worker Specialization via Delegation Packet
**Schema:** `skills/skill-hygiene/schemas/delegated.xsd`

Use when:
- An orchestrator delegates a focused sub-task to an isolated worker
- Worker needs clear inputs from the spawning skill and produces bounded outputs
- Task is small enough for single-execution validation with explicit contracts
- State changes are isolated and reversible

**Triggers:** Sub-agent specialization, packet-based work distribution, outcome-focused workers.

### orchestrated — Coordinates Sub-Skills/Workflows
Coordinates phases, workers, state, quality gates, or multiple skills. Use when the primary job is management/routing rather than execution. See schema: `skills/skill-hygiene/schemas/orchestrated.xsd`.

**Triggers:** Multiple steps needing different specialists; conditional branching; retry loops with quality checks.

**Non-Execution Guardrail:** Orchestrated skills are heavy-procedure coordinators only—they delegate all worker tasks to backing delegated skills or workers. Does not embed step execution that belongs in delegated skills/workers.

### planning — Artifact/Lifecycle Creation
Creates or reviews lifecycle artifacts (proposal→plan→runbook) and manages transitions between them. Triggers include new initiative kickoff, revision planning loops, or review orchestration. See schema: `skills/skill-hygiene/schemas/planning.xsd`.

**Triggers:** Starting a new runbook; updating an existing plan based on findings; coordinating review cycles for artifacts.

## How to Decide

1. Identify the main unit of work
2. Ask: "Does this validate in isolation?" → likely operation  
3. Ask: "Is this a worker specialization for delegation packets?" → delegated  
4. Ask: "Does this coordinate other skills/phases?" → orchestrated  
5. Ask: "Is primary job artifact creation or lifecycle management?" → planning

## Reference Trigger Language for Each Class Description Field

- **operation**: `Use when you need to <single bounded action>`
- **delegated**: `Use when delegating a specialized worker objective`
- **orchestrated**: `Use when coordinating <multiple steps/phases/skills>`
- **planning**: `Use when creating or reviewing proposal/plan/runbook lifecycle artifacts`