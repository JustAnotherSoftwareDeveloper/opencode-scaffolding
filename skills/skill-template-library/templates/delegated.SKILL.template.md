---
name: <<skill-name>>
description: "Use when <<trigger condition>>."
selection:
  role: owner
  tags:
    actions: [execute, verify]
    inputs: [delegation packet]
    outputs: [bounded deliverable]
    topics: [<<task subject>>]
    environments: [OpenCode worker]
     constraints: [declared files, declared skills]
  aliases: [<<alias>>] # optional recognition-only wording
  use_when: [an orchestrator delegates <<owned-operation>>]
  not_for: [interactive orchestration or unbounded discovery]
class: delegated
---

`aliases` is optional recognition-only metadata. Use it only for alternate wording
that should resolve to this skill's canonical `name`; it must not create another
skill, change ownership or class, or authorize routing, delegation, or loading.

# Delegated Worker

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

> **Template slot declarations (remove this authoring-only note after substitution):** Before instantiating this template, replace every retained slot below with its concrete value from the stated source; no slot marker may remain in the filled skill.
> - `<<skill-name>>` is the canonical skill name, sourced from the lowercase, hyphenated skill directory name; use the same value for the frontmatter `name` field.
> - `<<trigger condition>>` is the orchestrator-side situation that should select this delegated skill, sourced from the intended delegation trigger and phrased from the orchestrator's perspective.
> - `<<task subject>>` is the subject of the bounded operation this worker owns, sourced from its intended scope.
> - `<<alias>>` is an optional alternate phrase that should resolve to the canonical `name`, sourced from recognition wording relevant to that skill. Substitute a recognition-only alias when one is useful; otherwise omit the optional `aliases` field rather than leaving the slot unresolved.
> - `<<owned-operation>>` is the specific operation this skill owns, sourced from the operation the orchestrator will delegate.
> - `<scripts-python-dir>` is the concrete Python scripts root resolved for the skill's project/global origin, or the `$OPENCODE_SCRIPTS_PYTHON` override, following `skill-architect` path-resolution rules.
> - `<scripts-node-dir>` is the concrete Node scripts root resolved for the skill's project/global origin, or the `$OPENCODE_SCRIPTS_NODE` override, following `skill-architect` path-resolution rules.
> - `<entry-point>` is the deterministic subtask's script entry point: for Python, the command registered in that scripts root's `pyproject.toml [project.scripts]`; for Node, the selected CLI script under `scripts/node/src/cli/`.
> - `<args>` is the concrete CLI argument sequence needed to provide the prepared subtask input from step 2a (such as a file path or other CLI values); use no argument tokens when the selected script requires none.
> Replace command slots in place while preserving the `uv run --project` and `bun run --cwd` invocation forms and the separate `[args]` optional-argument notation.

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

1. Parse the eight-section input contract and sentinel values from the delegation packet.
2. Load declared skills, read required inputs, and perform bounded work. Loading a skill is context acquisition, not completion.
   If the work includes a deterministic subtask:
a. Prepare input for the script (file path, CLI arguments, or stdin).
    b. Load `skill-architect` for path resolution rules to resolve `<scripts-python-dir>` or `<scripts-node-dir>`.
       - **Python script:** `uv run --project <scripts-python-dir> <entry-point> <args>`
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
   Preserve the envelope defined by
   `~/.config/opencode/output-contract-template.md`; do not reproduce or vary its
   grammar in the skill.
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
