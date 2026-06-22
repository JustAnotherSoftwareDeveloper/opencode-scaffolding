---
name: dispatch-decompose
description: Use when the delegator must send the full user request and clarification context to a breakdown-tasks worker and return the worker's JSON decomposition output.
class: inline
---

# Dispatch Decompose

Construct the decomposition packet for `breakdown-tasks` and invoke exactly one worker with it.
Return the worker result unchanged.

## Input

Accept the full decomposition context as plaintext.
The input must include the original user request and the complete clarification context gathered by the delegator.
The clarification context should preserve question text and answers when available.

### Plaintext Packet Format Sent To Worker

```
## PURPOSE
Decompose the request into atomic task-delegation work items.

## DETAILS
<full original user request and clarification context, verbatim>

## FILES TO READ
None

## FILES TO WRITE
None

## SKILLS
breakdown-tasks

## EXECUTION INSTRUCTIONS
Load the breakdown-tasks skill and use it to decompose the full request and clarification context into atomic delegation packets. Return only the decomposition result.

## VERIFICATION
The output must be valid JSON parseable as a non-empty array. Every array element must be an object containing all 8 required camelCase keys: purpose, details, filesToRead, filesToWrite, skills, executionInstructions, verification, expectedOutput.

## EXPECTED OUTPUT
A non-empty JSON array of delegation packet objects with exactly the required camelCase keys for each object.
```

## Output

Return the result from the `breakdown-tasks` worker unchanged.

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

This is a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Always pass the complete original request and clarification context into `## DETAILS`.
- Never summarize, compress, omit, or reinterpret clarification answers.
- Never construct a decomposition packet without `## SKILLS` set to `breakdown-tasks`.
- Never invoke more than one worker.
- Never call any subagent type other than `worker`.
- Never parse or rewrite the worker result before returning it.
- Never write files.

## Docs

See `./reference/README.md` for supporting notes.
