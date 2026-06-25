---
name: <<skill-name>>
description: "Use when <<trigger description for multi-phase coordination>>."
class: orchestrated
---

# <<Skill Name>>

<<One-line description of the workflow this orchestrator coordinates.>>

## Execution Steps

1. **Delegated: <<Worker Skill A>>** — <<purpose of delegation>>.
2. **Script: <<entry-point>>** — <<what the script computes>>.
   Resolve `<scripts-python-dir>` per the global/project-local resolution order (see platform-layout-context.md).
   Run `uv run --directory <scripts-python-dir> <entry-point> [args]`.
   Validate structured output before proceeding.
3. **Inline: <<Inline Skill Name>>** — <<what this inline step does in a single pass>>.
4. **Decompose** — <<what to decompose into sub-packets>>.
5. **Delegated: <<Worker Skill B>>** — <<purpose of delegation>>.
6. **Verify** — <<what to verify>>.

## Worker Strategy

- <<dispatch model: parallel fan-out / sequential pipeline / conditional branching>>.
- <<concurrency limits and data flow between steps>>.

## Verification Checklist

- <<verification assertion that a worker must pass>>.
- <<verification assertion that a worker must pass>>.

## Self-Validation

- Name matches directory name.
- Description starts with "Use when".
- Class is `orchestrated`.
- All `<<placeholders>>` are replaced.
- No remaining old-template sections.
- One H1 only; all headings use Title Case.
