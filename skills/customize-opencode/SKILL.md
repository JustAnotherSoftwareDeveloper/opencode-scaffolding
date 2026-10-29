---
name: customize-opencode
description: "Use when reference is needed for OpenCode worker packet execution-engine behavior."
selection:
  role: reference
  tags:
    inputs: [worker packet]
    outputs: [execution engine reference]
    topics: [OpenCode packet execution]
    environments: [OpenCode]
  use_when: [the packet execution engine contract needs reference]
  not_for: [modifying an OpenCode configuration]
class: documentation
---

# Worker Packet Execution Guide

## Core Contract

- **Packet scope** — `PURPOSE`, `DETAILS`, `FILES TO READ`, `FILES TO WRITE`, `SKILLS`, `EXECUTION INSTRUCTIONS`, `VERIFICATION`, and `EXPECTED OUTPUT` define one task.
- **Hard boundaries** — Purpose, explicit prohibitions, write scope, named-skill scope, atomicity, and task-related discovery limits remain mandatory.
- **Bounded judgment** — The worker adapts supporting actions only when required to achieve the objective within every hard boundary.
- **Payload fidelity** — `EXPECTED OUTPUT` controls the payload under `Deliverable`.
- **Result visibility** — The worker contract controls the surrounding result envelope.
- **Statelessness** — Each packet contains all state required for one independent invocation.
- **Authority** — `task-delegation` constructs the canonical ordinary packet and validates ordinary worker envelopes.
- **Execution first** — Load skills for guidance, read inputs, execute outcomes, and verify before rendering the result envelope; loading a skill is not completion.

## Packet Sections

### Purpose

- The `## PURPOSE` section defines the primary task objective and governs all execution and interpretation decisions.

### Details

- The `## DETAILS` section supplies authoritative context and facts.
- Do not invent facts or claim unsupported outcomes.
- You may use repository evidence and reversible interpretations to resolve non-material omissions.

### Files to Read

- The `## FILES TO READ` section lists required initial read targets.
- You may discover additional task-related read context when useful.
- A missing listed file blocks only when its absence materially prevents the deliverable or required verification.

### Files to Write

- The `## FILES TO WRITE` section defines the complete write boundary through literal paths or explicit bounded path patterns.
- Every dynamic output must match an authorized pattern.
- A bounded pattern must identify a directory, filename structure, and extension.
- Do not use recursive wildcards or repository-wide write patterns.
- Report each listed path according to the canonical
  `~/.config/opencode/output-contract-template.md` reconciliation contract.
- You may leave a path unchanged when verification establishes that it already satisfies the requested state.

### Skills

- The `## SKILLS` section lists every authorized skill-tool invocation.
- Load every named skill successfully.
- Do not invoke the skill tool for unlisted names.
- Apply skill-level output instructions to the `Deliverable` payload while preserving the worker result envelope.
- Translate skill-level `PARTIAL:` and `BLOCKED:` guidance into the envelope status and report fields.

### Execution Instructions

- The `## EXECUTION INSTRUCTIONS` section defines required outcomes and the default execution order.
- Supporting actions and safe reordering are allowed when correctness requires them.
- Do not omit required outcomes.

### Verification

- The `## VERIFICATION` section defines applicable quality checks.
- Report every check according to
  `~/.config/opencode/output-contract-template.md`.
- You may remediate failures within the hard boundaries.

### Expected Output

- The `## EXPECTED OUTPUT` section defines the exact shape of the payload under `Deliverable`.
- It does not suppress or replace the worker result envelope.

## Sentinel Values

- `None` identifies an explicitly empty list or non-applicable packet value.
- `UNKNOWN — not provided in input` identifies missing information.
- Neither sentinel represents a literal path or skill name.
- Unknown purpose, execution instructions, or expected output blocks before side effects.
- Unknown write or skill scope grants no authorization.
- Unknown verification produces a `NOT RUN` row for absent declared checks.

## Conflict And Ambiguity Rules

- Compatible instructions use the most specific instruction.
- Material interpretations and execution deviations appear in `Deviations`.
- Repository evidence supports reversible interpretations.
- Unresolved information or conflict produces `BLOCKED` only when it can materially alter scope, safety, externally visible behavior, irreversible output, or the requested deliverable.
- A blocked result states both the blocker and the unblock condition.

## Status Values

Status vocabulary and invariants are defined only in
`~/.config/opencode/output-contract-template.md`.

## Output Format

`~/.config/opencode/output-contract-template.md` is the sole canonical source for
the worker result envelope. Read it when producing, validating, or consuming a worker
report. This reference intentionally does not reproduce the envelope grammar.

## Consumer Contract

- `task-delegation` validates and preserves the complete worker result envelope.
- Controllers read `Status` to continue after `COMPLETE` or `PARTIAL` and stop after `BLOCKED`.
- Payload-specific consumers extract all content after `## Deliverable` and validate that content against their own contract.
- Malformed envelopes fail before payload consumption.
- Envelope parsing and reconciliation follow
  `~/.config/opencode/output-contract-template.md` without a
  local compatibility grammar.

## Docs

See `./reference/README.md` for documentation of supporting files.
