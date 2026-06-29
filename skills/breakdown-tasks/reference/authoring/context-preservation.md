# Context Preservation

Guidelines for populating the `context` field in each task packet.

Copy all relevant user context into each task's `context` field so that workers never need to re-read the original prompt.

The `context` field contains:

- The relevant subset of the user request for this specific task
- Background information and constraints
- References to prior decisions or artifacts

Context fields are 2000–8000 characters.
The `maxLength` of 8000 supports longer prompts and keeps each task self-contained.
Do not truncate context to fit shorter limits — workers require full context to execute without ambiguity.
