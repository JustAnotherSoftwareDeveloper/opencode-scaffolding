# Requirements Traceability

The active operation contract and references below define current behavior. The
linked decision-resolution analyses are copied historical provenance only; they
are not current proposal sections or runtime inputs.

- **Normalized inputs, immutable baseline, and source drift:** [input contract](input-contract.md) and the historical [plan-audit policy](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#selected-immutable-input-contract).
- **Fresh collector, winning identity, and historical inventory limit:** [operation contract](../SKILL.md) and the historical [collector rule](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#collector-rule).
- **External report boundary, sections, overall precedence, and no approval:** [report contract](report-contract.md).
- **Check families, hard-failure boundaries, and exact thresholds:** [check rules](checks.md) and the historical [threshold rationale](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#exact-dispositions-and-thresholds).
- **Atomicity semantics:** [task-contract source](../../task-contract/SKILL.md) and [task-contract references](../../task-contract/reference/README.md).
- **Correction owner and no self-repair:** [operation guardrails](../SKILL.md) and the historical [remediation rationale](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#remediation-and-residual-input).
- **No mutation, reassignment, approval, readiness change, republication, or delegation:** [input contract](input-contract.md) and [report contract](report-contract.md).
- **Acceptance evidence:** the executable parser and its regression tests enforce the active contracts without relying on retired numbered proposal files.

This traceability index is documentation only. It does not authorize edits to the
proposal, source trees, plan, skills, collector inventory, or report consumers.
