# Breakdown Tasks — Reference Documents

Reference documents organized by domain module.
Each file covers one topic for progressive disclosure from SKILL.md.

## Authoring

Files related to task decomposition rules, anti-patterns, granularity guidelines, and context preservation.

- [core-rules.md](./authoring/core-rules.md) — Five atomicity rules for decomposing work into delegation packets.
- [anti-patterns.md](./authoring/anti-patterns.md) — Work-boundary and skill-assignment mistakes to avoid.
- [task-granularity.md](./authoring/task-granularity.md) — Heuristics for splitting work into atomic units.
- [field-reference-table.md](./authoring/field-reference-table.md) — All fields in the TaskPacket and root-level object.
- [context-preservation.md](./authoring/context-preservation.md) — Guidelines for populating the context field in each task packet.

## Orchestration

Files related to dependency mapping, task graphs, and validation of the task graph structure.

- [dependency-patterns.md](./orchestration/dependency-patterns.md) — Common dependency topologies and per-task dependency mapping.
- [task-validation.md](./orchestration/task-validation.md) — Validation checks for decomposition output correctness.

## Maintenance

Files related to verification best practices.

- [verification-best-practices.md](./maintenance/verification-best-practices.md) — Recommended verification checks by task type.

## Schema

Files related to the canonical output format.

- [json-schema.md](../schema/task-packet.schema.json) — JSON Schema defining the BreakdownTasksOutput object and TaskPacket structure.
