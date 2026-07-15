---
name: dispatch-decompose
description: "Use when the delegator must send the full user request to a breakdown-tasks worker and return the relative .tasks path unchanged."
tags: [request-forwarding, worker-invocation, packet-construction, breakdown-dispatch, worker-launch]
class: inline
---

# Dispatch Decompose

Construct the decomposition packet for `breakdown-tasks`.
Invoke exactly one worker with the packet.
Return a valid worker `.tasks/` path unchanged, or return `BLOCKED:` for invalid output.

## Input

Accept the effective request context as plaintext — not necessarily the latest user message.
When the user references prior work ("execute it", "use that info"), the caller must resolve what that prior work entails before invoking this skill.
Preserve the resolved context verbatim in the decomposition packet.

### Plaintext Packet Format Sent To Worker

```text
## PURPOSE
Decompose the request into atomic task-delegation work items.

## DETAILS
<full original user request, verbatim>

## FILES TO READ
None by default. When the effective request depends on a prior proposal, plan, or task file, include those paths.

## FILES TO WRITE
.tasks/<summary-slug>.json

## SKILLS
breakdown-tasks

## EXECUTION INSTRUCTIONS
Load the breakdown-tasks skill and use it to decompose the full request into atomic delegation packets.
Return only the relative `.tasks/` path of the state file written during decomposition.
Maintain decomposition state in the .tasks/ file declared in ## FILES TO WRITE.

## VERIFICATION
The output must be a non-empty string. It must not be whitespace-only. It must be a relative path matching `.tasks/<kebab-case-slug>.json`.
Do NOT wrap the path in backticks, Markdown code spans, or any other formatting. Return the raw path string only.

## EXPECTED OUTPUT
A single string: the relative `.tasks/<summary-slug>.json` path written during decomposition.
```

## Output

Return a valid relative `.tasks/` path from the `breakdown-tasks` worker unchanged.
`BLOCKED:` is the only valid non-path response.
Do not accept `PARTIAL:` for decomposition output.

## Execution Plan

1. **Accept decomposition context** from the delegator.
   Confirm it includes the original user request.
2. **Reject empty context.**
   If the input is absent, empty, or whitespace-only, return `BLOCKED: dispatch-decompose requires the full original user request.`
3. **Construct the decomposition packet.**
   Use the packet template above.
   Insert the full input verbatim into `## DETAILS`.
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
6. **Validate and return the worker result.**
    Strip leading/trailing backticks (`` ` ``), whitespace, and newlines from the worker output before matching.
     If the cleaned result is a relative path matching `.tasks/<kebab-case-slug>.json`, forward the cleaned path.
    If the cleaned result is `BLOCKED:`, forward it unchanged.
    Treat `PARTIAL:` or any other output shape as invalid and return `BLOCKED: decomposition must return a relative .tasks path or BLOCKED.`

Execute this as a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Always pass the complete original request into `## DETAILS`.
- Never summarize, compress, omit, or reinterpret the request.
- Never construct a decomposition packet without `## SKILLS` set to `breakdown-tasks`.
- Never invoke more than one worker.
- Never call any subagent type other than `worker`.
- Never rewrite a valid relative `.tasks/` path before returning it.
- Never treat `PARTIAL:` as valid decomposition output.
- Never write files outside the .tasks/ state file declared in ## FILES TO WRITE.

## Docs

See `./reference/README.md` for supporting notes.
