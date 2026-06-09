---
name: plan-workspace-creator
description: Use when a spawning orchestrator delegates creation of the .plans/<timestamp>-slug/ workspace scaffold from specification data including root files and tasks directory.
class: delegated
---

# Plan Workspace Creator Delegation Handler

Creates the `.plans/<timestamp>-<slug>/` workspace directory structure with required root files and tasks subdirectory—producing the execution-focused artifact scaffold ready for downstream task writing and runbook execution.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
 | `plan_id_slug` | Packet field or derived from spec | Lowercase alphanumeric with hyphens matching `.plans/<timestamp>-<slug>/` directory name | Target plan workspace identifier used in all generated artifact paths |
 | `target_workspace` | Packet field or computed from plan_id_slug | Path like `.plans/<timestamp>-<slug>/` directory that must not exist yet | Root location for creating plan workspace structure |
 | `proposal_path` | Packet field from intake output | Absolute or relative path to accepted proposal workspace | Reference for source.md and metadata.md linking back to accepted decision |
 | `spec_content` | Packet field from spec-analyst output or rendered content | JSON object with keys: goal_section, non_goals_section, source_proposal_reference, accepted_decisions_list, constraints_section, file_impact_analysis, validation_checkpoints (all required), or pre-rendered markdown strings for each of the 10 root files | Provides structured content for populating plan workspace files |

## Bounded Worker Objective (Single Goal)

Create the complete `.plans/<timestamp>-<slug>/` workspace directory structure with all 10 required root files populated from specification content, plus an empty `tasks/` subdirectory—without creating any task markdown files themselves.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract plan_id_slug, target_workspace, proposal_path, and spec_content
2. Validate that target_workspace does not already exist (fail if it does)
3. Create target_workspace directory and tasks/ subdirectory within it
4. Render each of the 10 root files from spec_content:
   - INDEX.md (TOC-only navigation, no frontmatter/body)
   - metadata.md (id, title, status, created_at, proposal reference)
   - source.md (link to accepted proposal with decision summary only)
   - execution-overview.md (high-level approach for what's executing today)
   - constraints.md (prerequisites, sequencing rules, hard boundaries)
   - file-impact.md (files/dirs that will be created/modified/deleted)
   - implementation-notes.md (or "TBD" if omitted)
   - validation.md (verification commands and checkpoints)
   - rollback-recovery.md (undo instructions for partial execution failure)
   - handoff.md (next steps and ownership transfer information)
5. Generate output JSON according to Output Contract below
6. Validate completion by confirming all files exist on filesystem

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Proposal workspace referenced by proposal_path
  - Specification content from upstream delegated skill output
- **Write/create paths**: `<target_workspace>/` directory and all 10 root files + `tasks/` subdirectory
- **State mutations**: None — worker does not modify state.xml or other orchestration tracking files

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and arrays where appropriate | Must include: `status`, `workspace_path`, `files_created` array with full paths, `tasks_directory_created` boolean, `verification_summary` object with counts, `blockers` array (empty if none) | Verify all listed files exist at specified paths; confirm tasks/ directory is present |

Example output structure:
```json
{
  "status": "completed",
  "workspace_path": ".plans/1786000000-plan-skill-orchestrated-delegated-rewrite",
  "files_created": [
    ".plans/1786000000-plan-skill-orchestrated-delegated-rewrite/INDEX.md",
    ".plans/1786000000-plan-skill-orchestrated-delegated-rewrite/metadata.md"
  ],
  "tasks_directory_created": true,
  "verification_summary": {
    "total_files_expected": 10,
    "total_files_created": 10,
    "tasks_dir_exists": true
  },
  "blockers": []
}
```

## Validation / Evidence Requirements

- **Workspace created**: Directory `.plans/<timestamp>-<slug>/` exists at target_workspace path
- **All 10 files present**: Each required root file exists with non-zero size
- **Tasks directory present**: `tasks/` subdirectory exists within workspace
- **No failure markers**: No exception traces or error state files created

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable|internal_error>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": [".plans/.../partial-file.md"],
  "blockers": ["description of blocking issue"]
}
```

Error types: `validation_error` (workspace already exists, missing spec_content), `resource_unavailable` (permission denied, disk full), `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace already exists | Directory listing shows existing `.plans/<slug>/` | Return failed with error_type=validation_error | Do not overwrite; request new plan_id_slug or user confirmation |
| Missing spec_content fields | JSON parse shows absent keys | Return failed with error_type=validation_error | Request spec-analyst regenerate complete specification |
 | Permission denied writing files | System call returns EACCES on file creation | Attempt to create temp and move; if fails, return failure | Skip this task set temporarily; continue other work |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"plan-workspace-creator"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification

## Validation Command

```bash
uv run --project scripts/python validate-skill-framework skills/plan-workspace-creator/SKILL.md
# Grep verification checklist:
grep -E "^class:" skills/plan-workspace-creator/SKILL.md  # should show: delegated
grep "plan_id_slug\|target_workspace\|proposal_path\|spec_content" skills/plan-workspace-creator/SKILL.md  # all input contract items present
grep "status\|workspace_path\|files_created\|tasks_directory_created\|verification_summary\|blockers" skills/plan-workspace-creator/SKILL.md  # all output contract items present
```