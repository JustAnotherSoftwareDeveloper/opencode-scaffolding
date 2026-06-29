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

## Summary Decision List

- Single bounded procedure, independent, self-validating → `operation`
- Receives delegation packet, returns structured output → `delegated`
- Single-pass reasoning-heavy, main agent executes → `inline`
- Coordinates phases, workers, sub-skills → `orchestrated`
- Passive data store for shared reference content → `documentation`
- Structural knowledge for planning activities → `planning`

## Task Involves Deterministic, Repeatable, or Token-Heavy Processing

For deterministic processing, use Python by default. If the core logic requires a Node-specific library (remark, mdast, babel, typescript) and no mature Python equivalent exists, route to a Node/Bun script.

Before selecting a class, evaluate whether the task qualifies for script delegation.
A task qualifies when ALL of these hold:

- Deterministic output for identical input.
- Well-defined I/O contract.
- Token cost exceeds script execution cost.
- Task appears in more than one skill or is used repeatedly.

When the task qualifies, the skill class remains the same (operation, delegated, etc.)
but must include a script invocation step in its Procedure or Execution Steps.
The script handles the deterministic portion; the LLM handles orchestration, validation,
and non-deterministic decisions around it.

## Choose Bash Over Python Based on Workflow Type

When a task qualifies for script delegation (criteria above), evaluate whether
bash or Python is the better implementation language. Choose **bash** when the
workflow matches one or more of these patterns:

### CLI Tool Wrapping

- The script's primary job is calling external CLI tools (shellcheck, shfmt, git, jq, curl, docker).
- Bash is the natural shell for command invocation, exit-code checking, and stdout/stderr capture.
- No non-trivial in-language data transformation is required.

### Pipeline Orchestration

- The script chains multiple commands where each step feeds into the next via pipes or temp files.
- Requires managing temporary files (mktemp, cleanup traps).
- Multi-step workflows where each step is itself a CLI command or script invocation.
- Example: a linting pipeline that runs shellcheck, then shfmt, then aggregates results.

### Environment Introspection

- The script checks tool availability (which/command -v), tool versions, OS type, or PATH resolution.
- Bash is the most direct way to query the execution environment.
- Example: a pre-flight skill that verifies jq, git, and docker are installed before proceeding.

Choose **Python** (or Node/Bun when a platform-specific library is required) for all other
deterministic scripting needs — string parsing, JSON/YAML transformation, file manipulation,
and any logic that benefits from structured error handling, type safety, or richer standard
library support.
