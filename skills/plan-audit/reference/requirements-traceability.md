# Requirements Traceability

The repository's selected proposal and decision-resolution analysis are the source
for this operation. The supplied `design/` paths were not present in this checkout;
the corresponding copied proposal sections below are the materially relied-on
sources.

- **Normalized inputs and baseline fallback:** [selected direction, Plan-audit
  contract](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/06-selected-direction.md#plan-audit-contract)
  and [immutable-input policy](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#selected-immutable-input-contract).
- **Authoritative/copy provenance and source drift:** [baseline rule](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#baseline-rule).
- **Fresh collector and winning identity:** [collector rule](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#collector-rule).
- **Historical inventory limit:** [collector rule](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#collector-rule) records persisted inventories as comparison evidence only.
- **External report boundary and report sections:** [report boundary and shape](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#report-boundary-and-shape).
- **Check families and hard-failure boundaries:** [selected direction, three checks](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/06-selected-direction.md#plan-audit-contract) and [exact thresholds](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#exact-dispositions-and-thresholds).
- **Atomicity semantics:** [task-contract source](../../task-contract/SKILL.md) and [task atomicity policy](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#exact-dispositions-and-thresholds).
- **Overall precedence and no approval:** [rollup](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#exact-dispositions-and-thresholds).
- **Correction owner and no self-repair:** [remediation and residual input](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-plan-audit-policy.md#remediation-and-residual-input) and [lifecycle fix authority](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/analysis/decision-resolution-planning-lifecycle.md#fix-authority-and-bounds).
- **No mutation, reassignment, approval, readiness change, republication, or delegation:** [read-only audit boundary](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/06-selected-direction.md#plan-audit-contract).
- **Acceptance evidence:** [plan-audit acceptance criteria](../../../.proposals/1787577875497-planning-workflow-and-breakdown-upgrade/09-acceptance-criteria.md#plan-audit-has-a-normalized-read-only-input-contract).

This traceability index is documentation only. It does not authorize edits to the
proposal, source trees, plan, skills, collector inventory, or report consumers.
