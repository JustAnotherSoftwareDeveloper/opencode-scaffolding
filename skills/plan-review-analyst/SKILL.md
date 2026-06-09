---
name: plan-review-analyst
description: Use when a spawning orchestrator delegates validation of complete plan artifact sets and quality gate checks against the required 10-file + tasks/ taxonomy.
class: delegated
---

# Plan Review Analyst Delegation Handler

Validates completed plan workspaces for structural completeness, file presence, content requirements, and adherence to the required plan taxonomy before upstream skills proceed with execution.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `plan_workspace_path` | Delegation packet or state file path | Absolute or relative path like `.plans/<timestamp>-<slug>/` | Target plan workspace directory to validate against required taxonomy |
| `proposal_path` | Packet field from intake-lane output | Path string `.proposals/<timestamp>-<slug>/INDEX.md` | Source proposal reference for boundary verification and provenance checks |
| `expected_delegated_skills` | State file or packet array | Array of skill names like `["plan-intake-lane", "plan-specification-analyst", "plan-task-writer"]` | Named delegated backing skills that should have been coordinated by orchestrated plan skill |

## Bounded Worker Objective (Single Goal)

Verify the complete plan artifact set exists and passes all quality gates including required file taxonomy, content validation of key sections, tasks directory structure verification against proposal inputs, and boundary confirmation between proposal input, plan workspace, and executed delegated skills.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract `plan_workspace_path`, `proposal_path`, and `expected_delegated_skills`
2. Verify target workspace directory exists at the specified path with required 10-file + tasks/ taxonomy structure:
   - INDEX.md, metadata.md, source.md, execution-overview.md, constraints.md, file-impact.md, implementation-notes.md, validation.md, rollback-recovery.md, handoff.md (optional)
3. Validate each plan markdown file has YAML frontmatter parsing correctly and contains expected required sections per `plan` skill taxonomy
4. Confirm tasks/ directory exists with at least one numbered task file following kebab-case naming convention; verify each task file matches structure requirements (Purpose, Files In Scope, Actions, Expected Observations, Common Mistakes, Completion Criteria)
5. Cross-reference content against source proposal to validate boundary: plan summarizes not duplicates rationale
6. Verify all named delegated backing skills from `expected_delegated_skills` are listed in INDEX.md Accepted Decisions or referenced as coordinated execution
7. Generate output JSON according to Output Contract below

## State/File Boundaries (What Changes)

- **Read-only paths**: 
  - Plan workspace directory `.plans/<timestamp>-<slug>/` and all files within
  - Source proposal path for boundary verification
- **Write/create paths**: None — validation only, no mutations
- **State mutations**: None — worker does not modify any state.xml or orchestration tracking

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and arrays where appropriate | Must include: `status`, `workspace_path`, `files_checked` array, `quality_gates_passed` boolean, `recommendation` ("accept" or "revise"), `missing_files` array if any, `validation_errors` array if any | Verify all listed files exist; check for passed status when gates pass |

Example output structure:
```json
{
  "status": "completed",
  "workspace_path": ".plans/1786000000-plan-skill-orchestrated-delegated-rewrite",
  "files_checked": ["INDEX.md", "metadata.md", "..."],
  "quality_gates_passed": true,
  "recommendation": "accept",
  "delegated_skills_verified": ["plan-intake-lane", "plan-specification-analyst", "plan-task-writer", "plan-review-analyst"]
}
```

Failure output structure:
```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator should do next>",
  "missing_files": [".plans/.../tasks/*.md"],
  "partial_artifacts": []
}
```

## Validation / Evidence Requirements

- **Artifact exists**: Target workspace directory and all required files exist at specified paths
- **Frontmatter valid**: All YAML frontmatter parses without error in each plan markdown file
- **Required sections present**: Each required file contains its expected section headers matching plan taxonomy (not duplication of proposal rationale)
- **Tasks structure compliant**: tasks/ directory exists with numbered task files containing all mandatory subsections
- **Quality gates passed**: 10-file + tasks/ taxonomy fully satisfied; no missing or empty critical sections

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator should do next>",
  "partial_artifacts": [".plans/.../INDEX.md"]
}
```

Error types: `validation_error` (missing required files or sections), `resource_unavailable`, `internal_error`

## Quality Gates Checklist

| Gate | Description | Verification Method |
|------|-------------|---------------------|
| File taxonomy complete | All 10 required files present in plan workspace | Directory listing and file existence check |
| Tasks directory populated | At least one numbered task file exists with proper structure | glob pattern match on tasks/*.md, content section scan |
| Frontmatter valid | Every markdown file has parseable YAML frontmatter | YAML parsing attempt |
| No proposal duplication | Plan summarizes decisions without duplicating rationale | Content comparison against proposal_path |
| Delegated skills named | Orchestrated plan explicitly names all delegated backing skills | Keyword search in INDEX.md Accepted Decisions |

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace missing required files | Directory listing shows gaps | Return failed with error_type=validation_error, list missing paths | Request plan-task-writer create missing artifacts before proceeding |
| Tasks directory empty or malformed | File exists but sections incomplete | Return failed for specific task file path | Skip execution; do not proceed until tasks fixed |
| Proposal content duplication found | Grep shows large text matches in source proposal | Flag as validation_error with evidence paths | Request plan revise to summarize rather than duplicate |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"plan-review-analyst"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification