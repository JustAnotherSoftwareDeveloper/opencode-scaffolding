# Context Preservation

Guidelines for populating the `context` field in each task packet.

*Why this field exists: Workers are stateless — they cannot re-read the original user prompt or access shared state between packets. The `context` field makes each packet self-contained, so every worker has all the information it needs without external lookup. This design prevents stale-context bugs and enables parallel dispatch.*

Copy relevant user context into each task's `context` field.
Workers must not re-read the original prompt.

The `context` field contains:

- The relevant subset of the user request for this specific task
- Background information and constraints
- References to prior decisions or artifacts

Context fields are 2000–8000 characters.
*The 2000-character minimum ensures the worker has enough context to execute without ambiguity — too little context forces the worker to make assumptions. The 8000-character maximumLength keeps tasks self-contained and respects worker token limits.*
Do not truncate context.
*Why: Truncation introduces ambiguity. If the context is too long, prioritize by relevance rather than truncating — the worker needs complete information for its specific task.*
