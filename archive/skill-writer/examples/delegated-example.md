---
name: delegation-packet-writer-delegated
description: Use when drafting bounded Worker Handoff Packets for specific orchestrators and tasks.
class: delegated
---

# Schema Validator Delegation Handler (Delegated Example)

Validates file contents against declared schemas or format constraints in isolation from parent orchestrator thread. Executes independent validation with explicit input/output contracts defined by spawning skill.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `target_file` | Packet field `/file` or argument | Path to JSON/YAML/XML file | The artifact needing validation |
| `schema_path` | Optional packet field | XSD path under `skills/` directory, omit for format-only checks | Schema constraint definition |

### Files in Scope (Read)
- `${target_file}` — File being validated
- `${schema_path}` — If provided, the schema file to validate against  

### Files Out of Scope (Must Not Touch)
- No write operations permitted

## Bounded Worker Objective (Single Goal)

Produce a structured validation result indicating pass/fail with specific errors if any constraints violated. Outcome must be verifiable without orchestrator intervention.

## Worker Execution Procedure

1. Receive file path and optional schema from packet/arguments  
2. If `schema_path` provided, validate `${target_file}` against XSD using uv script:
   ```bash
   uv run --project scripts/python validate-json "${target_file}" --schema "${schema_path}"
   # OR appropriate format validator based on extension
   ```
3. For JSON/YAML without schema, use built-in validators (no external schema required)
4. Generate output to stdout as structured result:

## State/File Boundaries (What Changes)

- **Read-only paths**: Target file and optional schema only
- **Write/create paths**: None - this worker is pure validation compute  
- **State mutations**: No persistent changes

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| stdout/JSON | JSON with `status`, `errors` array, `summary` keys | If passed: `{"status": "passed", "errors": [], ...}` ; if failed: list specific validation errors found | Check file exists was validated by inspecting result structure |

Example successful output:
```json
{
  "status": "passed",  
  "errors": [],
  "summary": "File /tmp/artifact.json validated successfully against schema atomic.xsd"
}
```

Example failure output:
```json  
{
  "status": "failed",
  "errors": [
    {"line": 42, "message": "Element 'xyz' is not allowed"},
    {"field": "/artifact/name", "issue": "required attribute missing"}
  ],
  "summary": "3 validation errors found in atomic.xsd constraints"  
}
```

## Validation / Evidence Requirements  

- **Success**: Exit code 0 from validator, empty `errors` array confirms all checks pass
- **Failure**: Non-zero exit code or populated `errors` field identifies exact violations  
- **Evidence markers**: N/A for pure compute validation; stderr captured if needed for debugging

## Failure Handling & Report Format

```json
{  
  "status": "failed",
  "error_type": "<validation_error|file_not_found>",
  "message": "...specific error encountered during validation...",
  "recovery_suggestion": "<what orchestrator should do with this result>" 
}
```

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| File not found at path | ls/path check in packet construction | Return failed, no retry (fix source file) | Repair packet with correct path before re-routing |
| Schema validation error | Parse validator stderr/stdout for line numbers | List specific errors discovered | Decide: fix artifact or adjust schema expectations |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens  
- `description` (string): Starts with "Use when" describing the trigger condition
- `class` (enum: delegated): Must be exactly this value for class identification