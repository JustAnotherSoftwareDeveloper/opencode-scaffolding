---
name: task-contract
description: "Use when referencing shared semantics for authoring one atomic task and its traceable result."
selection:
  role: reference
  tags:
    actions: [reference, explain]
    inputs: [task request, task metadata]
    outputs: [shared task-contract context]
    topics: [task identity, atomicity, verification alignment, dependencies, coupling, traceability]
    constraints: [passive, documentation-only, non-transitive]
  use_when:
    - the request needs shared semantics for a task boundary, result, verification, dependency, coupling, or traceability
  not_for:
    - decomposing a request into tasks
    - creating a plan workspace
    - executing a task packet
    - validating task JSON structure
  supports: [breakdown-tasks, plan-writer]
class: documentation
---

# Task Contract — Documentation Store

This skill is a passive data store for shared task identity, atomicity, alignment,
dependency, coupling, traceability, and authoring metadata semantics.

It does not auto-read any files when loaded.

It does not own decomposition, plan creation, packet execution, structural schema
validation, skill selection, assignment, delegation, writes, or completion evidence.

## Documentation Files

- [Ownership ledger](reference/ownership-ledger.md)
  — separates shared semantics from workflow procedures and structural interfaces.
- [Task identity](reference/task-identity.md)
  — defines identity and task-field boundaries.
- [Atomicity and alignment](reference/atomicity-and-alignment.md)
  — defines the split test and the one-purpose, one-result boundary.
- [Dependencies and coupling](reference/dependencies-and-coupling.md) — defines
  dependency meaning and coupling evidence.
- [Traceability and metadata](reference/traceability-and-metadata.md)
  — defines source, proposal, and authoring metadata traceability.
- [Class boundary](reference/class-boundary.md)
  — preserves the documentation class and non-transitive loading boundary.

The references are separate disclosures of one shared contract.

## Contents

- `reference/` — passive task-contract rules, ownership boundaries, and traceability
  guidance.

## Docs

See the [reference index](reference/README.md) for the documentation map.
