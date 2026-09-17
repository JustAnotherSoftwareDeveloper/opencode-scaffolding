# Atomicity Examples

Use these contrasts with the shared
[atomicity rule](../../../task-contract/reference/atomicity-and-alignment.md).

## Split

- **Assess authentication design and dependency risk:** two findings can be accepted
  or retried separately. Create two tasks; synthesize only when requested.
- **Analyze migration risk, then propose a bridge:** the assessment is a predecessor
  result consumed by the proposal. Create two dependent tasks.
- **Research session evidence, then create an audit skill:** separate the research
  when its findings determine the skill's scope or audit contract.
- **Revise the API reference and deprecation policy:** the documentation and policy
  changes have separate acceptance decisions.

## Keep Together

- **Produce one login-flow threat model using dependency attack paths:** investigating
  attack paths is internal evidence for the one threat-model result when it produces
  no separate finding needed downstream.
- **Change cache invalidation and run regression tests:** the tests verify the code
  result and do not produce a separate requested report.
- **Change a source schema and regenerate its client:**
  keep one task when both files form one reproducible result and separation would
  leave an invalid repository state.

## Wrong Reasons To Keep Together

Do not merge results because they share a file, report, topic, release, skill,
dependency, or final deliverable. Do not split one result merely because it requires
several actions or files.
