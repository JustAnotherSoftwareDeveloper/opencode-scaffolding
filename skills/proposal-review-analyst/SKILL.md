---
name: proposal-review-analyst
description: Use when a spawning orchestrator delegates bounded review of proposal artifacts for completeness, quality gates, embedded critique against acceptance criteria, and verification that all 13 required files are present with proper content.
class: delegated
---

# Proposal Review Analyst Delegation Handler (Delegated)

Execute structured review of completed proposal workspaces to validate completeness, verify evidence quality, check scope boundaries, assess acceptance criteria alignment, and enforce the proposal-vs-plan boundary before orchestrator decision-making.

## Class Purpose

**Delegated backing role:** Delegated skills are worker-executed specialists spawned by orchestrated skills through delegation packets. They provide read-only review for orchestrated procedures - performing embedded critique that coordinators manage and coordinate.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `workspace_path` | Delegation packet or state context | Absolute path to `.proposals/<timestamp>-slug/` directory | Root directory of the proposal workspace to review |
| `embedded_critique_template` | Packet field or null | Path to embedded-quality-check.md template in skill templates | File containing critique criteria checklist for quality gates |

### Files in Scope (Read)
- All 13 required files per the proposal artifact contract:
  - `INDEX.md`, `metadata.md`, `goal.md`, `problem-opportunity.md`
  - `scope.md`, `recommended-approach.md`, `alternatives-considered.md`
  - `risks-and-unknowns.md`, `acceptance-criteria.md`, `decision.md`
  - `clarification-questions.md`, `artifact-and-state-impact.md`, `discovery-results.md`

### Files Out of Scope (Must Not Touch)
- No write operations to any files under the workspace path or configuration root.
- Do not modify proposal artifacts unless explicitly authorized by orchestrator via packet field.
- Return findings only via stdout in the Output Contract format below.

## Bounded Worker Objective (Single Goal)

Critique a complete proposal workspace against all 13 required file checkpoints, embedded critique criteria from `acceptance-criteria.md`, evidence quality standards, scope boundary verifications, and rejection of plan-content leakage - producing a structured review report with pass/fail determination and detailed severity ratings.

## Worker Execution Procedure

1. Parse input contract from received delegation packet:
   - Validate `workspace_path` exists and is readable as a directory.
   - If provided, read embedded critique template for specific checklist items.

2. File Presence Check (required 13 files):
   - Enumerate all expected markdown files per the artifact contract.
   - Report missing or unexpected extra files.

3. Content Analysis:
   - **Metadata/Status**: Review `metadata.md` and `decision.md` for proper status field values (`draft`/`accepted`/etc.).
   - **Evidence Quality**: Verify facts in `discovery-results.md` include source citations, confidence levels, and fit caveats where appropriate.
   - **Scope Boundaries**: Confirm `scope.md` explicitly states In/Out of scope items; check no unauthorized boundaries exist elsewhere.
   - **Acceptance Criteria**: Validate criteria in `acceptance-criteria.md` are independently testable with Given/When/Then format for behavioral items.
   - **Proposal-vs-Plan Boundary**: Flag any dependency graphs, task breakdowns, implementation steps, or runbook state behavior (these belong in plans/runbooks).

4. Severity Assessment: Mark each finding as `critical`, `high`, `medium`, or `low` based on impact to proposal validity.

5. Return structured response via stdout per Output Contract below.

## State/File Boundaries (What Changes)

- **Read-only paths**: All files under `.proposals/<timestamp>-slug/`; no modifications permitted except as explicitly authorized by orchestrator packet field.
- **Write/create paths**: None - temporary working files in `/tmp/` only for intermediate processing, cleaned up before exit.
- **State mutations**: No persistent changes to any state files or configuration.

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
 | stdout/markdown + JSON code fence block | Markdown with findings section plus appended ```json``` block containing `status`, `findings` array, and summary counts | Check for required severity field in each finding; verify blockers section present if any critical issues found | Parse output for markdown structure and closing ``` delimiter |

### Required Sections in Output
- **Findings**: Detailed list with severity, file reference, line when available, and rationale. Must include:
  - `file`: which of the 13 files has the issue
  - `line`: approximate line number or section name (e.g., "scope.md#In-Scope")
  - `severity`: one of `critical`, `high`, `medium`, `low`
  - `issue`: concise description of the problem or gap
  - `rationale`: why this matters for proposal acceptance

### Severity Legend
| Severity | Meaning | Example Issues |
|----------|---------|----------------|
| critical | Blocks proposal acceptance; must be fixed before proceeding | Missing required file, contradictory scope boundaries, embedded execution plan |
| high | Major quality problem that undermines confidence | Untestable acceptance criteria, missing evidence citations in discovery-results.md |
 | medium | Noticeable gap or improvement opportunity | Unclear language, minor ambiguity without recommended default |
| low | Minor polish issue; does not block acceptance | Typos, formatting inconsistencies |

### Pass/Fail Determination
- **FAIL**: Any findings with `severity: critical` OR `severity: high`. Proposal cannot be accepted in current state.
- **PASS**: All findings are `medium` or `low`, OR no findings at all. Proposal meets minimum quality gates for consideration.

Example output structure (for FAIL condition):
```markdown
## Review Results: Proposal Quality Check

### Findings Summary
| File | Severity | Issue | Rationale |
|------|----------|-------|-----------|
| scope.md | critical | In-scope boundary missing explicit end date criterion | Acceptance criteria cannot be verified without clear boundaries | 
| discovery-results.md | high | Fact row lacks source citation for claimed constraint | Evidence quality requirement violated; confidence assessment impossible |

**Total**: 1 critical, 1 high, 0 medium, 0 low findings. **Result: FAIL** - Proposal requires revision before acceptance.
```

Example output structure (for PASS condition):
```markdown
## Review Results: Proposal Quality Check

### Findings Summary  
| File | Severity | Issue | Rationale |
|------|----------|-------|-----------|
| risks-and-unknowns.md | medium | Missing mitigation for "stale source" risk in discovery-results.md row 7 | Opportunity to strengthen proposal robustness |

**Total**: 0 critical, 0 high, 1 medium, 0 low findings. **Result: PASS with notes** - Proposal meets quality criteria though minor improvements suggested.
```

## Validation / Evidence Requirements  

- **File completeness verified**: Reported status for all 13 required files explicitly checked against artifact contract.
- **Critique alignment**: Findings reference embedded critiqued criteria and evidence standards from proposal guidance.
- **Scope boundary check performed**: Explicitly called out or confirmed none found in `scope.md`.
- **Proposal-vs-plan leakage detected**: Any implementation artifacts, task breakdowns, runbook state references flagged as critical findings if present.

## Failure Handling & Report Format

When things go wrong during review, return this format:

```json
{  
  "status": "failed",
  "error_type": "<timeout|validation_error|resource_unavailable>",
  "message": "...specific error encountered during review...",
  "recovery_suggestion": "<what orchestrator should do next>",
  "partial_artifacts": []
}
```

Error types: `timeout`, `validation_error`, `resource_unavailable`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Workspace path unreadable (permission denied) | ls/read error in output before any analysis begins | Return failed with error_type=resource_unavailable immediately | Verify workspace_path is valid and worker has read access to the proposal directory |
| Expected files missing from artifact contract | Output shows fewer than 13 markdown files present | Report as critical finding if required file(s) missing; also note in summary | May need to create missing section files before acceptance |
| Critically unclear language prevents assessment | Multiple findings across files for same ambiguous concept | Consolidate into single medium/high severity issue on primary affected file with clear example lines | Request clarification or revision from proposal author |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens  
- `description` (string): Starts with "Use when" describing the trigger condition
- `class` (enum: delegated): Must be exactly this value for class identification