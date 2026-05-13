---
name: delegation
description: Build OpenCode Task tool delegation packets, select worker family/size, consume worker results, and handle retry or escalation.
---

# Delegation Skill

Use this skill when an orchestration plan step should be handed to a worker subagent through OpenCode's Task tool pattern. This skill defines the packet and result-consumption convention; it does not replace the Task tool or create a new agent framework.

## Responsibilities

1. Convert a plan step into a bounded delegation packet.
2. Select the smallest capable worker family and size.
3. Include all context the worker needs without rereading the full conversation.
4. State files in scope, files out of scope, expected output, verification, and recovery.
5. Tell the worker how to return results and which state/artifact files to update.
6. Reconcile worker output into the orchestrator's plan state.
7. Retry, redelegate, or escalate only when the packet's recovery policy permits it.

## Non-Goals

- Do not replace OpenCode's Task tool.
- Do not add team-mode, tmux, plugin, MCP, model, provider, or agent-registration infrastructure.
- Do not create new worker families or model IDs.
- Do not bypass plan dependencies, file scopes, permissions, or state ownership.

## Worker Routing

Use the current harness worker chart:

| Work | Worker |
| --- | --- |
| Tiny supplied-context checks, extraction, naming, short summaries | `generic-xs`, `analysis-xs`, `doc-writer-xs`, `websearch-xs` |
| Bounded synthesis, simple comparisons, narrow local discovery | `generic-sm`, `analysis-sm`, `doc-writer-sm`, `websearch-sm` |
| Read-only local discovery and inventory | `explore`, `generic-sm`, `generic-md` |
| Tool-heavy discovery or multi-file investigation | `explore` for read-only search; otherwise `generic-md` or `generic-lg` |
| Reasoning, tradeoffs, risks, architecture, dependency validation | `analysis-sm`, `analysis-md`, `analysis-lg`, `analysis-xl` |
| Embedded review and final judgment | `analysis-md`, `analysis-lg`, `analysis-xl` |
| Tiny code suggestions or patch sketches | `coding-xs`, `coding-sm` |
| Code, config, schema, or template edits | `coding-md`, `coding-lg`, `coding-xl` |
| Skill, prompt, command, and documentation prose | `doc-writer-sm`, `doc-writer-md`, `doc-writer-lg`, `doc-writer-xl` |
| General synthesis or coordination support | `generic-sm`, `generic-md`, `generic-lg`, `generic-xl` |
| Current external documentation or source-critical research | `websearch-md`, `websearch-lg`, `websearch-xl` |
| Images, screenshots, diagrams, and PDFs | `multimodal-looker` |

Choose the smallest reliable tier. Escalate when the task has high ambiguity, high cost of error, broad file scope, failed prior attempts, or architecture-sensitive judgment.

## Packet Construction

Use `templates/delegation-packet.md` as the canonical packet template. A packet must include:

- `target_agent`: exact worker/subagent name to invoke.
- `skill`: skill to load, or `null`.
- `objective`: one bounded objective.
- `context_package`: user requirement slice, proposal sections, state files, files in/out of scope, and expected return format.
- `state_updates`: state files the worker may update.
- `acceptance_criteria`: success criteria.
- `verification`: checks the orchestrator or worker should run.
- `result_consumption`: how the orchestrator reads the worker result.
- `recovery_escalation`: retry, redelegation, escalation, or stop conditions.

## Result Consumption

OpenCode does not provide a documented structured child-session result protocol. Use explicit conventions:

- The worker must end with a concise final summary.
- For plan execution, the worker should also write the assigned `.state/<plan_slug>/<step>.md` file when write access is in scope.
- The orchestrator reconciles `metadata.json` and `MAIN.md`; workers should not edit those unless explicitly assigned.
- If a worker cannot complete the task, it must report blocker, attempted actions, partial outputs, and recommended recovery.

## Failure Handling

1. If the packet is ambiguous, repair the packet before retrying.
2. If the worker lacks capability, redelegate to the next capable family/size.
3. If the worker hits a permission or scope blocker, stop and report rather than expanding scope silently.
4. If repeated attempts fail, escalate to `analysis-lg` or `coding-lg` depending on whether the blocker is reasoning or implementation.
5. Record retries and escalation decisions in the relevant step state file.

## Safety Rules

- Do not delegate work that lacks clear objective, scope, acceptance criteria, and expected output.
- Do not ask a worker to modify files outside `files_in_scope`.
- Do not delegate destructive git operations or provider/model/config edits unless a plan explicitly authorizes them.
- Do not hide unresolved assumptions; include them in the packet or stop for clarification.
