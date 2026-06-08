---
name: proposal-local-lane
description: Use when a spawning orchestrator delegates bounded local discovery of harness files, conventions, and constraints for isolated exploration with explicit input/output contracts.
class: delegated
---

# Proposal Local Lane Delegation Handler (Delegated)

Execute localized discovery within the current opencode configuration environment to identify available skills, runbooks, plans, and operational conventions without external dependencies.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `workspace_root` | Runbook state context | Absolute path string | Root directory for discovery scope |
| `scope_filter` | Optional packet field or null | Alphanumeric pattern, default "skills/" | Directory patterns to enumerate |

### Files in Scope (Read)
- `.runbooks/` — Enumerate existing runbooks and their steps/structure.
- `skills/` — Inventory all available skills with their classes.
- `.plans/` — Review plan structures for template/reference.
- `.proposals/` — Check proposal workspace format requirements.
- Any local configuration files under `~/.config/opencode/`.

### Files Out of Scope (Must Not Touch)
- No write operations to any existing files.
- Do not create, modify, or delete artifacts outside temporary exploration scope.
- Do not execute implementation—only discover and report.

## Bounded Worker Objective (Single Goal)

Produce an inventory of current harness files, skills, runbooks, conventions, and constraints in a structured discovery format that the orchestrator can use to inform subsequent delegation decisions. Outcome must be verifiable without external input.

## Worker Execution Procedure

1. Parse scope_filter from packet/context; default to `skills/` if not specified.
2. Enumerate all files under `.runbooks/`, `skills/`, and relevant local directories matching the filter pattern.
3. For each discovered skill, extract: name, description (first sentence), class (if present).
4. Identify any orchestrated class skills that coordinate delegated backing roles.
5. Generate output as structured markdown table with path -> key attributes mapping.

## State/File Boundaries (What Changes)

- **Read-only paths**: `.runbooks/`, `skills/`, `.plans/`, `.proposals/` directories under workspace root; no modifications permitted.
- **Write/create paths**: None—output returned via stdout only.
- **State mutations**: No persistent changes to any state files or configuration.

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| stdout/markdown table | Markdown table with columns: path, name, description, class, notes | Must include all discovered skills and runbooks; summary section at end | Check for required column presence in output |

Example successful output structure (markdown):

```markdown
## Discovery Results: Local Lane Exploration

### Skills Inventory
| File Path | Name | Description | Class | Notes |
|-----------|------|-------------|-------|-------|
| skills/proposal/SKILL.md | proposal | Create bounded proposals... | planning | Primary orchestrator skill |

### Runbook Structure Reference  
| Path | ID | Active Step | Status |
|------|-----| ------------|--------|
| .runbooks/1780951246-rewrite-proposal-orchestrated-delegated/main.xml | 178095... | 01-author-proposal-local-lane-skill | approved |

**Total discovered**: N skills, M runbooks. **Orchestration pattern**: <summary>
```

## Validation / Evidence Requirements  

- **Artifact exists**: Output was generated on stdout with valid markdown structure.
- **Content validation**: All enumerated files matched scope_filter; no external systems accessed.
- **Evidence markers**: Check for "Total discovered" summary line confirming completeness.
- **Failure markers absent**: No error state or exception traces in output.

## Failure Handling & Report Format

```json
{  
  "status": "failed",
  "error_type": "<timeout|validation_error|resource_unavailable>",
  "message": "...specific error encountered during exploration...",
  "recovery_suggestion": "<what orchestrator should do with this result>" ,
  "partial_artifacts": []
}
```

Error types: `timeout`, `validation_error`, `resource_unavailable`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Scope filter too restrictive | Output shows zero discoveries but files exist | Retry with broader scope_filter or null | Expand discovery boundaries before re-routing |
| Permission denied reading path | ls/read error in output | Return failed, no retry (fix source file) | Verify permissions on workspace root |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens  
- `description` (string): Starts with "Use when" describing the trigger condition
- `class` (enum: delegated): Must be exactly this value for class identification