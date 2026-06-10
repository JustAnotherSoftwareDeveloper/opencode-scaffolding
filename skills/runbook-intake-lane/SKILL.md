---
name: runbook-intake-lane
description: Use when a spawning orchestrator delegates validating approved markdown plans and extracting runbook-generation handoff data to produce structured contract data for downstream processing.
class: delegated
---

# Runbook Intake Lane Delegation Handler

Validates an approved plan artifact exists with correct status, extracts runbook generation handoff fields for downstream specification analysis in the runbook orchestration pipeline.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `plan_path` | Delegation packet or orchestrator state file | Absolute or relative path (`.plans/<timestamp>-slug/INDEX.md`) | Target plan workspace to validate and parse |
| `proposal_path` | State file reference | Path from state.xml proposal field | Linked proposal to verify acceptance |

## Bounded Worker Objective (Single Goal)

Verify the plan at the specified path exists with `status: approved`, confirm linked proposal has `status: accepted`, then extract goal, constraints, scope boundaries, acceptance criteria, and delegation suggestions into a structured handoff JSON blob for downstream runbook specification analysis.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to get plan_path and proposal_path
2. Verify the plan path exists as `.plans/<timestamp>-<slug>/INDEX.md` workspace with `metadata.md` showing `status: approved`
3. Read linked proposal and confirm `status: accepted` in its metadata/frontmatter
4. Extract planning-relevant data from plan sections: Goal, Non-Goals, Accepted Decisions, Constraints, Acceptance Criteria, Scope Boundaries (In/Out), Risks to Monitor, Suggested Delegation/Skills
5. Generate output JSON with required fields per Output Contract below
6. Validate completion by checking for success fields presence

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Plan workspace directory `.plans/<timestamp>-<slug>/INDEX.md` and sibling files (`metadata.md`, `source.md`, etc.)
  - Proposal workspace `.proposals/<timestamp>-<slug>/INDEX.md` and sibling files
- **Write/create paths**: None required; output returned via stdout/JSON handback
- **State mutations**: None

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and values, arrays where appropriate | Must include: `status`, `plan_path`, `proposal_path`, `goal`, `non_goals`, `accepted_decisions`, `constraints`, `acceptance_criteria`, `scope_in`, `scope_out`, `risks_to_monitor`, `suggested_delegation` | Check all required keys present in JSON parse |

Example output structure:
```json
{
  "status": "completed",
  "plan_path": ".plans/1781039000-build-runbook-orchestrated-delegated/INDEX.md",
  "proposal_path": ".proposals/1781038954-build-runbook-orchestrated-delegated/INDEX.md",
  "goal": "...",
  "non_goals": ["...", "..."],
  "accepted_decisions": [{"decision": "...", "reason": "..."}],
  "constraints": ["..."],
  "acceptance_criteria": ["...", "..."],
  "scope_in": ["..."],
  "scope_out": ["..."],
  "risks_to_monitor": ["...", "..."],
  "suggested_delegation": [{"lane": "...", "skill": "..."}]
}
```

## Validation / Evidence Requirements

- **Artifact exists**: Check plan path from input contract was found and readable
- **Status validated**: Confirmed `status: approved` in plan metadata.md or historical frontmatter
- **Proposal accepted**: Confirmed linked proposal has `status: accepted`
- **Content extracted**: All required output fields populated with non-empty values for goal, constraints, acceptance_criteria minimum
- **JSON valid**: Output parses as valid JSON without error

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<not_found|validation_error|parse_error>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": []
}
```

Error types: `not_found`, `validation_error` (status not approved/accepted), `parse_error`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Plan path not found | File system check on plan_path | Return failed with error_type=not_found | Skip dependent tasks, log missing artifact |
| Status not approved | Read status from metadata.md/frontmatter | Return failed with error_type=validation_error | Do not proceed to runbook creation; request user clarification |
| Proposal not accepted | Read status from proposal metadata | Return failed with error_type=validation_error | Request proposal acceptance before proceeding |
| Parse/Extract error | Missing required content in plan sections | Return failed with error_type=parse_error | Request clearer plan or fill missing fields |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"runbook-intake-lane"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification