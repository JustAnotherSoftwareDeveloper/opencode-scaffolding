---
name: proposal-synthesis-analyst
description: Use when a spawning orchestrator delegates bounded synthesis of lane outputs into decision-ready tradeoffs, risks, contradictions, acceptance criteria candidates, and evidence ledger entries.
class: delegated
---

# Proposal Synthesis Analyst Delegation Handler (Delegated)

Execute bounded synthesis by merging completed exploration lane outputs into proposal-ready artifacts that support orchestrator decision-making with explicit fact/inference/assumption distinctions.

## Class Purpose

**Delegated backing role:** Delegated skills are worker-executed specialists spawned by orchestrated skills through delegation packets. They provide read-only synthesis for orchestrated procedures - performing cross-lane analysis that coordinators manage and coordinate.

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `lane_outputs` | State file or packet field | Object with keys: local, historical, external; values are paths to lane SKILL.md or output artifacts | Paths to all completed exploration lane results for synthesis |
| `proposal_sections` | Packet context or null | Array of section names from proposal artifact (e.g., "Tradeoffs", "Risks") | Specific sections the orchestrator wants populated with analysis |

### Files in Scope (Read)
- All lane output files specified in `lane_outputs.local`, `.historical`, `.external` paths above.
- Existing skill artifacts under `skills/proposal-local-lane/SKILL.md`, `skills/proposal-historical-lane/SKILL.md`, `skills/proposal-external-lane/SKILL.md`.

### Files Out of Scope (Must Not Touch)
- No write operations to any `.runbooks/`, `.plans/`, `.proposals/` artifacts.
- Do not create or modify proposal files unless explicitly authorized by orchestrator via packet field.
- Return synthesis results only via stdout in the Output Contract format below.

## Bounded Worker Objective (Single Goal)

Produce a structured evidence-backed analysis that distinguishes facts from inferences and assumptions, identifies contradictions across lanes, summarizes tradeoffs/risks, generates candidate acceptance criteria, and compiles an evidence ledger - all formatted for immediate use by the orchestrator in proposal construction.

## Worker Execution Procedure

1. Parse input contract from delegation packet/state:
   - Validate `lane_outputs` contains valid paths to readable files.
   - If `proposal_sections` is provided, focus synthesis on those areas; otherwise cover full scope.

2. For each lane output file:
   - Extract documented facts (verifiable claims with sources).
   - Identify inferences (reasoned conclusions from evidence).
   - Note explicit assumptions (stated or implied prerequisites).

3. Cross-lane analysis:
   - Compare findings across lanes for contradictions or inconsistencies.
   - Synthesize common themes into tradeoff summaries.
   - Aggregate risks from all lanes with confidence levels.
   - Generate candidate acceptance criteria based on discovered constraints.

4. Build evidence ledger: map each fact/inference/assumption to its source path and lane origin.

5. Validate completeness against Evidence Requirements below.

6. Return structured response via stdout in external-lane-results format per Output Contract.

## State/File Boundaries (What Changes)

- **Read-only paths**: All file paths under `.runbooks/`, `skills/proposal-*-lane/SKILL.md`, and any referenced output artifacts; no modifications permitted.
- **Write/create paths**: None - temporary working files in `/tmp/` only for intermediate processing, cleaned up before exit.
- **State mutations**: No persistent changes to any state files or configuration.

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| stdout/markdown + JSON code fence block | Markdown with headings plus appended ```json``` block containing `status`, `deliverables` array, and all required sections below | Check for fact/inference/assumption distinctions; verify evidence ledger has sources; confidence ratings on risks present | Parse output for markdown structure and closing ``` delimiter |

### Required Sections in Output
- **Facts** (verifiable claims with source citations)
- **Inferences** (reasoned conclusions from facts)
- **Assumptions** (stated or implied prerequisites)
- **Contradictions Found** (differences between lane findings)
- **Tradeoff Summaries** (comparison of alternatives/approaches)
- **Risk Aggregated** (risks with confidence ratings: high/medium/low)
- **Acceptance Criteria Candidates** (proposed criteria from constraints discovered)
- **Evidence Ledger** (mapping of claims to source paths/lanes)

Example output structure:
```markdown
## Synthesis Results

### Facts Identified
| Fact | Source | Lane | Evidence Marker |
|------|--------|------|-----------------|
| ... | ... | ... | [Source: path] |

### Inferences Drawn
| Inference | Supporting Facts | Caveat |
|-----------|------------------|--------|
| ... | ... | ... |

**Synthesis Summary**: N facts, M inferences, L assumptions across P contradictions found. Q candidate acceptance criteria generated.

```json
{"status": "completed", "deliverables": [], "facts_count": 0, "inferences_count": 0, "contradictions": []}
```
```

## Validation / Evidence Requirements  

- **Fact/inference/assumption distinguished**: Output explicitly labels each as Fact/Inference/Assumption.
- **Evidence ledger complete**: Maps all claims to source paths and lane names.
- **Contradiction check performed**: Report identifies or confirms none found.
- **Confidence ratings on risks**: Each risk has explicit high/medium/low rating.
- **Acceptance criteria candidates present**: At least one suggestion based on discovered constraints.

## Failure Handling & Report Format

When things go wrong, return this format:

```json
{  
  "status": "failed",
  "error_type": "<timeout|validation_error|resource_unavailable>",
  "message": "...specific error encountered during synthesis...",
  "recovery_suggestion": "<what orchestrator should do next>",
  "partial_artifacts": []
}
```

Error types: `timeout`, `validation_error`, `resource_unavailable`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| Lane output path unreadable | ls/read error in output before analysis begins | Return failed with error_type=resource_unavailable | Verify paths are valid and worker has read access |
| Contradiction unresolvable | Conflicting claims lack common source for reconciliation | Note contradiction with confidence=low and caveat explaining conflict scope | Consider additional research or explicit decision point |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens  
- `description` (string): Starts with "Use when" describing the trigger condition
- `class` (enum: delegated): Must be exactly this value for class identification