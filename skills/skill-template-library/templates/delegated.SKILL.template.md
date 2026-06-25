---
name: <<skill-name>>
description: "Use when <<trigger condition>>."
class: delegated
---

# <<Skill Name>> — Delegated Worker

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
- **`## FILES TO READ`** — Every file listed must be read before producing output.
  Missing or inaccessible files are blockers.
- **`## FILES TO WRITE`** — Only files in this list may be modified or created.
  All listed files must be written unless blocked.
- **`## SKILLS`** — Skill names to load for specialized instructions.
  Unknown or missing skills are blockers.
- **`## EXECUTION INSTRUCTIONS`** — Step-by-step instructions the worker must follow in order.
  A failure at any step blocks the task.
- **`## VERIFICATION`** — Checks the worker must run against its own output before finishing.
  Fix issues if possible.
- **`## EXPECTED OUTPUT`** — Defines the deliverable format and content.
  The worker must produce exactly this and nothing more.

## Execution Steps

1. Parse input contract from delegation packet.
2. Perform bounded work.
   If the work includes a deterministic subtask:
   a. Prepare input for the script (file path, CLI arguments, or stdin).
   b. Resolve `<scripts-python-dir>` per `platform-layout-context.md` and invoke `uv run --directory <scripts-python-dir> <entry-point> <args>`.
   c. Capture and validate stdout output.
   d. On non-zero exit, return `BLOCKED: <script-name> failed — <stderr>`.
3. Produce output per Output Contract below.
4. Self-validate using the packet's `## VERIFICATION` instructions and the template's `## Verification` section.
5. Return exactly what the packet's `## EXPECTED OUTPUT` requests, following the template's `## Output Contract`.

## Output Contract

The delegation packet's `## EXPECTED OUTPUT` is the sole authority for what the worker returns.
The worker must produce exactly what that section specifies, in the format it specifies, without wrapping the result in extra sections, metadata, status markers, or explanatory framing.

**Format rules:**
- **Default format is plaintext.**
  If `## EXPECTED OUTPUT` does not explicitly request a specific format (e.g., JSON, structured sections), the worker returns plaintext and nothing more.
- **No wrapping.**
  Do not add a `Summary`, `Deliverables`, `Status`, or any other wrapper section unless `## EXPECTED OUTPUT` itself calls for them.
- **Missing or ambiguous `## EXPECTED OUTPUT`.**
  If the section is absent or its intent cannot be determined, the worker must use CLARIFY rather than inventing a format or guessing the deliverable.
- **Silence is success.**
  A clean return of the requested deliverable signals completion.
  Do not append a status message unless the packet explicitly asks for one.

## Verification

- Artifact exists at expected path.
- Content contains required elements.
- No failure markers.

## Guardrails

- Do not invent facts.
  If information is missing, state it as an assumption; if the assumption is critical to correctness, use CLARIFY.
- Work only within supplied files and instructions.
- Do not edit files outside `## FILES TO WRITE`.
- Prefer the simplest sufficient approach.
- Report blockers as `BLOCKED: <reason>` when contradictions or missing dependencies prevent completion.

## Cross-References

- `./platform-layout-context.md` — Path resolution rules for script invocations.
- `../../skill-template-library/templates/inline.SKILL.template.md` — Inline skill template for single-pass steps.
- `../../skill-template-library/templates/orchestrated.SKILL.template.md` — Orchestrated skill template for multi-step coordination.
