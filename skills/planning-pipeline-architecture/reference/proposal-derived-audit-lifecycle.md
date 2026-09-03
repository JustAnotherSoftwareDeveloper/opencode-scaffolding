# Proposal-Derived Audit Lifecycle

`proposal-derived-audit-lifecycle` — `proposal`, `plan-writer`, `plan-audit` —
describes the forward audit and remediation states for a proposal-derived plan.

**Use when:** A recorded proposal decision is the baseline for a plan whose audit,
findings, bounded fix, and re-audit handoffs must remain explicit.

## Passive Boundary

This reference names states, artifacts, owners, and transitions only. It is passive
and non-transitive: it grants no executable steps, tools, writes, delegation, skill
loading, approval, or completion authority.

`plan-audit` remains an independent, read-only report owner. `plan-writer` remains
the only owner of a bounded plan correction and revised plan. A finding does not
authorize a repair, and an audit pass does not authorize approval.

## Forward States And Transitions

- **Proposal recorded** — `proposal` owns the decision record, supporting evidence,
  source labels, and authoritative proposal baseline. The proposal workspace and
  its canonical decision sections are the artifact. A stable baseline does not
  authorize planning.
- **Proposal authorization confirmed** — the decision authority owns the transition
  to planning. It requires either a recorded accepted lifecycle state or
  `decision-ready` plus explicit planning authorization from the recorded
  `decision-owner`. Publication, validation, `review-ready`, baseline stability,
  recency, and invocation do not cause this transition.
- **Plan authored** — `plan-writer` owns the proposal-derived plan snapshot. The
  plan workspace, `tasks.json`, `tasks.md`, copied sources, and proposal traceability
  are the artifacts. Publication transitions this proposal-derived path to **Audit
  pending**.
- **Audit pending** — `plan-audit` owns the pending audit handoff. The artifact is
  an exact plan workspace, proposal baseline, task packet, and assignment context
  identified for independent review. The state has two permitted report outcomes:
  **Audit passed** or **Audit findings**.
- **Audit passed** — `plan-audit` owns the external UTF-8 Markdown audit report with
  an overall `PASS` disposition and no finding handoff. This state has no fix
  transition unless a later explicit audit request or material change creates a new
  audit context.
- **Audit findings** — `plan-audit` owns the external report with stable finding
  IDs, check dispositions, evidence gaps, and remediation impact. The handoff names
  finding IDs only; the report does not change the audited plan.
- **Bounded plan-owned fix** — `plan-writer` owns a revision bounded by the exact
  finding IDs, proposal decision, source evidence, and stated impact. The audit
  report remains immutable, and the fix does not expand the proposal scope or
  replace the proposal decision.
- **Revised plan** — `plan-writer` owns the new plan snapshot and its preserved
  proposal and source traceability. The revised plan transitions to **Mandatory
  re-audit** rather than directly to a passed state.
- **Mandatory re-audit** — `plan-audit` owns a new external report against the
  revised immutable snapshot. The report returns the lifecycle to **Audit passed**
  or **Audit findings**; every further finding/fix loop repeats the same bounded
  transition.

## Evidence Labels And Handoff Shape

- `Proposal-derived:` identifies requirements, decisions, constraints, and
  verification criteria inherited from the proposal.
- `Source-derived:` identifies evidence and constraints inherited from source
  documents.
- `Assumption:` identifies unverified material.
- `Open Question:` identifies an unresolved decision for the responsible engineer.
- `Evidence Gap:` identifies missing material evidence rather than an inferred fact.
- An audit finding preserves its stable finding ID, exact needed input, and impact.
  The impact states which state or artifact cannot advance and keeps the fix bounded.

## Blocked Upstream-Decision Handoffs

Each blocked state preserves a named owner, an exact needed input, and an impact.
The planning reference does not infer a substitute input or transition.

- **Changed proposal decision** — owner: `proposal`; needed input: the revised
  authoritative proposal section, decision delta, and supporting evidence identity;
  impact: the existing plan snapshot is stale for audit and cannot enter a
  plan-writer fix until a new proposal baseline is available.
- **Missing evidence** — owner: `proposal`; needed input: the named source path or
  an explicit `Evidence Gap:` disposition identifying what is unavailable;
  impact: the affected decision, plan traceability, or audit criterion remains
  blocked and no claim can be promoted from `Assumption:` to evidence.
- **Baseline drift** — owner: `plan-audit`; needed input: the authoritative
  proposal baseline plus the changed-file identity and manifest/digest evidence;
  impact: the immutable snapshot is not auditable, so no pass or finding-driven fix
  handoff is valid until the baseline and plan context are reconciled.
- **Unavailable exact collector-backed capability** — owner: `plan-audit`; needed
  input: a fresh collector-backed record naming the exact `plan-audit` operation,
  class, and `SKILL.md` path required for the audit; impact: audit remains pending
  and blocked, with no fallback assignment, passive planning reference, pass, or
  finding result.

## Direct Non-Proposal Boundary

The direct `plan-only` path remains owned by `plan-writer` and may end at plan
publication when no proposal exists and no audit is requested. It does not inherit
the mandatory proposal-derived audit loop. An explicit audit request is the only
condition that adds an audit handoff to that direct path, subject to the separate
audit contract's required baseline and exact capability evidence.
