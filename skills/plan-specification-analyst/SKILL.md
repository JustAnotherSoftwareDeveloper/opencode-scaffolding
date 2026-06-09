---
name: plan-specification-analyst
description: Use when a spawning orchestrator delegates transformed proposal decisions into structured plan workspace specification content including goal, constraints, file impact, and validation sections.
class: delegated
---

# Plan Specification Analyst Delegation Handler

Transforms accepted decisions from the intake lane output into structured analysis that defines required plan workspace sections, producing plan specification content/structure not execution runbook state.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `intake_data` | Packet field from plan-int intake-lane output | JSON object with keys: goal, non_goals, accepted_decisions, constraints, acceptance_criteria, scope_in, scope_out, risks_to_monitor, suggested_delegation | Used as source material for generating plan specification sections |
| `plan_id_slug` | Packet field or state file path | Lowercase alphanumeric with hyphens matching `.plans/<timestamp>-<slug>/INDEX.md` directory name | Target plan workspace identifier used in all generated artifact paths and references |

## Bounded Worker Objective (Single Goal)

Produce structured JSON output that defines the complete plan specification including goal section, non-goals, source proposal reference, accepted decisions summary, constraints from input, file impact analysis derived from scope_in/scope_out boundaries, and validation checkpoints — ready for downstream task-writer delegated skill to materialize into markdown files.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract `intake_data` JSON and `plan_id_slug` string
2. Validate that intake_data contains required keys: goal (non-empty), constraints (array non-empty), acceptance_criteria (array) minimum
3. Transform accepted_decisions array into planning-level decision summaries suitable for Accepted Decisions section in plan INDEX.md
4. Derive file impact analysis from scope_in/scope_out arrays combined with constraint knowledge to produce artifact list
5. Construct validation checkpoints from acceptance criteria and constraints
6. Generate output JSON according to Output Contract below
7. Validate completion by checking all required keys present

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - None; this is a pure transformation skill receiving input via delegation packet JSON
- **Write/create paths**: None - outputs returned via stdout as JSON
- **State mutations**: None - worker does not modify any state files

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and values, arrays where appropriate | Must include: `status`, `plan_id_slug`, `goal_section`, `non_goals_section`, `source_proposal_reference`, `accepted_decisions_list`, `constraints_section`, `file_impact_analysis`, `validation_checkpoints` | Check all required keys present in JSON parse; verify goal_section and constraints_section non-empty strings |

Example output structure:
```json
{
  "status": "completed",
  "plan_id_slug": "1786000000-plan-skill-orchestrated-delegated-rewrite",
  "goal_section": "**Goal:** Transform skills/plan/SKILL.md from planning to orchestrated class with four delegated backing skills...",
  "non_goals_section": "- Does not create new proposal artifacts\n- Does not modify plan execution state",
  "source_proposal_reference": ".proposals/1785000000-plan-skill-orchestrated-delegated-rewrite/INDEX.md",
  "accepted_decisions_list": [{"decision": "Convert class from planning to orchestrated", "rationale": "Proposal accepted"}],
  "constraints_section": "**Prerequisites:** Step 01 inventory completed\n**Sequencing:** Steps must complete in order",
  "file_impact_analysis": {
    "create": ["skills/plan-specification-analyst/SKILL.md"],
    "modify": [],
    "delete": []
  },
  "validation_checkpoints": [
    {"gate": "Framework compliance", "command": "uv run --project scripts/python validate-skill-framework skills/plan/*"},
    {"gate": "File structure", "check": "All required files present"}
  ]
}
```

## Validation / Evidence Requirements

- **Input validated**: Confirmed intake_data has all required keys populated with non-empty values for goal, constraints minimum
- **Output valid JSON**: Output parses as valid JSON without error  
- **Required fields present**: All output contract keys verified in parsed result
- **No failure markers**: No exception traces or error state indicators

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|parse_error>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": []
}
```

Error types: `validation_error` (missing required input fields), `parse_error`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Input constraint violation | Missing goal, constraints, or acceptance_criteria in intake_data | Return failed with error_type=validation_error | Prompt user for clearer proposal data; do not proceed |
| JSON parse failure | Invalid JSON from upstream packet | Return failed with error_type=parse_error | Request restart of intake-lane step |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"plan-specification-analyst"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification