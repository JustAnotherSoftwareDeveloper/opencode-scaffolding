---
name: runbook-step-writer
description: Use when individual v3 XML step files need to be generated from plan tasks with worker delegation metadata embedded in each step.
class: delegated
---

# Runbook Step Writer Delegation Handler

Creates individual v3 XML step files under `.runbooks/<id>/steps/` from approved plan task instructions, enforcing SUPER-atomic criteria, one worker routing target per step, exact input/output artifacts, precise files_in_scope, files_out_scope, expected return format, and serial dependency encoding.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `runbook_id` | Packet field or derived from spec | Lowercase alphanumeric with hyphens matching `.runbooks/<id>/` directory name | Target runbook workspace identifier used in all generated artifact paths |
| `target_workspace` | Packet field or computed from runbook_id | Path like `.runbooks/<id>/` directory that must already exist | Root location where steps/ subdirectory exists |
| `steps_spec` | Packet field from specification analyst output or rendered content | JSON array of step objects, each containing: `step_id`, `operation`, `skill_target`, `input_artifacts`, `output_artifacts`, `files_in_scope`, `files_out_scope`, `expected_return_format` | Provides structured specification for creating individual step XML files |

## Bounded Worker Objective (Single Goal)

Create individual v3 XML step files under `.runbooks/<id>/steps/` from the provided `steps_spec` array, ensuring each step meets SUPER-atomic criteria before writing its XML file.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract runbook_id, target_workspace, and steps_spec
2. Validate that target_workspace exists and contains a `steps/` subdirectory (fail if not present)
3. For each step in steps_spec:
   - Verify SUPER-atomic criteria are met (single operation, one skill target, explicit I/O artifacts)
   - If broad task detected, return failure with defect marker (do not proceed with XML creation)
   - Render step XML using XSD schema under `skills/runbook/schemas/`:
     - Root element: `<step id="<step-id>">`
     - Include operation description, input/output artifacts, files_in_scope, files_out_scope, expected_return_format
     - Embed worker delegation metadata including skill_target
4. Write each step XML file to `.runbooks/<id>/steps/<step-id>.xml`
5. Generate output JSON according to Output Contract below
6. Validate completion by confirming all files exist on filesystem

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Specification content from upstream delegated skill output
  - Proposal/workspace referenced by steps_spec
  - Existing `.runbooks/<id>/steps/` directory structure
- **Write/create paths**: `.runbooks/<id>/steps/*.xml` files only
- **State mutations**: None — worker does not modify state.xml or other orchestration tracking files

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and arrays where appropriate | Must include: `status`, `workspace_path`, `steps_created` array with full paths, `verification_summary` object with counts, `blockers` array (empty if none), `defects` array (if any steps failed SUPER-atomic validation) | Verify all listed files exist at specified paths; confirm directories are present |

Example output structure:
```json
{
  "status": "completed",
  "workspace_path": ".runbooks/1781039100-build-runbook-orchestrated-delegated",
  "steps_created": [
    ".runbooks/1781039100-build-runbook-orchestrated-delegated/steps/01-author-runbook-intake-lane.xml"
  ],
  "verification_summary": {
    "total_steps_expected": 1,
    "total_steps_created": 1,
    "defects_found": 0
  },
  "blockers": [],
  "defects": []
}
```

## Validation / Evidence Requirements

- **Steps directory exists**: Directory `.runbooks/<id>/steps/` exists at target_workspace path
- **Step files created**: Each step XML file exists with valid v3 XML structure matching XSD schema
- **SUPER-atomic compliance**: Each step meets single-operation, one-skill-target criteria
- **No failure markers**: No exception traces or error state files created

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable|internal_error>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": [".runbooks/.../steps/partial-step.xml"],
  "blockers": ["description of blocking issue"]
}
```

Error types: `validation_error` (workspace doesn't exist, missing steps_spec, non-SUPER-atomic task), `resource_unavailable` (permission denied, disk full), `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace doesn't exist | Directory listing shows missing `.runbooks/<id>/` or `steps/` | Return failed with error_type=validation_error | Request workspace creator run first |
| Missing steps_spec fields | JSON parse shows absent keys | Return failed with error_type=validation_error | Request specification analyst regenerate complete specification |
| Non-SUPER-atomic task detected | Task describes multiple operations or lacks file-level scope | Return failed with defect marker in defects array | Split task into atomic units before proceeding |
| Permission denied writing files | System call returns EACCES on file creation | Attempt to create temp and move; if fails, return failure | Skip this task set temporarily; continue other work |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"runbook-step-writer"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification

## Validation Command

```bash
uv run --project scripts/python validate-skill-framework skills/runbook-step-writer/SKILL.md
# Grep verification checklist:
grep -E "^class:" skills/runbook-step-writer/SKILL.md  # should show: delegated
grep "runbook_id\|target_workspace\|steps_spec" skills/runbook-step-writer/SKILL.md  # all input contract items present
grep "status\|workspace_path\|steps_created\|verification_summary\|blockers\|defects" skills/runbook-step-writer/SKILL.md  # all output contract items present
```