---
name: runbook-workspace-creator
description: Use when a spawning orchestrator delegates creation of the .runbooks/<id>/ v3 XML scaffold including main.xml, manifests, steps/ directories as appropriate, without execution state mutation.
class: delegated
---

# Runbook Workspace Creator Delegation Handler

Creates the `.runbooks/<id>/` v3 XML/XSD-first scaffold directory structure with required root files (main.xml, manifests), steps/ subdirectory, and optional evidence/snippets/reference manifest indexes—producing the execution-focused artifact scaffold ready for downstream step writing and validation.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
 | `runbook_id` | Packet field or derived from spec | Lowercase alphanumeric with hyphens matching `.runbooks/<id>/` directory name | Target runbook workspace identifier used in all generated artifact paths |
 | `target_workspace` | Packet field or computed from runbook_id | Path like `.runbooks/<id>/` directory that must not exist yet | Root location for creating runbook workspace structure |
 | `spec_content` | Packet field from specification analyst output or rendered content | JSON object with keys: goal_section, non_goals_section, source_proposal_reference, accepted_decisions_list, constraints_section, file_impact_analysis, validation_checkpoints (all required), or pre-rendered markdown strings for each section | Provides structured content for populating runbook workspace files |

## Bounded Worker Objective (Single Goal)

Create the complete `.runbooks/<id>/` v3 XML/XSD-first workspace directory structure with main.xml, manifests (evidence/index.xml, snippets/index.xml, reference/index.xml), steps/ subdirectory—without creating any step XML files themselves or initializing state.xml.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract runbook_id, target_workspace, and spec_content
2. Validate that target_workspace does not already exist (fail if it does)
3. Create target_workspace directory and subdirectories: steps/, evidence/, snippets/, reference/
4. Render main.xml using XSD schema under skills/runbook/schemas/:
   - Root element: `<runbook artifact_type="runbook" format_version="3" id="<runbook-id>">`
   - Include step references for each defined step
5. Generate default manifest index files:
   - evidence/index.xml
   - snippets/index.xml
   - reference/index.xml
6. Generate output JSON according to Output Contract below
7. Validate completion by confirming all files exist on filesystem

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Specification content from upstream delegated skill output
  - Proposal workspace referenced by spec_content
- **Write/create paths**: `<target_workspace>/` directory and all required files + subdirectories
- **State mutations**: None — worker does not modify state.xml or other orchestration tracking files; state initialization is handled separately by init-runbook-state when authorized

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and arrays where appropriate | Must include: `status`, `workspace_path`, `files_created` array with full paths, `steps_directory_created` boolean, `manifests_created` array, `verification_summary` object with counts, `blockers` array (empty if none) | Verify all listed files exist at specified paths; confirm directories are present |

Example output structure:
```json
{
  "status": "completed",
  "workspace_path": ".runbooks/1781039100-build-runbook-orchestrated-delegated",
  "files_created": [
    ".runbooks/1781039100-build-runbook-orchestrated-delegated/main.xml",
    ".runbooks/1781039100-build-runbook-orchestrated-delegated/evidence/index.xml"
  ],
  "steps_directory_created": true,
  "manifests_created": ["evidence/index.xml", "snippets/index.xml", "reference/index.xml"],
  "verification_summary": {
    "total_files_expected": 5,
    "total_files_created": 5,
    "steps_dir_exists": true,
    "manifests_exist": true
  },
  "blockers": []
}
```

## Validation / Evidence Requirements

- **Workspace created**: Directory `.runbooks/<id>/` exists at target_workspace path
- **main.xml present**: File exists with valid v3 XML structure matching XSD schema
- **Steps directory present**: `steps/` subdirectory exists within workspace
- **Manifests present**: All three manifest index files exist with valid XML structure
- **No failure markers**: No exception traces or error state files created

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable|internal_error>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": [".runbooks/.../partial-file.xml"],
  "blockers": ["description of blocking issue"]
}
```

Error types: `validation_error` (workspace already exists, missing spec_content), `resource_unavailable` (permission denied, disk full), `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace already exists | Directory listing shows existing `.runbooks/<id>/` | Return failed with error_type=validation_error | Do not overwrite; request new runbook_id or user confirmation |
| Missing spec_content fields | JSON parse shows absent keys | Return failed with error_type=validation_error | Request specification analyst regenerate complete specification |
| Permission denied writing files | System call returns EACCES on file creation | Attempt to create temp and move; if fails, return failure | Skip this task set temporarily; continue other work |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"runbook-workspace-creator"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification

## Validation Command

```bash
uv run --project scripts/python validate-skill-framework skills/runbook-workspace-creator/SKILL.md
# Grep verification checklist:
grep -E "^class:" skills/runbook-workspace-creator/SKILL.md  # should show: delegated
grep "runbook_id\|target_workspace\|spec_content" skills/runbook-workspace-creator/SKILL.md  # all input contract items present
grep "status\|workspace_path\|files_created\|steps_directory_created\|manifests_created\|verification_summary\|blockers" skills/runbook-workspace-creator/SKILL.md  # all output contract items present
```