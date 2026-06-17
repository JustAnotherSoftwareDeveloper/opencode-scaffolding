---
name: breakdown-tasks
description: Use when decomposing a request into the smallest possible task-delegation work items.
class: inline
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.

## Input

Free-form prompt containing a request to decompose.

- **Overall goal**: The unified outcome the user wants.
- **Implicit or explicit phases**: Multi-step aspects already mentioned.
- **Provided context**: Preserve meaning; do not omit details.

## Output

A plaintext string of one or more delegation packets separated by `---` on its own line.
The consumer splits the output on `---` delimiters before forwarding each packet to a worker.
Each packet uses the exact header names from the Delegation Packet Template.

### Packet Template

```
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated file paths to read>

## FILES TO WRITE
<single file path or "None">

## SKILLS
<comma-separated skill names to load>

## EXECUTION INSTRUCTIONS
<step-by-step instructions for execution>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

Delimit multiple packets with `---` on its own line between them.

## Atomic Task Unit

An atomic task is the smallest useful unit of work that can be delegated, executed, and verified independently.

### Core Rules

1. **Single file, single change** — Each task touches exactly one file and makes exactly one logical change.
   If a task modifies two files or makes two unrelated edits to the same file, split it.

2. **Single output artifact** — Each task produces exactly one verifiable output.
   If a task produces two outputs (e.g., writes a file and runs a test), split verification from production.

3. **Logical step pipeline** — Tasks form a pipeline where each is one discrete step in a sequence.
   Independent steps must be separate parallel-capable tasks.
   Dependent steps must be sequential but still individually atomic.

4. **Same-file serialization** — When multiple changes to the same file are needed, serialize them as separate sequential tasks.
   Each task lists the file in `## FILES TO WRITE`.
   Run tasks in order so each sees the prior task's output.

### Anti-Patterns

- **"Add user authentication"** — Touches multiple files and produces multiple outputs.
  Split into: middleware, route, model, tests, test run.
- **"Implement X and add error handling"** — Two logical changes to the same file.
  Split into two sequential tasks.
- **"Write utils.py with three helpers"** — Three logical changes in one file write.
  Split into three sequential tasks.
- **"Refactor checkout and run tests"** — Produces two outputs.
  Split into refactor task then test-run task.

## Execution Plan

1. Parse [Input](#input) into independently verifiable work items.
2. Split work to the finest useful granularity per [Core Rules](#core-rules) and [Anti-Patterns](#anti-patterns).
3. Order tasks so prerequisites are satisfied by earlier tasks.
4. Return tasks as plaintext `---` delimited delegation packets per [Packet Template](#packet-template).

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task; omit background and rationale.
- Do not bundle dependent changes into a single task.