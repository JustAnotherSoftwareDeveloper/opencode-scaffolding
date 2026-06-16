---
name: task-delegation
description: Use when validating a delegation packet and forwarding it to a worker via the task tool.
class: inline
---

# Task Delegation

This skill validates a delegation packet and forwards it to a worker via the task tool.

## Input

One delegation packet using the standard header format (`## PURPOSE`, `## DETAILS`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, `## EXPECTED OUTPUT`).

## Delegation Packet Template

Flat structure optimized for small worker models. This is the format the input packet should conform to and the format forwarded to workers.

```
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated file paths to read>

## FILES TO WRITE
<comma-separated file paths to write, if any>

## SKILLS
<comma-separated skill names to load>

## EXECUTION INSTRUCTIONS
<step-by-step instructions for execution>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

Since the packet arrives as plaintext headers, array values are already formatted as bullet lists or comma-separated values by the sender. No conversion is needed.

## Execution Plan

1. Validate the delegation packet has all required sections: `## PURPOSE`, `## DETAILS`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, `## EXPECTED OUTPUT`.
2. Use the packet as-is — no transformation needed. The packet is already in the Delegation Packet Template format.
3. Invoke the `task` tool with `subagent_type: "worker"`, `description` from `## PURPOSE`, `prompt` as the full delegation packet, and `command` as the `## PURPOSE` content or original user request.
4. Return the worker result requested by `## EXPECTED OUTPUT`.

## Guardrails

- Validate that all 8 required sections (`## PURPOSE`, `## DETAILS`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, `## EXPECTED OUTPUT`) are present in the packet.
- Reject malformed packets (missing sections, unrecognized format) with a clear description of what is missing or invalid.
- Do not modify, re-encode, or transform the packet. Forward it to the worker exactly as received.
- Launch exactly one worker task per invocation.