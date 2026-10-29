# Context Preservation

Use this procedure to populate the `context` field in each task packet. The loaded
`task-contract` documentation skill's **Task identity** (`task-identity.md`) and
**Traceability and metadata** (`traceability-and-metadata.md`) references define the
shared requirements for task context and source/proposal links. This page covers only
the decomposition workflow's context-preservation procedure.

Workers cannot reread the original user prompt or access shared state between packets.
Copy the relevant user context into each task's `context` field so each worker has the
request facts needed for its task without relying on that prompt or shared state.
Workers must not reread the original prompt. This self-contained handoff reduces
stale-context risk and supports parallel dispatch.

The `context` field contains:

- The relevant subset of the user request for this specific task
- Background information and constraints
- References to prior decisions or artifacts, and source/proposal references required
  by the shared traceability contract

Context fields must contain 200–8,000 characters. Keep context concise and
task-specific; meet the minimum with relevant information rather than padding it with
repeated or irrelevant text.
Do not truncate context.
If context is too long, prioritize information by relevance and revise it to fit.
Truncation can introduce ambiguity or remove information the worker needs for its task.
