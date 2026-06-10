---
name: runbook-specification-analyst
description: Use when a spawning orchestrator delegates transforming validated runbook intake JSON from an approved plan into structured runbook workspace specification JSON for downstream processing by the workspace creator.
class: delegated
---

# Runbook Specification Analyst Delegation Handler

Transforms validated runbook intake data from the intake lane into structured runbook workspace specification JSON ready for downstream workspace creation.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `intake_data` | Packet field from runbook-intake-lane output | JSON object with keys: goal, non_goals, accepted_decisions, constraints, acceptance_criteria, scope_in, scope_out, risks_to_monitor, suggested_delegation | Source material for generating runbook specification |
| `runbook_id_slug` | Packet field or state file path | Lowercase alphanumeric with hyphens matching `.plans/<timestamp>-<slug>/` directory name | Target runbook workspace identifier used in all generated artifact paths and references |

## Bounded Worker Objective (Single Goal)

Produce structured JSON output that defines the complete runbook workspace specification including runbook_id_slug, step units with dependency edges, delegation map, manifest requirements, validation checkpoints, and state-init readiness — ready for downstream task-writer and workspace-creator delegated skills to materialize.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract `intake_data` JSON and `runbook_id_slug` string
2. Validate that intake_data contains required keys: goal (non-empty), constraints (array non-empty), acceptance_criteria (array minimum)
3. Transform accepted_decisions array into runbook-level decision summaries suitable for INDEX.md
4. Derive step units from acceptance criteria and scope boundaries, establishing dependency edges between steps
5. Construct delegation map referencing backing skills for each step type
6. Generate manifest requirements listing all files needed for runbook workspace
7. Define validation checkpoints from acceptance criteria and constraints
8. Assess state-init readiness based on completed upstream steps
9. Generate output JSON according to Output Contract below
10. Validate completion by checking all required keys present

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - None; this is a pure transformation skill receiving input via delegation packet JSON
- **Write/create paths**: None - outputs returned via stdout as JSON
- **State mutations**: None - worker does not modify any state files

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and values, arrays where appropriate | Must include: `status`, `runbook_id_slug`, `goal_section`, `non_goals_section`, `source_proposal_reference`, `accepted_decisions_list`, `constraints_section`, `step_units_spec`, `delegation_map`, `manifest_requirements`, `validation_checkpoints`, `state_init_readiness` | Check all required keys present in JSON parse; verify goal_section and constraints_section non-empty strings |

Example output structure:
```json
{
  "status": "completed",
  "runbook_id_slug": "1781039100-build-runbook-orchestrated-delegated",
  "goal_section": "**Goal:** Create an orchestrated runbook with delegated backing skills for building runbooks.",
  "non_goals_section": "- Does not create proposal artifacts\n- Does not execute runbook steps",
  "source_proposal_reference": ".proposals/1781038954-build-runbook-orchestrated-delegated/INDEX.md",
  "accepted_decisions_list": [{"decision": "Use delegated class for specialization", "rationale": "Proposal accepted"}],
  "constraints_section": "**Prerequisites:** Step 01 completed\n**Sequencing:** Steps must complete in order",
  "step_units_spec": [
    {"step_id": "02-author-runbook-specification-analyst", "depends_on": ["01-author-runbook-intake-lane"]},
    {"step_id": "03-author-runbook-workspace-creator", "depends_on": ["02-author-runbook-specification-analyst"]}
  ],
  "delegation_map": {
    "workspace_creation": "runbook-workspace-creator",
    "step_writing": "runbook-step-writer"
  },
  "manifest_requirements": {
    "create": ["main.xml", "state.xml"],
    "modify": [],
    "delete": []
  },
  "validation_checkpoints": [
    {"gate": "Framework compliance", "command": "uv run --project scripts/python validate-skill-framework skills/runbook/*"},
    {"gate": "File structure", "check": "All required files present"}
  ],
  "state_init_readiness": true
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
| Input constraint violation | Missing goal, constraints, or acceptance_criteria in intake_data | Return failed with error_type=validation_error | Prompt user for clearer plan data; do not proceed |
| JSON parse failure | Invalid JSON from upstream packet | Return failed with error_type=parse_error | Request restart of intake-lane step |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"runbook-specification-analyst"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification