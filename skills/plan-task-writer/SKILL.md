---
name: plan-task-writer
description: Use when a spawning orchestrator delegates creation of numbered senior-to-intern task markdown files under the tasks/ directory from a structured plan specification.
class: delegated
---

# Plan Task Writer Delegation Handler

Transforms validated plan specifications into properly formatted, numbered task markdown files in the `tasks/` directory—named artifacts that provide clear execution instructions for workers following the plan.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `plan_spec` | Packet field from spec-analyst output or state file path | JSON object with keys: goal_section, constraints_section, file_impact_analysis, validation_checkpoints (all required), plan_id_slug | Provides structured content for task creation and workspace location |
| `target_workspace` | Packet field or derived from plan_spec.plan_id_slug | Path like `.plans/<timestamp>-<slug>/` directory that must exist with tasks/ subdirectory | Target location for creating numbered task files |
| `task_naming_constraints` | Packet field or default rules | Array of strings, e.g., ["kebab-case only", "no spaces in filename"] | Ensures consistent file naming per plan taxonomy |

## Bounded Worker Objective (Single Goal)

Create a complete set of properly formatted task markdown files under the target workspace `tasks/` directory—producing numbered senior-to-intern instruction files with required sections, correct frontmatter, and appropriate worker capability recommendations where applicable.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract plan_spec JSON and target_workspace path
2. Validate that target_workspace has a `tasks/` subdirectory (create if missing per orchestrator instruction)
3. Transform plan_spec content into numbered task files (e.g., `01-implementation.md`, `02-validation.md`) following the template structure:
   - YAML frontmatter with id, title, status, timestamps
   - Purpose statement for the step
   - Files In Scope section with exact paths
   - Actions section with concrete steps and commands
   - Expected Observations section describing success conditions
   - Common Mistakes & How to Avoid Them table
   - Completion Criteria (pass/fail checklists)
4. For each task, include `Recommended Worker Capability` note where applicable (e.g., "small", "medium", "large" worker; or specific skill like `documentation-medium`)
5. Generate output JSON according to Output Contract below
6. Validate completion by confirming all required sections present in created files

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Plan specification JSON from input contract
  - Existing plan workspace structure (`.plans/<timestamp>-<slug>/` and subdirectories if any)
- **Write/create paths**: `<target_workspace>/tasks/*.md` — one file per numbered task
- **State mutations**: None — worker does not modify state.xml or other orchestration tracking files

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and arrays where appropriate | Must include: `status`, `workspace_path`, `tasks_created` array, `task_files` array with full paths | Verify all listed files exist on filesystem; validate frontmatter format |

Example output structure:
```json
{
  "status": "completed",
  "workspace_path": ".plans/1786000000-plan-skill-orchestrated-delegated-rewrite",
  "tasks_created": ["implementation", "validation"],
  "task_files": [".plans/1786000000-plan-skill-orchestrated-delegated-rewrite/tasks/01-implementation.md"],
  "summary": "Created 2 task files with proper frontmatter and required sections"
}
```

## Validation / Evidence Requirements

- **Artifact exists**: Each listed file in `task_files` array exists at the specified path
- **Frontmatter valid**: All YAML frontmatter parses correctly with required fields (id, title, status, created_at)
- **Required sections present**: Every task file contains Purpose, Files In Scope, Actions, Expected Observations, Common Mistakes & How to Avoid Them, Completion Criteria
- **Naming compliant**: File names follow plan taxonomy conventions (numbered prefix, kebab-case, no spaces)
- **No failure markers**: No exception traces or error state files created

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": [".plans/.../tasks/partial-file.md"]
}
```

Error types: `validation_error` (missing required output sections), `resource_unavailable`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace missing tasks/ dir | Directory listing of target_workspace | Create directory and proceed, or return failed if unwritable | Retry with corrected path; do not fail the overall plan |
| Missing required output sections in plan_spec | JSON parse shows absent keys | Return failed with error_type=validation_error | Request spec-analyst regenerate complete specification |
| File permission denied writing tasks/ | System call returns EACCES on file creation | Attempt to create temp and move; if fails, return failure | Skip this task set temporarily; continue other work |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"plan-task-writer"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification