# Ownership Ledger

This ledger separates the shared task contract from the procedures and structural
interfaces that consume it.

## Shared Semantics

`task-contract` owns the meaning of these cross-workflow invariants:

- task identity and the distinction between a task and its position in an ordered
  list;
- atomicity and the independent-concern split test;
- one-purpose, one-result, and result-to-verification alignment;
- directed dependency meaning and predecessor-artifact traceability;
- evidence required before multiple concerns are treated as coupled;
- source and proposal traceability; and
- authoring metadata that records boundary and verification reasoning.

## Workflow Procedures

The decomposition workflow retains ownership of request inventory, boundary drafting,
skill collection, skill assignment, packet publication, and workflow validation.

The plan workflow retains ownership of source copying, plan-workspace lifecycle,
task authoring from a plan, publication, and plan-workspace validation.

Those procedures may consume this reference, but they remain outside this owner.

## Structural Interfaces

The existing task input and task packet schemas remain structural runtime interfaces
with their current owner.

This documentation does not duplicate, relocate, extend, or validate those schemas.

Schema requiredness, types, patterns, and additional-property behavior remain schema
concerns rather than semantic rules in this store.

## Evidence Map

- Identity is supported by the task field descriptions and the stable-identity field
  in the task schemas.
- Atomicity is supported by the core authoring rules, task-granularity guidance,
  and the named atomicity anti-patterns.
- Result and verification alignment is supported by the core authoring rules, field
  reference, and layered task-validation guidance.
- Dependency meaning is supported by the core authoring rules, ordered-work examples,
  and dependency validation guidance.
- Coupling evidence is supported by the core authoring rules,
  unsupported-coupling anti-patterns, and one-result validation guidance.
- Source and proposal traceability is supported by context-preservation guidance
  and source-oriented task-authoring guidance.
- Authoring metadata is supported by the metadata fields in both task schemas and
  the field reference.

The evidence map identifies semantic sources without importing their workflow
procedures into this documentation store.
