# Reference Documentation Map

Use this index to locate detailed guidance for the decomposition workflow.

## Authoring

- [Core rules](authoring/core-rules.md) define operation-owned decomposition and
  drafting and point to the shared task contract.
- [Decomposition method](authoring/decomposition-method.md) defines the break-down,
  split-again, connect, draft, and review procedure.
- [Packet drafting checklist](authoring/packet-drafting-checklist.md) maps stabilized
  boundaries into existing task packet content.
- [Task-set review](authoring/task-set-review.md) defines the final coverage and
  rework gate before assignment.
- [Worked decomposition examples](authoring/decomposition-examples.md) demonstrate
  aggressive recursive splitting, dependency handoffs, narrow retained coupling, and stopping.
- [Task granularity](authoring/task-granularity.md)
  describes recursive splitting and the stopping rule.
- [Atomicity anti-patterns](authoring/anti-patterns.md) list operation review signals.
- [Atomicity examples](authoring/atomicity-examples.md) provide short contrastive
  examples that consume the shared contract.
- [Field reference](authoring/field-reference-table.md) mirrors the schemas and
  links shared field meaning to its owner.
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

Load the `task-contract` documentation skill and consume its named references for
task identity, atomicity, alignment, dependencies, coupling, traceability, and
authoring metadata. The documentation load is passive and non-transitive.
