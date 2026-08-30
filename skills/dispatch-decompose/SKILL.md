---
name: dispatch-decompose
description: "Use when forwarding an effective request or focused correction context to a breakdown-tasks worker and returning its relative tasks path."
selection:
  role: owner
  tags:
    actions: [dispatch decomposition, corrective decomposition]
    inputs: [effective request context, focused correction feedback]
    outputs: [relative tasks path]
    topics: [task delegation]
  use_when: [a delegator must invoke breakdown-tasks and forward its path]
  not_for: [decomposing tasks directly]
class: inline
---

# Dispatch Decompose

Construct one decomposition packet for `breakdown-tasks`. The effective context may
be the full original request or the original request followed by concise feedback
from a semantic review. Preserve the original outcome and make correction context
explicit; do not provide implementation advice or silently change intent.
Invoke exactly one worker with the packet.
Validate the canonical worker envelope and return a valid `.tasks/` path from it.
Return `BLOCKED:` for incomplete, blocked, or malformed worker results.

## Input

Accept the effective request context as plaintext — not necessarily the latest user message.
When the user references prior work ("execute it", "use that info"), the caller must resolve what that prior work entails before invoking this skill.
Preserve the resolved context verbatim in the decomposition packet.

### Plaintext Packet Format Sent To Worker

```text
## PURPOSE
Decompose the request into atomic task-delegation work items.

## DETAILS
<effective request context, including focused correction feedback when present>

## FILES TO READ
<required source-document paths, or None>

## FILES TO WRITE
.tasks/<epoch-milliseconds>-<summary-slug>.json

## SKILLS
breakdown-tasks

## EXECUTION INSTRUCTIONS
Load the breakdown-tasks skill and use it to decompose the full request into atomic delegation packets.
Place only the relative `.tasks/` path of the state file in the worker envelope's Deliverable section.
Maintain decomposition state in the .tasks/ file declared in ## FILES TO WRITE.

## VERIFICATION
The Deliverable payload must be a non-empty string. It must not be whitespace-only. It must match `^\.tasks/[0-9]{13}-[a-z0-9]+(?:-[a-z0-9]+)*\.json$`.
Do NOT wrap the Deliverable path in backticks, Markdown code spans, or any other formatting.

## EXPECTED OUTPUT
A single string payload under Deliverable: the relative `.tasks/<epoch-milliseconds>-<summary-slug>.json` path written during decomposition.
```

## Output

First read `~/.config/opencode/output-contract-template.md` and validate the
complete worker envelope against that canonical contract and the ordinary
`task-delegation` reconciliation rules. Then return the valid relative `.tasks/` path
extracted from a `COMPLETE` envelope.
Return `BLOCKED:` for every non-complete or invalid result.

## Execution Plan

1. **Accept decomposition context** from the delegator.
   Confirm it includes the original user request.
2. **Reject empty context.**
   If the input is absent, empty, or whitespace-only, return `BLOCKED: dispatch-decompose requires the full original user request.`
3. **Construct the decomposition packet.**
   Use the packet template above.
   Insert the full input verbatim into `## DETAILS`.
   Set `## FILES TO READ` to `None` unless the effective request identifies required source-document paths.
   Keep `## FILES TO WRITE` as the literal bounded pattern `.tasks/<epoch-milliseconds>-<summary-slug>.json`.
   Do not resolve either placeholder; `breakdown-tasks` derives the actual timestamp and slug.
   Keep `## SKILLS` hardcoded to `breakdown-tasks`.
4. **Validate the packet.**
   Confirm all 8 standard packet sections are present.
   Confirm `## DETAILS` contains the complete input verbatim.
   Confirm `## SKILLS` is exactly `breakdown-tasks`.
5. **Invoke the worker.**
   Call the `task` tool with `subagent_type: "worker"`.
   Set `description` to `Decompose request into atomic tasks`.
   Set `command` to `Decompose request into atomic tasks`.
   Set `prompt` to the complete decomposition packet.
6. **Validate the worker result envelope.**
   Read `~/.config/opencode/output-contract-template.md` and validate the report
   against its complete envelope grammar, status rules, reconciliation rules, and
   payload boundary.
   Return `BLOCKED: decomposition worker returned a malformed result envelope.` when validation fails.
7. **Handle non-complete status.**
   Return `BLOCKED: decomposition worker was blocked — <Blocker>. Unblock condition: <Unblock condition>.` for `BLOCKED`.
   Return `BLOCKED: decomposition requires COMPLETE status; worker returned PARTIAL.` for `PARTIAL`.
8. **Extract and validate the payload.**
   Read all content after the `## Deliverable` heading.
   Strip leading and trailing whitespace.
   Return the payload unchanged when it matches `^\.tasks/[0-9]{13}-[a-z0-9]+(?:-[a-z0-9]+)*\.json$`.
   Return `BLOCKED: decomposition deliverable must be a timestamped relative .tasks path.` for every other payload.

Execute this as a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Always pass the complete original request into `## DETAILS`.
- Never summarize, compress, omit, or reinterpret the original request. Focused
  correction feedback may be appended only to explain a diagnosed decomposition defect.
- Never construct a decomposition packet without `## SKILLS` set to `breakdown-tasks`.
- Never replace the `## FILES TO WRITE` placeholders before worker execution.
- Never invoke more than one worker.
- Never call any subagent type other than `worker`.
- Never rewrite a valid relative `.tasks/` payload before returning it.
- Never treat `PARTIAL` or `BLOCKED` worker status as valid decomposition output.
- Never accept an envelope that violates
  `~/.config/opencode/output-contract-template.md`.
- Never write files outside the .tasks/ state file declared in ## FILES TO WRITE.

## Docs

See `./reference/README.md` for supporting notes.
