# Reference Documentation Map

How the pieces fit together — the breakdown pipeline flows through six domains, from authoring to execution:

1. **Authoring** (`reference/authoring/`) — Rules and heuristics for producing atomic, well-structured task packets. Start here if a task fails validation or feels too large. Includes:
   - `core-rules.md` — Five atomicity rules (why tasks must be atomic)
   - `anti-patterns.md` — Common mistakes and how to diagnose them
   - `task-granularity.md` — Heuristics for splitting work at the right boundaries
   - `field-reference-table.md` — All fields in the TaskPacket and root-level object
   - `context-preservation.md` — Guidelines for self-contained worker packets

2. **Orchestration** (`reference/orchestration/`) — Validation of decomposition output correctness. Use after completing a decomposition to check structure.
   - `task-validation.md` — Validation checks for decomposition output correctness

3. **State Management** (`reference/state-initialization.md`) — How the shared state file is initialized and managed across pipeline stages. Consult when debugging state-related failures or filename collisions.
   - `state-initialization.md` — State-file derivation rules, collision behavior, and retention policy

4. **Skill Assignment** (`reference/skill-assignment.md`) — The deterministic scoring system that assigns skills to task drafts. Consult when troubleshooting skill selection or scoring behavior.
   - `skill-assignment.md` — FlashRank-based procedure for assigning skills to task drafts

5. **Scripts** (`reference/scripts/`) — Automation layer documentation for the breakdown pipeline. Consult when running, debugging, or extending the pipeline scripts:
   - `pipeline-overview.md` — Full pipeline walkthrough and design philosophy
   - `validate-and-format-output.md` — Final validation gate reference
   - `validate-task-structure.md` — Task structure validation rules
   - `error-handling-testing.md` — Exit code conventions and testing patterns

6. **Maintenance** (`reference/maintenance/`) — Quality assurance and verification best practices. Use before dispatch to confirm output integrity:
   - `verification-best-practices.md` — Verification checks by task type

7. **Schema** (`../schema/`) — Canonical output format definitions that all pipeline stages conform to.
   - `task-packet.schema.json` — JSON Schema defining the BreakdownTasksOutput object and TaskPacket structure
   - `task-input.schema.json` — JSON Schema defining the TaskDraft input format (no `skills` property — enforced by schema)