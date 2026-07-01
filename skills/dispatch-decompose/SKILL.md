---
name: dispatch-decompose
description: "Use when the delegator must send the full user request and clarification context to a breakdown-tasks worker and return the worker result unchanged."
tags: [workflow, internal]
class: inline
---

# Dispatch Decompose

Construct the decomposition packet for `breakdown-tasks`.
Invoke exactly one worker with the packet.
Return the worker result unchanged.

## Input

Accept the full decomposition context as plaintext.
Include the original user request and the complete clarification context gathered by the delegator.
Preserve question text and answers in the clarification context when available.

### Plaintext Packet Format Sent To Worker

```text
## PURPOSE
Decompose the request into atomic task-delegation work items.

## DETAILS
<full original user request and clarification context, verbatim>

## FILES TO READ
None

## FILES TO WRITE
.tasks/ state file (~/.config/opencode/.tasks/<unix-epoch-seconds>-<request-summary-slug>.json)

## SKILLS
breakdown-tasks

## EXECUTION INSTRUCTIONS
Load the breakdown-tasks skill and use it to decompose the full request and clarification context into atomic delegation packets.
Return only the filename of the `.tasks/` state file written during decomposition.
Maintain decomposition state in the .tasks/ file declared in ## FILES TO WRITE.

## VERIFICATION
The output must be a non-empty string. It must not be whitespace-only. It must be a valid filename matching the pattern `<digits>-<slug>.json`.

## EXPECTED OUTPUT
A single string: the filename of the `.tasks/<epoch>-<slug>.json` state file written during decomposition.
```

## Output

Return the result from the `breakdown-tasks` worker unchanged.
`PARTIAL:` is a valid success signal from the worker.
Preserve and forward `PARTIAL:` as-is without transformation or rejection.

## Execution Plan

1. **Accept decomposition context** from the delegator.
   Confirm it includes the original user request and the clarification context.
2. **Reject empty context.**
   If the input is absent, empty, or whitespace-only, return `BLOCKED: dispatch-decompose requires the full request and clarification context.`
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
6. **Return the worker result unchanged.**
   Do not parse, normalize, summarize, or reformat the worker output.
   If the output contains `PARTIAL:` followed by JSON, treat it as a valid completion signal.
   Forward it as-is.
   Do not reject, re-route, or re-wrap `PARTIAL:` responses.

Execute this as a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Always pass the complete original request and clarification context into `## DETAILS`.
- Never summarize, compress, omit, or reinterpret clarification answers.
- Never construct a decomposition packet without `## SKILLS` set to `breakdown-tasks`.
- Never invoke more than one worker.
- Never call any subagent type other than `worker`.
- Never parse or rewrite the worker result before returning it.
- Never treat `PARTIAL:` as an error.
  Forward `PARTIAL:` unchanged when the worker returns it.
- Never write files outside the .tasks/ state file declared in ## FILES TO WRITE.

## Docs

See `./reference/README.md` for supporting notes.
