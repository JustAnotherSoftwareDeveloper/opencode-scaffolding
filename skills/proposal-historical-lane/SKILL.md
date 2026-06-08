---
name: proposal-historical-lane
description: Use when a spawning orchestrator delegates bounded read-only inspection of prior proposals, plans, runbooks, and lessons to inform current decisions with explicit input/output contracts.
class: delegated
---

# Proposal Historical Lane Delegation Handler (Delegated)

Execute bounded historical exploration within the opencode configuration environment to identify relevant past artifacts, patterns, and precedents without external dependencies or write operations.

## Class Purpose

**Delegated backing role:** Delegated skills are worker-executed specialists spawned by orchestrated skills through delegation packets. They provide read-only discovery for orchestrated procedures - performing historical artifact inspection that coordinators manage and coordinate.

## When to Use This Template (Trigger Condition)

- A spawning orchestrator needs bounded read-only exploration of prior proposals, plans, runbooks, or lessons
- The worker objective is isolated with clear input/output contracts
- Search scope is defined by specific patterns (e.g., topics, artifact types, date ranges)
- No write operations are required - only discovery and reporting

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `search_terms` | Delegation packet or state context | JSON array of strings, case-insensitive patterns | Keywords to match against proposal/plan/runbook content |
| `artifact_types` | Packet field or null | Array from: proposal, plan, runbook, lesson (default: all) | Restrict search scope by artifact category |
| `date_range` | Optional packet field | Object with `start` and `end` ISO dates, optional | Filter artifacts by creation/modification timeframe |

### Files in Scope (Read-Only)
- `.proposals/` — Enumerate prior proposals for relevant decisions/conflicts
- `.plans/` — Review plan structures for established patterns/conventions  
- `.runbooks/` — Inspect runbook step histories and execution outcomes
- `.lessons/` — Examine past session lessons for recurring issues/gotchas

### Files Out of Scope (Must Not Touch)
- No write operations to any files under workspace root
- Do not execute or modify proposal/plan/runbook artifacts
- Return findings only via stdout/state file as specified in Output Contract

## Bounded Worker Objective (Single Goal)

Produce an evidence-backed inventory of historical artifacts matching the search criteria, with confidence levels and caveats about fit, that enables orchestrator decision-making without external research.

## Worker Execution Procedure

1. Parse input contract from received delegation packet:
   - If `search_terms` is null/empty, enumerate all known artifacts for overview
   - Apply artifact type filters if specified; default to scanning all types
   - Filter by date range if provided (check creation/modification metadata)
   
2. For each discovered matching file, extract relevant attributes:
   - Path, name/title, creation date, key topics mentioned in first section
   - Relevant excerpts or decision points that match search criteria

3. Generate evidence table mapping findings to artifacts with confidence/caveat columns

4. Validate completion against Evidence Requirements below

5. Return structured response via stdout as markdown table per Output Contract

## State/File Boundaries (What Changes)

- **Read-only paths**: `.proposals/`, `.plans/`, `.runbooks/`, `.lessons/` directories under workspace root; no modifications permitted
- **Write/create paths**: None - temporary working files in `/tmp/` only for intermediate processing, cleaned up before exit
- **State mutations**: No persistent changes to any state files or configuration

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| stdout/markdown table + JSON summary block | Markdown table plus appended code fence block with `search_terms`, `artifacts_found` array, and optional warning fields | Check for required columns presence; verify paths are valid relative to workspace root | Parse output for markdown table structure and closing ``` delimiter |

Example successful output structure:
```markdown
## Historical Exploration Results

### Matching Artifacts Discovered
| Path | Type | Title/Topic | Date | Confidence Match | Caveats/Fit Notes |
|------|------|-------------|------|------------------|-------------------|
|.proposals/1780575222-normalize-proposal-files/INDEX.md|proposal|Proposal Plan Refactoring|2026-04-30|High|Schema changes align with current rewrite context|

**Search Summary**: 1 artifact found across proposal, plan types. Dates: 2026-04-30 to 2026-05-12.
```

```json
{"search_terms": ["proposal", "schema"], "artifacts_found": [".proposals/1780575222-normalize-proposal-files/INDEX.md"]}
```

## Validation / Evidence Requirements  

- **Artifact exists**: Output was generated on stdout with valid markdown table structure (check for pipe-delimited rows and header separator)
- **Content validation**: All discovered files matched provided search criteria; paths verified as readable within workspace root
- **Evidence markers**: Check for "**Search Summary**" line confirming completeness; JSON block present at end of output
- **Failure markers absent**: No error state or exception traces in output

## Failure Handling & Report Format

When things go wrong, return this format:

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
| Scope too restrictive (zero results but files exist) | Compare search_terms against known artifact topics in workspace | Return found=false with message; suggest expanding terms or checking date range | Expand discovery boundaries, consider broader pattern match |
| Permission denied reading path | ls/read error in output before scan begins | Return failed immediately - no retry on permissions errors | Verify read access to workspace root directory |
| No historical artifacts exist yet | Output shows zero discoveries with empty search_terms | Return found=false gracefully; indicate "no prior history" is itself a finding | May need proposal-local-lane for current state discovery instead |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens  
- `description` (string): Starts with "Use when" describing the trigger condition
- `class` (enum: delegated): Must be exactly this value for class identification