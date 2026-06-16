---
name: <<skill-name>>
description: "Use when <<trigger condition>>."
class: delegated
---

# <<Skill Name>> — Delegated Worker

One-line summary of what this worker accomplishes.

*(Skill directory name must be lowercase with hyphens, matching `name` field. The description captures the orchestrator's trigger perspective.)*

## Input Contract (from Delegation Packet)

- **`<<field>>`** — Source: *Packet section* — Purpose: *What it provides*

## Worker Objective

Single verifiable outcome this worker must produce.

## Execution Steps

1. Parse input contract from delegation packet.
2. Perform bounded work.
3. Produce output per Output Contract below.
4. Self-validate against Evidence Requirements.
5. Return structured response.

## File / State Boundaries

- **Read**: `<<paths>>`
- **Write**: `<<paths>>`
- **State mutations**: `<<state fields>>`

## Output Contract

- **Channel**: *stdout / file* — **Format**: *JSON / text* — **Content**: *Required keys, paths, summary*

## Evidence Requirements

- Artifact exists at expected path.
- Content contains required elements.
- No failure markers.

## Failure Format

```json
{
  "status": "failed",
  "error_type": "timeout|validation_error|resource_unavailable|internal_error",
  "message": "...",
  "recovery_suggestion": "..."
}
```