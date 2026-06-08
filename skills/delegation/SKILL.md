---
name: delegation
description: Coordinate runbook steps via Worker Handoff Packets, routes work to specific workers (worker/multimodal-looker), constructs packets with explicit contracts, consumes worker results, and handles failures through packet repair or escalation.
class: orchestrated
---

# Delegation Skill (Orchestrator)

This skill is the canonical source of truth for single-worker routing and handoff packet construction in OpenCode's Task tool pattern. It does **not** replace the Task tool or create a new agent framework—instead, it provides structured coordination protocols that use direct templating at `templates/delegation-packet.md` for worker-executed tasks.

## Responsibilities

1. **Route text work** to `worker`; route visual/PDF/image analysis to `multimodal-looker`.
2. **Construct a bounded Worker Handoff Packet** using the delegation-packet template at `templates/delegation-packet.md` with explicit contracts.
3. **Consume the worker result and reconcile it** through direct inspection for simple cases or runbook-local state reconciliation.  
4. Handle failures via packet repair (iterate with same worker), same-worker retry (for defective packets/transient issues), or return to user after repeated attempts fail.

## Subskills / Dependencies

- **Direct templating** — Primary approach for packet construction (use this template directly)
  - `templates/delegation-packet.md`

## Non-Goals

- Do not replace OpenCode's Task tool.
- Do not add team-mode, tmux, plugin, MCP, model provider registration infrastructure.
- Do not create new worker families beyond `worker` and `multimodal-looker`.
- Do not bypass plan dependencies, file scopes, permissions, or state ownership.

## Worker Routing Table

| Work type | Route to | Notes |
|-----------|----------|-------|
| Analysis, reasoning, tradeoffs, risk, architecture, critique | `worker` | General text processing and synthesis |
| Code editing, implementation, refactor, debugging, config writing | `worker` | Follow task-mode guardrails strictly |
| Documentation, prompts, skills, commands, guides, structured prose | `worker` | Ensure proper frontmatter in created files |
| Synthesis, coordination, classification, extraction, general-purpose tasks | `worker` | Often benefits from explicit verification steps |
| Web research, current facts, source synthesis, evidence comparison | `worker` | Include blocker policy for uncertain findings |
| Image/screenshot/diagram/PDF analysis | `multimodal-looker` | Specify what visual elements to extract/analyze |

## Handoff Packet Construction Protocol

Select the delegation-packet template at `skills/delegation/templates/delegation-packet.md`. The packet must include:

- **Orchestrator name**;
- **Skill to load**, or `none`;  
- One bounded objective;
- Relevant context and inputs;
- Files in and out of scope;
- Explicit Do / Do-not instructions;
- State file the worker may update (or "none");
- Verification expectations;
- Required return format.

**Delegation flow - Direct templating:** Fill template directly without additional delegation:

1. Select the delegation-packet template at `skills/delegation/templates/delegation-packet.md`  
2. Complete all required sections with your objective and scope details
3. Proceed with Task tool call using the completed packet

**Context fit rule:** If required context cannot fit without overstuffing, decompose into smaller sub-units rather than enlarging the packet beyond its intended scope.

If your packet creates or edits JSON/YAML, include an appropriate validator in verification:

- `uv run --project scripts/python validate-json <file>`
- `uv run --project scripts/python validate-json <file> --schema <schema-file>`  
- `uv run --project scripts/python validate-yaml <file>`

## Result Consumption & Reconciliation Protocol

OpenCode does not provide a documented structured child-session result protocol. Use explicit conventions:

### Direct reconciliation (primary approach):
- The worker must end with a concise final summary.
- For runbook execution, workers may update assigned step state only when explicitly instructed; otherwise the orchestrator reconciles runbook-local `state.xml`.
- Workers should not edit runbook-level state, proposal artifacts, or plan artifacts unless explicitly assigned.

### Flow control decisions (conceptual reference):

| Worker status | Decision | Orchestrator action |
|---------------|----------|---------------------|
| Completed (valid) | proceed | Continue to next step |
| Failed/Blocked | fail | Return to user with blockers documented |
| Retryable error | retry | Repair packet, re-invoke same worker skill |

## Failure Handling Strategy

1. **Ambiguous packet** — Repair before retry: clarify objective, scope, acceptance criteria, or context using the delegation-packet template directly.
2. **Worker lacks capability** — Retry with same worker after repair; if still failing after 3 attempts, return to user.  
3. **Permission or scope blocker** — Stop and report; do not expand scope silently.
4. **Repeated attempts fail** — Return to user after documenting blockers with partial outputs preserved for inspection.

## Safety Rules

- Do not delegate without clear objective, scope, acceptance criteria, and expected output.  
- Do not ask a worker to modify files outside `files_in_scope`.
- Do not delegate destructive git operations or provider/model/config edits unless explicitly authorized.  
- Do not hide unresolved assumptions; include in packet or stop for clarification.
- Only route to configured workers: `worker` and `multimodal-looker`.

## Nano-Reader Routing (Workflow Artifact Inspection)

The following bounded routing applies for workflow artifact inspection only:

| Work Type | Route to | Scope/Constraints |  
|-----------|----------|-------------------|
| Read-only summary/stamp of `.proposals/`, `.plans/`, `.runbooks/` state or evidence files | `nano-reader` | Read-only; cannot edit any files. Used when orchestrator needs quick verification without full analysis depth.