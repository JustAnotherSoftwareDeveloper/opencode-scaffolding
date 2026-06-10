---
name: runbook-validation-analyst
description: Use when v3 XML runbook workspace validation and readiness checks are needed before state initialization to ensure schema compliance, manifest presence, step granularity, dependency correctness, delegation map coverage, and no plan/proposal boundary violations.
class: delegated
---

# Runbook Validation Analyst Delegation Handler

Validates v3 XML runbook workspaces for completeness and readiness before `init-runbook-state` execution, ensuring all artifacts are properly formed and the workspace meets quality gates.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
 | `workspace_path` | Packet field or derived from runbook_id | Path like `.runbooks/<id>/` directory that must exist | Target runbook workspace location to validate |
| `checklist` | Packet field from specification analyst output | JSON array of required artifact paths to verify | Provides list of mandatory files that must be present |
| `validation_depth` | Optional packet field | `"basic"` (schema only) or `"full"` (schema + dependencies + boundaries) | Determines scope of validation to perform |

## Bounded Worker Objective (Single Goal)

Validate the specified v3 XML runbook workspace at `workspace_path`, checking schema compliance, manifest presence, step granularity, dependency correctness, delegation map coverage, state initialization readiness, and no plan/proposal boundary violations. Report results via JSON output contract without modifying any files.

## Worker Execution Procedure

1. Parse input contract from received delegation packet/state file to extract `workspace_path` and optional `checklist`/`validation_depth`
2. Verify `workspace_path` exists as a directory (fail if not present)
3. For each validation check based on `validation_depth`:
   - **Schema validation**: Run `uv run --project scripts/python validate-runbook <workspace_path>/main.xml`
   - **Manifest presence**: Check for required manifests (`evidence/index.xml`, `snippets/index.xml`, `reference/index.xml`)
   - **Step granularity**: Verify each step under `steps/` has valid v3 XML structure matching XSD schema
   - **Dependency correctness**: Validate `dependency_graph` in `state.xml` references existing steps
   - **Delegation map coverage**: Ensure all skill targets in steps have corresponding skill definitions
   - **State initialization readiness**: Confirm `state.xml` is well-formed and matches main.xml runbook ID
   - **Boundary violations**: Verify no read operations outside workspace or write operations to unauthorized paths
4. Compile results into output JSON according to Output Contract below
5. Return status via stdout

## State/File Boundaries (Read-Only Access)

- **Read-only paths**: 
  - All files under `.runbooks/<id>/` directory
  - Skill definitions under `skills/` for delegation map verification
  - Schema/XSD files under `skills/runbook/schemas/`
- **Write/create paths**: None — worker performs validation only, no modifications allowed
- **State mutations**: None — worker does not modify state.xml or other orchestration tracking files

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `stdout` | JSON object with string keys and arrays where appropriate | Must include: `status`, `workspace_path`, `quality_gates_passed` boolean, `validation_results` array with check names and pass/fail status, `blockers` array (empty if none), `recommendation` string ("proceed" or "repair") | Verify JSON parses; confirm all listed checks were performed |

Example output structure:
```json
{
  "status": "completed",
  "workspace_path": ".runbooks/1781039100-build-runbook-orchestrated-delegated",
  "quality_gates_passed": true,
  "validation_results": [
    {"check": "schema_validation", "passed": true, "message": "main.xml validates against runbook.xsd"},
    {"check": "manifest_presence", "passed": true, "message": "All 3 required manifests present"},
    {"check": "step_granularity", "passed": true, "message": "All 5 steps have valid v3 XML structure"},
    {"check": "dependency_correctness", "passed": true, "message": "All dependency references resolve"},
    {"check": "delegation_coverage", "passed": true, "message": "All skill targets have SKILL.md files"},
    {"check": "state_initialization", "passed": true, "message": "state.xml ready for init-runbook-state"}
  ],
  "blockers": [],
  "recommendation": "proceed"
}
```

## Validation / Evidence Requirements

- **Schema validation passed**: `validate-runbook` command exits 0 for main.xml
- **Required manifests present**: `evidence/index.xml`, `snippets/index.xml`, `reference/index.xml` exist
- **Step files valid**: Each step XML file exists with valid v3 XML structure matching XSD schema
- **Dependencies resolvable**: All step references in dependency_graph exist as step files
- **Delegation coverage**: All skill_target values in steps have corresponding `skills/<name>/SKILL.md` files
- **State readiness**: `state.xml` is well-formed XML with matching runbook ID to main.xml
- **No boundary violations**: No evidence of unauthorized file access or modification attempts

## Failure Handling & Report Format

When things go wrong, return this format via stdout:

```json
{
  "status": "failed",
  "error_type": "<validation_error|resource_unavailable|internal_error>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": [".runbooks/.../partial-validation.json"],
  "blockers": ["description of blocking issue"]
}
```

Error types: `validation_error` (workspace doesn't exist, missing required artifacts), `resource_unavailable` (permission denied, disk full), `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace doesn't exist | Directory listing shows missing `.runbooks/<id>/` | Return failed with error_type=validation_error | Request workspace creator run first |
| Missing required manifest | File not found for evidence/snippets/reference index | Add blocker and continue other checks; report missing files | Create missing manifests before proceeding |
 | Schema validation fails | validate-runbook output shows XSD errors | Record failure in validation_results | Repair main.xml against XSD schema |
| Dependency reference broken | Step ref in dependency_graph points to non-existent step | Add blocker for that dependency | Fix dependency_graph to reference existing steps |
| Skill target missing | skills/<target>/SKILL.md does not exist | Add blocker for delegation coverage | Create missing skill or update step to use existing skill |
| State/runbook ID mismatch | state.xml runbook_id differs from main.xml id | Add blocker for state initialization | Regenerate state.xml with correct runbook ID |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens - `"runbook-validation-analyst"`
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification

## Validation Command

```bash
uv run --project scripts/python validate-skill-framework skills/runbook-validation-analyst/SKILL.md
# Grep verification checklist:
grep -E "^class:" skills/runbook-validation-analyst/SKILL.md  # should show: delegated
grep "Orchestrator Handoff Input\|State/File Boundaries\|Output Contract" skills/runbook-validation-analyst/SKILL.md  # mandatory sections present
grep "quality_gates_passed\|validation_results\|blockers\|recommendation" skills/runbook-validation-analyst/SKILL.md  # all output contract items present
```