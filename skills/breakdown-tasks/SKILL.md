---
name: breakdown-tasks
description: Use when decomposing a request into the smallest possible task-delegation work items.
class: inline
---

# Breakdown Tasks

This skill decomposes a request into atomic work items suitable for serial worker delegation.

## Input

Free-form prompt containing a request to decompose.

- **Overall goal**: The unified outcome the user wants
- **Implicit/explicit phases**: Any multi-step aspects already mentioned
- **All provided context**: Preserve meaning; do not omit details

## Output

A list of discrete work items, each with clear scope and boundaries.

### Output Format

A plaintext string of one or more delegation packets separated by `---` on its own line. Each packet uses the exact header names from task-delegation's Delegation Packet Template.

Each packet includes all of the following sections:

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

When multiple packets are produced, they are delimited by `---`:

```
## PURPOSE
First task

## DETAILS
...

## FILES TO READ
...

## FILES TO WRITE
...

## SKILLS
...

## EXECUTION INSTRUCTIONS
...

## VERIFICATION
...

## EXPECTED OUTPUT
...

---

## PURPOSE
Second task
```

Each work item is a complete delegation packet as defined in task-delegation's Delegation Packet Template.

## Atomic Task Unit

An atomic task is the smallest useful unit of work that can be delegated, executed, and verified independently.

### Core Rules

**1. Single file, single change** — Each atomic task touches exactly one file and makes exactly one logical change to it. A "logical change" is one coherent edit: adding a single function, renaming one identifier, updating one configuration value, writing one test case, etc. If a task would need to modify two files or make two unrelated edits to the same file, it must be split.

**2. Single output artifact** — Each atomic task produces exactly one verifiable output. That output is one of: one file written, one test result, one report, one lint/type-check pass, one deployment step, etc. If a task produces two outputs (e.g., writes a file *and* runs a test), it is too large — split the verification from the production.

**3. Logical step pipeline** — Tasks form a pipeline where each is one discrete step in a sequence. Steps that can be done independently (no dependency on prior output) should be separate parallel-capable tasks. Steps that depend on prior output should be sequential but still individually atomic. Examples of valid pipelines:

- Design stubs → implement one function → check code style → fix style issues
- Write test stubs → implement one test → verify that test passes
- Define schema → write migration → update model → update query

### Anti-Patterns (Too Large)

| Anti-pattern | Why it's too large | Correct split |
|---|---|---|
| "Add user authentication" | Touches multiple files (routes, middleware, model, tests) and produces multiple outputs | Pipeline: (1) write auth middleware, (2) add login route, (3) add user model method, (4) write auth tests, (5) run tests |
| "Implement `calculate_total` and add error handling" | Two logical changes to the same file | Pipeline: (1) implement `calculate_total`, (2) add error handling to `calculate_total` |
| "Write `utils.py` with three helper functions" | Three logical changes in one file write | Pipeline: (1) add `parse_date` helper, (2) add `format_currency` helper, (3) add `validate_email` helper |
| "Refactor `checkout` and run all tests" | Produces two outputs (file change + test run) | Pipeline: (1) refactor `checkout`, (2) run tests to verify refactor |

### Correct Examples (Atomic)

**Example 1 — Single function addition:**
```
## PURPOSE
Add a `validate_email` function to utils/validation.py

## DETAILS
...
## FILES TO WRITE
utils/validation.py
## EXPECTED OUTPUT
The updated utils/validation.py with the new function
```

**Example 2 — Verify after change (separate task):**
```
## PURPOSE
Run the test suite for utils/validation.py to confirm `validate_email` passes

## DETAILS
...
## FILES TO READ
utils/validation.py, tests/test_validation.py
## EXPECTED OUTPUT
Test results showing all tests pass
```

### Same-File Pipeline Guidance

When multiple changes to the same file are needed, do not combine them into one task. Instead, serialize them as separate sequential tasks in the pipeline. Each task makes one logical edit to the file, and the next task picks up the result. For example, to add two functions to `utils.py`:

1. Task A: Add `parse_date` to `utils.py`
2. Task B: Add `format_currency` to `utils.py`

Each task lists `utils.py` in `## FILES TO WRITE`, and Task B's `## DETAILS` notes that `parse_date` already exists. The delegator runs them in order, so Task B always sees Task A's output.

## Execution Plan

1. Parse [Input](#input) into independently verifiable work
2. Split work to the finest useful granularity in [Atomic Task Unit](#atomic-task-unit)
3. Order tasks so that each task's prerequisites are satisfied by earlier tasks in the sequence. Do not bundle dependent changes into a single task.
4. Return tasks as plaintext `---` delimited delegation packets using the [Output Format](#output-format)

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task; omit background and rationale.
