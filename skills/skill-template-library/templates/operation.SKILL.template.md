---
name: <<skill-name>>
description: "Use when <<trigger-condition>>."
selection:
  role: owner
  tags:
    actions: [<<owned-action>>]
    inputs: [<<input>>]
    outputs: [<<output>>]
    topics: [<<topic>>]
    environments: [<<environment>>]
     constraints: [<<safety boundary>>]
  aliases: [<<alias>>] # optional recognition-only wording
  use_when: [<<positive selection condition>>]
  not_for: [<<nearby request not owned>>]
class: operation
---

`aliases` is optional recognition-only metadata. Use it only for alternate wording
that should resolve to this skill's canonical `name`; it must not create another
skill, change ownership or class, or authorize routing, delegation, or loading.

# Operation Workflow

> **Editorial constraint:** Do not use Markdown tables in filled content. Use bullets
> for peer rules, ordered lists only for order-dependent procedures, paragraphs for
> connected reasoning, definition lists for term-and-definition material, and
> subsection headings for separately reviewable concerns.

## Template Slot Declarations

When instantiating this template, substitute every retained slot below using its
stated value source. Do not leave a declared slot unresolved in a filled operation
skill.

- Frontmatter values are drawn from the operation's scope, input/output contract, and
  procedure defined in this same profile:
  - `<<skill-name>>` is the canonical identifier assigned to this operation.
  - `<<trigger-condition>>` is the concise request condition under which this
    operation owns the work.
  - `<<owned-action>>` is the semantic action performed by the operation.
  - `<<input>>` and `<<output>>` are the input and produced result described by the
    same profile's input normalization and expected-output requirements.
  - `<<topic>>` is the subject matter addressed by this operation, and
    `<<environment>>` is the environment in which its procedure applies.
  - `<<safety boundary>>` is a constraint that limits the procedure's authority or
    actions.
  - `<<alias>>` is alternate recognition-only wording for the canonical skill name;
    if no alias is useful, omit the optional `aliases` field in the filled profile
    instead of retaining this slot.
  - `<<positive selection condition>>` states a positive ownership condition
    consistent with the operation's procedure and output.
  - `<<nearby request not owned>>` identifies a materially neighboring request that
    this operation does not handle.
  Substitute each retained frontmatter slot with the corresponding concrete value.
- Each `<<step>>` is one imperative action required by the concrete procedure in this
  profile; substitute every occurrence with that ordered action.
- Each `<<yes/no check>>` is a binary assertion about successful completion, derived
  from the procedure and expected output in this profile; substitute every occurrence
  with a checkable assertion.
- `<reason>` is the concrete reason a required input is missing, taken from the
  required fields and blocking conditions declared under `Normalize Input`; substitute
  that reason in the `BLOCKED` message.
- Script and argument values come from the selected script and its interface, with
  script-directory values resolved using the global/project-local order specified in
  the script instruction below:
  - `<script-entry-point>` names the same concrete script selected by the corresponding
    Python or Node command below; substitute its identifier from that command's script
    selection.
  - `<scripts-python-dir>` and `<scripts-node-dir>` are the resolved directories for
    the selected script's Python or Node script tree, respectively.
  - `<entry-point>` is the script path relative to the selected directory, supplied by
    the chosen script implementation.
  - `<args>` is the concrete argument sequence required by that entry point's declared
    interface and the normalized input. Substitute the sequence required by the
    selected script; `[args]` in the Node command remains its existing optional-argument
    notation.
- `<stderr summary>` is a concise summary of stderr captured from the script's
  non-zero exit; substitute the captured error summary in the required `BLOCKED`
  report.

## Normalize Input

Normalize invocation context into one internal input object. Specify its required
fields and defaults, and define which cases of missing required input return `BLOCKED: <reason>`.

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. `<<step>>`.
2. **Run script: `<script-entry-point>`** —
   Load `skill-architect` for path resolution rules per the global/project-local resolution order.
   - **Python script:** `uv run --project <scripts-python-dir> <entry-point> <args>`
   - **Node script:** `bun run --cwd <scripts-node-dir> <entry-point> [args]`
   Capture stdout as structured output.
   Parse output and validate against expected schema.
   On non-zero exit, report `BLOCKED: Script failed — <stderr summary>`.
3. `<<step>>`.
4. `<<step>>`.
5. `<<step>>`.

## Self-Validation

Each check is a yes/no assertion.

- <<yes/no check>>.
- <<yes/no check>>.
- <<yes/no check>>.
- [ ] Filled content uses semantic prose forms and contains no Markdown tables.

## Expected Output

Specify: artifact path/location, format, contents, and completeness criteria.
