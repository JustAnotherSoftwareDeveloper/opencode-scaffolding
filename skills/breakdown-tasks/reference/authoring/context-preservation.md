# Context Preservation

Operation guidance for populating the `context` field in each task packet. The loaded
`task-contract` documentation skill's named **Task identity** and named
**Traceability and metadata** reference (`traceability-and-metadata.md`) define
requirements for context and source/proposal links; this file only describes the
decomposition workflow's context-preservation procedure.

*Why this field exists: Workers are stateless. They cannot re-read the original
user prompt or access shared state between packets. The `context` field makes each
packet self-contained, so every worker has the information it needs without external
lookup. This design prevents stale-context bugs and enables parallel dispatch.*

Copy relevant user context into each task's `context` field, preserving the shared
contract's source and proposal references.
Workers must not re-read the original prompt.

The `context` field contains:

- The relevant subset of the user request for this specific task
- Background information and constraints
- References to prior decisions or artifacts, as required by the shared traceability
  contract

Context fields are 200–8000 characters.
Use concise, task-specific information to meet the minimum.
Do not pad context with repeated or irrelevant text.
Do not truncate context.
*Why: Truncation introduces ambiguity. If the context is too long, prioritize by
relevance rather than truncating. The worker needs complete information for its
specific task.*
