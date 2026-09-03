---
name: plan-audit
description: "Use when auditing one immutable proposal-derived plan snapshot without changing audited inputs."
selection:
  role: owner
  tags:
    actions: [audit]
    inputs: [plan workspace, proposal baseline, task packet]
    outputs: [UTF-8 Markdown audit report]
    topics: [proposal traceability, task atomicity, exact skill assignment]
    constraints: [read-only, immutable snapshot, external report only]
  use_when:
    - a caller requests an independent audit of one plan and proposal input snapshot
  not_for:
    - creating or revising a plan
    - repairing findings or assigning replacement skills
    - approving a proposal or changing readiness
class: operation
---

# Plan Audit

Audit one immutable plan/proposal snapshot and publish one external report. The
operation is evidence-only: it never edits an audited tree, repairs a finding,
republishes a packet, changes readiness, approves work, or delegates.

## Normalize Input

Require one object with `planWorkspace`, `proposalBaseline`, `assignmentInventory`,
and `auditOutput`. `planWorkspace` and `auditOutput` resolve under the caller's
workspace root. The baseline is `authoritative` by default; `copied-snapshot` is
accepted only when the caller supplies an explicit unavailable/unreadable reason,
origin identity, capture time, PROPOSAL.md plus its declared copied sources, and
per-file manifest. The operation populates `assignmentInventory` from its one fresh
collector run; any caller-supplied inventory is historical comparison evidence only
and never replaces that fresh result.

An authoritative baseline must contain `PROPOSAL.md` with valid frontmatter
(`title`, `slug`, `status`, `readiness`, `decision-owner`, `source-documents`),
the required H2 sections (`Recommendation`, `Technical Rationale`, `Questions`,
`Options Considered`, `Implementation Details`, `Verification Criteria`, `Sources`),
and every frontmatter-declared copied source file.
Record status and readiness as evidence facts without treating either as approval.

Block before writing when a required path is absent, the report parent is absent,
the report already exists, the report is inside an audited tree, or the baseline
fallback is incomplete.

## Procedure

1. Resolve the input object and prove that the new report path is outside the plan,
   proposal, copied-source, persisted-inventory, and selected-skill trees.
2. Run the exact collector command once:

   ```text
   uv run --project ~/.config/opencode/scripts/python collect-skills \
     --class operation --class documentation
   ```

   Retain its complete JSON array and provenance; a failed or invalid run
   blocks skill assignment and does not permit a persisted inventory fallback.
3. Reconcile and read the exact fresh `task-contract` documentation winner as
   passive semantic context; it grants no authority, execution, or completion
   evidence. Then read the proposal baseline (PROPOSAL.md plus declared copied
   sources), plan packet,
   rendered task document, and selected skill contracts. Create a sorted SHA-256
   manifest containing every resolved input path, byte length, and digest before
   evaluating checks.
4. Evaluate proposal compliance, conceptual and structural task atomicity, and exact
   skill assignment independently. Allow documentation entries as passive context
   when the task also has a fitting operation owner. Use stable finding IDs derived
   from check family, criterion, relative location, and expected/observed evidence.
5. Recompute the manifest immediately before output.
   Mark affected checks `BLOCKED` when drift is found, then render exactly one
   composite Markdown report atomically at the caller's new path.
6. Record bounded remediation handoff to `plan-writer` using finding IDs only;
   do not apply, validate, or self-certify a correction.

## Self-Validation

- The report contains audit provenance, the complete manifest and collector array,
  overall disposition, all three check sections, evidence gaps, and remediation.
- Every check and the rollup is exactly `PASS`, `CONDITIONAL PASS`, `FAIL`, or
  `BLOCKED`; overall precedence is `BLOCKED`, then `FAIL`, then `CONDITIONAL PASS`,
  then `PASS`.
- A fresh collector failure, missing baseline evidence, invalid required input,
  or input drift is never represented as a pass.
- The report is new UTF-8 Markdown and no audited file changes byte-for-byte.

## Expected Output

Write only the caller-declared new Markdown report. The report is a deterministic
composite audit record with a run timestamp for provenance, stable finding IDs,
independently statused check families, and no approval or correction claim.

## Docs

See `./reference/README.md` for the input, report, checks, and traceability contracts.

See [input contract](reference/input-contract.md), [report contract](reference/report-contract.md),
[check rules](reference/checks.md), and [requirements traceability](reference/requirements-traceability.md).
The executable implementation is
[`scripts/plan_audit.py`](scripts/plan_audit.py).
Invoke it with the repository Python environment so the shared collector and validator
are available: `uv run --project ~/.config/opencode/scripts/python python
skills/plan-audit/scripts/plan_audit.py --help`.
