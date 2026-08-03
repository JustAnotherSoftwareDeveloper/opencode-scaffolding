---
name: <skill-name>
description: Use when a spawning skill delegates a bounded worker objective for isolated execution with explicit input/output contracts.
class: delegated
---

# <<Skill Name>> Skill Template (Delegated)

Replace all `<placeholder>` values before using. Match `name` to the directory name exactly.

## Class Purpose

**Delegated role:** Delegated skills are worker-executed specialists spawned through delegation packets. They perform the bounded work assigned by the spawning skill.

## When to Use This Template

- You need to delegate one focused sub-task that can run independently
  - Worker has clear inputs it needs from orchestrator
  - Worker produces bounded outputs for orchestrator handback
  - Task is small enough for single-execution validation
  - State changes are isolated and reversible

## Template Structure

```markdown
---
name: <delegated-skill-name>                          # Must match directory name, lowercase with hyphens
description: Use when ...                   # Trigger from orchestrator's perspective (see class-selection.md)
class: delegated                            # Required class declaration
---

# <<Worker Task Name>> Delegation Handler

Brief description of what the spawned worker accomplishes.

## Orchestrator Handoff Input (What Worker Needs)

List all inputs provided by the spawning orchestrator skill via delegation packet or file state:

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `<input-name>` | Packet field or `.state.xml` path | e.g., JSON object with `topic`, `scope` keys | Used for ... |

## Bounded Worker Objective (Single Goal)

State the exact outcome this worker must achieve: One clear, verifiable result.

## Worker Execution Procedure

Steps the spawned subagent performs:

1. Parse input contract from received delegation packet/state file
2. Perform main work (...be specific about what "work" means here...)
3. Generate output according to Output Contract below
4. Validate completion against Evidence Requirements
5. Return structured response via designated channel (stdout, state file, or direct handback)

## State/File Boundaries (What Changes)

Specify worker's allowed scope - nothing external:

- **Read-only paths**: `<list files/directories the worker may read>`
- **Write/create paths**: `<where new artifacts are created, typically under /tmp/ or skill-specific dir>`
- **State mutations**: `<which .state.xml fields this modifies, if any>`

## Output Contract (What Orchestrator Receives)

Define exact format and content of successful completion:

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| `<stdout/state file/path>` | JSON/text/etc. | Must include `<required keys/fields>`, path to artifacts, summary | Check for required fields presence |

Example output structure:
```json
{
  "status": "completed",
  "deliverables": ["/path/to/artifact.md"],
  "summary": "...",
  "evidence_files": ["/tmp/evidence.txt"]
}
```

## Validation / Evidence Requirements

List what constitutes provable success (must be self-contained):

- **Artifact exists**: Check file/path from output contract was created
- **Content validation**: Verify artifact contains expected elements (`<specific patterns>` or JSON schema)
- **Evidence generated**: Confirm `<required evidence>` in designated location
- **Failure markers absent**: No error state files, no exception traces

## Failure Handling & Report Format

When things go wrong, return this format:

```json
{
  "status": "failed",
  "error_type": "<timeout|validation_error|resource_unavailable>",
  "message": "...human-readable description...",
  "recovery_suggestion": "<what orchestrator might do next>",
  "partial_artifacts": ["/tmp/partial-output.md"]
}
```

Error types: `timeout`, `validation_error`, `resource_unavailable`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Input constraint violation | Check source field in input contract | Return failed with error_type=validation_error | Skip dependent tasks, log input issue |
| Resource unavailable | File not found at expected path after timeout | Retry N times, then fail | Consider alternative worker or abort |
```

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: delegated): Must be exactly this value for class identification

> **Warning**: This is a template file. Copy it to create actual skills; do not load `templates/delegated-skill-template.md` as an active skill.
