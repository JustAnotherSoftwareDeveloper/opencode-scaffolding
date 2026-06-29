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

Files related to verification practices.

- [verification-practices](./maintenance/verification-best-practices.md) — Verification checks by task type.

## Schema

Files related to the canonical output format.

- [json-schema.md](../schema/task-packet.schema.json) — JSON Schema defining the BreakdownTasksOutput object and TaskPacket structure.

## Scripts

Files related to breakdown pipeline scripts.

- [pipeline-overview.md](./scripts/pipeline-overview.md) — End-to-end pipeline flow for task decomposition.
- [generate-uuids.md](./scripts/generate-uuids.md) — UUID generation for task packet IDs.
- [validate-task-structure.md](./scripts/validate-task-structure.md) — Structural validation of task packet fields.
- [validate-dependencies.md](./scripts/validate-dependencies.md) — Dependency graph structural validation.
- [topological-sort.md](./scripts/topological-sort.md) — Topological sorting of task packets.
- [validate-and-format-output.md](./scripts/validate-and-format-output.md) — Output validation and formatting rules.
- [error-handling-testing.md](./scripts/error-handling-testing.md) — Error handling and testing patterns for the pipeline.
