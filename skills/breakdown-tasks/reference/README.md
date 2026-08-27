# Reference Documentation Map

Use this index to locate detailed guidance for the decomposition workflow.

## Authoring

- [Core rules](authoring/core-rules.md) define operation-owned inventory and draft
  procedures and point to the shared task contract.
- [Task granularity](authoring/task-granularity.md) applies the shared boundary
  review to the operation's concern inventory.
- [Atomicity anti-patterns](authoring/anti-patterns.md) list operation review signals.
- [Atomicity examples](authoring/atomicity-examples.md) provide decomposition examples
  that consume the shared contract.
- [Field reference](authoring/field-reference-table.md) mirrors the schemas and links
  shared field meaning to its owner.
- [Context preservation](authoring/context-preservation.md) describes worker context.
- [Implementation steps](implementation-steps-format.md) describes step documents.

## Orchestration And Assignment

- [Task validation](orchestration/task-validation.md) defines packet review checks.
- [Skill assignment](skill-assignment.md) defines direct skill selection.

## Scripts And Maintenance

- [Pipeline overview](scripts/pipeline-overview.md) summarizes the pipeline.
- [Structure validation](scripts/validate-task-structure.md) documents validation.
- [Error handling](scripts/error-handling-testing.md) documents failure behavior.
- [Verification practices](maintenance/verification-best-practices.md) lists checks.

## Schemas

- [Task packet schema](../schema/task-packet.schema.json) defines published packets.
- [Task input schema](../schema/task-input.schema.json) defines draft packets.

## Shared Semantics

- [Task-contract reference](../../task-contract/reference/README.md) owns task
  identity, atomicity, alignment, dependencies, coupling, traceability, and
  authoring metadata. It is passive and non-transitive.
