---
name: <<skill-name>>
description: "Use when <<trigger condition>>."
tags:
  - <<primary-capability>>
  - <<domain-or-artifact>>
  - <<tool-or-workflow-context>>
  - <<additional-discriminator>>
class: delegated
---

# `<<Skill Name>>` — Delegated Worker

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

One-line summary of what this worker accomplishes.

*(Skill directory name must be lowercase with hyphens, matching `name` field.
The description captures the orchestrator's trigger perspective.)*

## Input Contract (from Delegation Packet)

The delegation packet is the authoritative source of truth for a worker invocation.
Each header defines a specific dimension of the task:

- **`## PURPOSE`** — One-sentence task summary.
  The worker reads this first to understand what must be done.
- **`## DETAILS`** — Primary context, constraints, and background.
  The worker must not invent facts beyond what is here.
- **`## FILES TO READ`** — Every available listed file must be read before producing output.
  Missing files block only when their absence materially prevents the deliverable or required verification.
- **`## FILES TO WRITE`** — Only literal paths or bounded path patterns in this list may be modified or created.
  Bounded patterns identify a directory, filename structure, and extension without recursive wildcards.
  Already-compliant files remain unchanged and appear in the worker result.
- **`## SKILLS`** — Skill names to load for specialized instructions.
  `None` authorizes no skills; unknown skill scope grants no authorization and blocks only when execution requires a skill.
- **`## EXECUTION INSTRUCTIONS`** — Required outcomes and their default order.
  Supporting actions and safe reordering remain permitted within hard boundaries.
- **`## VERIFICATION`** — Checks the worker must run against its own output before finishing.
  Fix issues if possible.
- **`## EXPECTED OUTPUT`** — Defines the `Deliverable` payload format and content.
  The worker result envelope remains mandatory.

## Execution Steps

1. Parse input contract from delegation packet.
2. Perform bounded work.
   If the work includes a deterministic subtask:
a. Prepare input for the script (file path, CLI arguments, or stdin).
    b. Load `skill-architect` for path resolution rules to resolve `<scripts-python-dir>` or `<scripts-node-dir>`.
       - **Python script:** `uv run --directory <scripts-python-dir> <entry-point> <args>`
       - **Node script:** `bun run --cwd <scripts-node-dir> <entry-point> [args]`
    c. Capture and validate stdout output.
   d. On non-zero exit, return `BLOCKED` envelope status with the script failure and unblock condition.
3. Produce the payload per Output Contract below.
4. Self-validate using the packet's `## VERIFICATION` instructions and the template's `## Verification` section.
5. Place exactly what the packet's `## EXPECTED OUTPUT` requests under `Deliverable` in the worker result envelope.

## Output Contract

The delegation packet's `## EXPECTED OUTPUT` is the sole authority for the `Deliverable` payload.
The worker agent contract remains the authority for the surrounding result envelope.

**Format rules:**

- **Default payload format is plaintext.**
  If `## EXPECTED OUTPUT` does not request a specific format, place plaintext under `Deliverable`.
- **Mandatory envelope.**
  Preserve `Worker Result`, `File Changes`, `Verification`, and `Deliverable` in the order required by the worker agent contract.
- **Missing or ambiguous `## EXPECTED OUTPUT`.**
  Return `BLOCKED` envelope status when the payload contract cannot be determined without a material assumption.
- **Explicit status.**
  Return `COMPLETE`, `PARTIAL`, or `BLOCKED` through the worker result envelope.
- **Legacy skill guidance.**
  Translate skill-level `PARTIAL:` or `BLOCKED:` instructions into envelope status and report fields.

## Verification

- Artifact exists at expected path.
- Content contains required elements.
- No failure markers.
- [ ] No Markdown tables in filled content (use bullet lists instead).

## Guardrails

- Do not invent facts.
  Record non-material assumptions as deviations and return `BLOCKED` when a material fact remains unavailable.
- Work only within supplied files and instructions.
- Do not edit files outside `## FILES TO WRITE`.
- Prefer the simplest sufficient approach.
- Report blockers through `BLOCKED` envelope status with blocker and unblock-condition fields.

## Cross-References

- Load `skill-architect` for path resolution rules for script invocations.

## Docs

See `./reference/README.md` for documentation of supporting files.
