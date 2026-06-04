---
name: delegation
description: Construct bounded worker handoff packets for single-worker text processing (worker-md) or visual analysis (multimodal-looker), consume results, and handle packet repair.
class: orchestrated
---

# Delegation Skill

Use this skill when a runbook step should be handed to a worker subagent through OpenCode's Task tool pattern. This is the **canonical source of truth** for single-worker routing and handoff packet construction. It does not replace the Task tool or create a new agent framework.

## Responsibilities

1. Route text work to `worker-md`; route visual/PDF/image analysis to `multimodal-looker`.
2. Construct a bounded worker handoff packet using the template at `templates/delegation-packet.md`.
3. Consume the worker result and reconcile it into runbook state.
4. Handle failures via packet repair, same-worker retry (for defective packets or transient issues), or return to user.

## Non-Goals

- Do not replace OpenCode's Task tool.
- Do not add team-mode, tmux, plugin, MCP, model, provider, or agent-registration infrastructure.
- Do not create new worker families beyond `worker-md` and `multimodal-looker`.
- Do not bypass plan dependencies, file scopes, permissions, or state ownership.

## Worker Routing

| Work type | Route to |
|-----------|----------|
| Analysis, reasoning, tradeoffs, risk, architecture, critique | `worker-md` |
| Code editing, implementation, refactor, debugging, config writing | `worker-md` |
| Documentation, prompts, skills, commands, guides, structured prose | `worker-md` |
| Synthesis, coordination, classification, extraction, general-purpose tasks | `worker-md` |
| Web research, current facts, source synthesis, evidence comparison | `worker-md` |
| Image/screenshot/diagram/PDF analysis | `multimodal-looker` |

## Handoff Packet Construction

Select the delegation-packet template at `skills/delegation/templates/delegation-packet.md`. The packet must include:

- Orchestrator name;
- Skill to load, or `none`;
- One bounded objective;
- Relevant context and inputs;
- Files in and out of scope;
- Explicit do / do-not instructions;
- State file the worker may update (or "none");
- Verification expectations;
- Required return format.

**Context fit rule**: If required context cannot fit without overstuffing, decompose into smaller sub-units rather than enlarging the packet beyond its intended scope.

If delegated work creates or edits JSON/YAML, include an appropriate validator in verification:

- `uv run --project scripts/python validate-json <file>`
- `uv run --project scripts/python validate-json <file> --schema <schema-file>`
- `uv run --project scripts/python validate-yaml <file>`

## Result Consumption

OpenCode does not provide a documented structured child-session result protocol. Use explicit conventions:

- The worker must end with a concise final summary.
- For runbook execution, workers may update assigned step state only when explicitly instructed; otherwise the orchestrator reconciles runbook-local `state.xml`.
- Workers should not edit runbook-level state, proposal artifacts, or plan artifacts unless explicitly assigned.
- If a worker cannot complete the task, it must report blockers, attempted actions, partial outputs, and recommended recovery.

## Failure Handling

1. **Ambiguous packet** — Repair before retry: clarify objective, scope, acceptance criteria, or context.
2. **Worker lacks capability** — Retry with same worker after repair; if still failing, return to user.
3. **Permission or scope blocker** — Stop and report; do not expand scope silently.
4. **Repeated attempts fail** — Return to user after documenting blockers.

## Safety Rules

- Do not delegate without clear objective, scope, acceptance criteria, and expected output.
- Do not ask a worker to modify files outside `files_in_scope`.
- Do not delegate destructive git operations or provider/model/config edits unless explicitly authorized.
- Do not hide unresolved assumptions; include in packet or stop for clarification.
- Only route to configured workers: `worker-md` and `multimodal-looker`.
