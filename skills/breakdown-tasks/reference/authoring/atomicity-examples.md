# Atomicity Examples

Use these contrasts with the shared
[atomicity rule](../../../task-contract/reference/atomicity-and-alignment.md).

## Split

- **Assess authentication design and dependency risk:** two findings can be accepted
  or retried separately. Create two tasks; synthesize only when requested.
- **Analyze migration risk, then propose a bridge:** the assessment is a predecessor
  result consumed by the proposal. Create two dependent tasks.
- **Research session evidence, then create an audit skill:** separate the research
  inventory, audit-contract decision, skill creation, and validation.
- **Revise the API reference and deprecation policy:** the documentation and policy
  changes have separate acceptance decisions.
- **Research packet construction and write a proposal:** separate source discovery,
  behavioral analysis, recommendation, proposal authoring, and proposal validation.
- **Implement a change and run tests:** separate implementation and verification when
  the tests can execute against a fixed implementation result.

## Narrow Keep-Together Exceptions

- **Read an already-identified parser reference while implementing one specified
  option:** the read itself produces no discovery, finding, or decision.
- **Change a source schema and regenerate its client:**
  keep the state change together only when separation would leave an invalid
  repository state; put independently executable verification in another task.

## Wrong Reasons To Keep Together

Do not merge results because they share a file, report, topic, release, skill,
dependency, or final deliverable. Do not merge because the intermediate handoff is
small or was not explicitly requested. If uncertain, split.
