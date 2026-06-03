# Runbook Handoff

## Post-Approval Process

After plan approval, load the `runbook` skill to convert this plan workspace into a v2 XML runbook. The plan itself does not execute.

## Required Inputs

- Approved plan entry point: `.plans/<id>/INDEX.md`
- Accepted proposal path: `<relative path>`
- Supporting files to include in context packages:
  - `context.md`
  - `skill-map.md`
  - `validation.md`

## Suggested Step Boundaries

- <Step boundary, objective, and files in scope.>
- <Step boundary, objective, and files in scope.>

## Dependency And Serial Sequencing Notes

- <Dependency that must run first.>
- Execute all phases serially; each phase's result must be reconciled before starting the next.

## Delegation Notes

- Load `delegation` during runbook execution to choose worker sizes for each atomic unit.
- Include relevant proposal sections, plan supporting files, files in scope, files out of scope, and expected return format in each handoff packet.

## Important Reminder

**Plans do not execute.** Execution must be handled through the `runbook` skill with proper state initialization and embedded review.
