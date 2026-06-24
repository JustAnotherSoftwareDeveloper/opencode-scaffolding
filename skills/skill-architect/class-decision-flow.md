# Class Decision Flow

Use these questions when uncertain.
Start with `operation` as the default.
Only choose another class when a specific condition clearly applies.

## Default — Single Bounded, Independent, Self-Validating, No Sub-Delegation

Choose `operation` when the skill:
- Performs one bounded procedure.
- Is independent — no dependency on external orchestration.
- Is self-validating — verifies its own output.
- Does not sub-delegate to other skills or workers.
- Example: a token-counter skill that reads a file, counts tokens, and returns the count.

## Receives a Delegation Packet

Choose `delegated` when the skill:
- Receives a well-formed delegation packet from a delegator.
- Performs a bounded subtask within a pipeline or orchestration.
- Returns structured output to the delegator.
- Example: a document-section worker that receives a packet of document metadata, processes one section, and returns the result.

## Single-Pass Reasoning-Heavy, Main Agent Executes Directly

Choose `inline` when the skill:
- Requires heavy reasoning in a single pass.
- Is executed directly by the main agent, not via delegation.
- May make optional direct tool calls.
- Has no worker or sub-skill orchestration as its own workflow.
- Example: a complex data-mapping skill that transforms one schema to another in one pass.

## Coordinates Phases, Workers, or Sub-Skills

Choose `orchestrated` when the skill:
- Coordinates sub-skills, workers, phases, or quality gates.
- Owns sub-delegation and result collation.
- Uses the 7-section canonical layout.
- Example: a document-generation skill that dispatches section writers, then collates results.

## Passive Data Store for Shared Docs/Schemas/Templates

Choose `documentation` when the skill:
- Is a passive data store consumed by other skills.
- Contains reference content (docs, schemas, templates) for domain-shared use.
- Defines no execution steps and produces no side effects.
- Example: an API-reference skill that documents endpoint schemas consumed by code-generation skills.

## Planning Reference for Structural Knowledge

Choose `planning` when the skill:
- Documents structural knowledge about the codebase.
- Is loaded during planning or architecting activities.
- Must not produce side effects, modify files, invoke tools, or define execution steps.
- Example: a service-architecture skill that documents module boundaries, data flow, and deployment topology.

## Summary Decision Table

| Condition | Class |
|---|---|
| Single bounded procedure, independent, self-validating | `operation` |
| Receives delegation packet, returns structured output | `delegated` |
| Single-pass reasoning-heavy, main agent executes | `inline` |
| Coordinates phases, workers, sub-skills | `orchestrated` |
| Passive data store for shared reference content | `documentation` |
| Structural knowledge for planning activities | `planning` |