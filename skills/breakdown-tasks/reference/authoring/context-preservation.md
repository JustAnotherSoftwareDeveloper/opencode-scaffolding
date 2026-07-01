# Context Preservation

Guidelines for populating the `context` field in each task packet.

Copy relevant user context into each task's `context` field.
Workers must not re-read the original prompt.

The `context` field contains:

- The relevant subset of the user request for this specific task
- Background information and constraints
- References to prior decisions or artifacts

Context fields are 2000–8000 characters.
The 8000-character `maxLength` keeps tasks self-contained.
Do not truncate context.
Workers require full context to execute without ambiguity.
