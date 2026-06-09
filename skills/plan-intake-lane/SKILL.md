---
name: plan-intake-lane
description: Use when a spawning orchestrator delegates proposal artifact validation and planning handoff extraction to verify accepted status and produce structured contract data.
class: delegated
---

# Plan Intake Lane Delegation Handler

Validates an accepted proposal artifact exists, has correct status, extracts the planning handoff data contract for downstream processing by other delegated skills in the plan orchestration pipeline.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `proposal_path` | Delegation packet or orchestrator state file | Absolute or relative path (`.proposals/<timestamp>-<slug>/INDEX.md`) | Target proposal workspace to validate and parse |

## Bounded Worker Objective (Single Goal)

Verify the proposal at the specified path exists, has `status: accepted`, then extract goal, non-goals, decisions, constraints, acceptance criteria, scope boundaries, risks, and delegation/skill suggestions into a structured handoff JSON blob.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to get proposal_path
2. Verify the proposal path exists as `.proposals/<timestamp>-<slug>/INDEX.md` workspace with `metadata.md` showing `status: accepted`, or historical single-file with frontmatter status
3. Extract planning-relevant data from proposal sections: Goal, Non-Goals, Accepted Decisions, Constraints, Acceptance Criteria, Scope Boundaries (In/Out), Risks to Monitor, Suggested Delegation/Skills
4. Generate output JSON with required fields per Output Contract below
5. Validate completion by checking for success fields presence

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Proposal workspace directory `.proposals/<timestamp>-<slug>/INDEX.md` and sibling files (`metadata.md`, `source.md`, etc.)
  - Historical proposal file if present
- **Write/create paths**: None required; output returned via stdout/JSON handback
- **State mutations**: None

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and values, arrays where appropriate | Must include: `status`, `proposal_path`, `goal`, `non_goals`, `accepted_decisions`, `constraints`, `acceptance_criteria`, `scope_in`, `scope_out`, `risks_to_monitor`, `suggested_delegation` | Check all required keys present in JSON parse |

Example output structure:
```json
{
  "status": "completed",
  "proposal_path": ".proposals/1785000000-plan-skill-orchestrated-delegated-rewrite/INDEX.md",
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

- **Artifact exists**: Check proposal path from input contract was found and readable
- **Status validated**: Confirmed `status: accepted` in workspace metadata.md or historical frontmatter
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

Error types: `not_found`, `validation_error` (status not accepted), `parse_error`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Proposal path not found | File system check on proposal_path | Return failed with error_type=not_found | Skip dependent tasks, log missing artifact |
| Status not accepted | Read status from metadata.md/frontmatter | Return failed with error_type=validation_error | Do not proceed to plan creation; request user clarification |
| Parse/Extract error | Missing required content in proposal sections | Return failed with error_type=parse_error | Request clearer proposal or fill missing fields |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"plan-intake-lane"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification