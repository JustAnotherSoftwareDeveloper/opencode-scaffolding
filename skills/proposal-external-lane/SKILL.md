---
name: proposal-external-lane
description: Use when a spawning orchestrator delegates bounded external research on frameworks, standards, or comparable solutions with cited facts, fit caveats, and confidence ratings that inform proposal decisions.
class: delegated
---

# Proposal External Lane Delegation Handler (Delegated)

Execute bounded external research via one-topic-at-a-time investigation of specific URLs or topic keywords to produce evidence-backed findings for orchestrator decision-making without making unsourced claims.

## Class Purpose

**Delegated backing role:** Delegated skills are worker-executed specialists spawned by orchestrated skills through delegation packets. They provide read-only discovery for orchestrated procedures - performing external reference exploration that coordinators manage and coordinate.

## When to Use This Template (Trigger Condition)

- A spawning orchestrator needs bounded external research on specific frameworks, standards, or comparable solutions
- The worker objective is isolated with clear input/output contracts and source citation requirements
- Search scope is defined by specified URLs or topic keywords from the orchestrator
- No unsourced claims are permitted - all findings must include verifiable sources

## Orchestrator Handoff Input (What Worker Needs)

| Item | Source | Format/Constraints | Purpose |
|------|--------|-------------------|---------|
| `target_urls` | Delegation packet or state context | JSON array of absolute URLs, HTTPS only | Specific web resources to investigate for factual claims |
| `topic_keywords` | Packet field or null | JSON array of case-insensitive strings | Keywords defining research topic when URLs not specified |
| `required_facts` | Optional packet field | JSON object with fact_id keys and brief descriptions as values | Specific facts the orchestrator needs confirmed or discovered |

### Files in Scope (Read)

- Any URL provided via `target_urls` input - web pages, API docs, specification files, etc.
- Public documentation sites referenced by topic keywords

### Files Out of Scope (Must Not Touch)

- No local file modifications under workspace root
- Do not create or edit any `.runbooks/`, `.plans/`, `.proposals/` artifacts
- Return findings only via stdout marked as external-lane-results format

## Bounded Worker Objective (Single Goal)

Produce an evidence-backed research report with cited references, fit caveats about application context, and confidence ratings that enables orchestrator decision-making for proposal evaluation.

## Worker Execution Procedure

1. Parse input contract from received delegation packet:
   - If `target_urls` is provided, fetch each URL in order of precedence
   - If `topic_keywords` provided without URLs, perform bounded topical search (single query expansion max)
   
2. For each source/resource, extract:
   - Document title and publication date if available
   - Relevant passages that address required facts or topic keywords
   - Any stated limitations, assumptions, or version constraints

3. Generate output with the following structure per Output Contract below

4. Validate completion against Evidence Requirements ensuring all claims have sources

5. Return structured response via stdout as markdown + JSON summary block

## State/File Boundaries (What Changes)

- **Read-only paths**: Any URL provided in input; no local file system writes permitted
- **Write/create paths**: None - temporary working files in `/tmp/` only for intermediate processing, cleaned up before exit  
- **State mutations**: No persistent changes to any state files or configuration

## Output Contract (What Orchestrator Receives)

| Channel | Format | Content Requirements | Verification |
|---------|--------|---------------------|--------------|
| stdout/markdown + JSON code fence block | Markdown with headings plus appended ```json``` block containing `target_urls`, `topic_keywords` (null if not used), `findings` array, and warnings field | Check for required citation format: `[Source: URL]` or `[Source: document title]` inline; verify confidence ratings present | Parse output for markdown structure and closing ``` delimiter |

### Evidence Format Requirements

Each finding must include:
- **Claim**: The factual assertion being made
- **Confidence**: One of `high`, `medium`, `low` based on source quality/reproducibility  
- **Source citation**: Inline reference like `[Source: https://example.com/doc]` or `[Source: RFC 9239, Section 4.2]`

Example output structure:
```markdown
## External Research Results

### Finding Summary
| Claim | Confidence | Source Citation | Fit Caveat |
|-------|------------|-----------------|------------|
| OpenTelemetry supports OTLP over HTTP/gRPC | high | [Source: https://opentelemetry.io/docs/proto/] | Vendor-neutral implementation; may need adaptation for proprietary exporters |

**Research Summary**: 1 URL investigated, 2 facts verified with confidence ratings.

```json
{"target_urls": ["https://opentelemetry.io/docs/proto/"], "topic_keywords": null, "findings": [{"claim": "OpenTelemetry supports OTLP over HTTP/gRPC", "confidence": "high"}], "warnings": []}
```

## Validation / Evidence Requirements  

- **Evidence markers present**: All claims include `[Source: ...]` citations inline
- **Content validation**: No unsourced statements or unattributed passages
- **Confidence ratings provided**: Each finding has explicit `high|medium|low` rating
- **Staleness caveat included**: If applicable, note when source last updated/reviewed

## Failure Handling & Report Format

When things go wrong, return this format:

```json
{  
  "status": "failed",
  "error_type": "<timeout|validation_error|resource_unavailable>",
  "message": "...specific error encountered during external research...",
  "recovery_suggestion": "<what orchestrator should do next>",
  "partial_artifacts": []
}
```

Error types: `timeout`, `validation_error`, `resource_unavailable`, `internal_error`

## Gotchas & Recovery Patterns

| Failure Mode | Evidence to Check | Worker Action | Orchestrator Signal |
|--------------|-------------------|---------------|---------------------|
| URL not accessible (404, timeout) | HTTP status code or connection error before fetch | Return failed with error_type=resource_unavailable for that specific URL; skip if other URLs valid | Consider alternative sources for same topic |
| Source lacks required facts | Content analysis of fetched document | Note missing fact in findings with confidence=low and caveat explaining source gap | Request additional targets from user |
| Topic search yields low-quality results | Search result quality assessment | Return empty findings array with warning about ambiguous keywords | Clarify topic_keywords or provide specific URLs |

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens  
- `description` (string): Starts with "Use when" describing the trigger condition
- `class` (enum: delegated): Must be exactly this value for class identification