---
name: task-delegation
description: Use when validating a delegation packet and forwarding it to a worker via the task tool.
class: inline
---

# Task Delegation

Validate a delegation packet and forward it to a worker via the task tool.

## Input

One delegation packet using the standard header format.
See [Packet Format](#packet-format) for required sections.
Do not split, merge, or transform the packet.
Forward it to the worker as-is.

### Packet Format

```
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated file paths to read>

## FILES TO WRITE
<single file path, or "None">

## SKILLS
<comma-separated skill names to load>

## EXECUTION INSTRUCTIONS
<step-by-step instructions for execution>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

## Output

The result returned by the worker matching the packet's `## EXPECTED OUTPUT`.

## Execution Plan

1. Validate the packet has all 8 required sections — see [Packet Format](#packet-format).
2. Invoke the `task` tool with `subagent_type: "worker"`, `description` from `## PURPOSE`, `prompt` as the full delegation packet, and `command` set to the `## PURPOSE` content.
3. Return the worker result.

This is a single-pass process.
Launch exactly one worker task per invocation.

## Guardrails

- Reject malformed packets with a clear description of what is missing or invalid.
- Do not modify, re-encode, or transform the packet.