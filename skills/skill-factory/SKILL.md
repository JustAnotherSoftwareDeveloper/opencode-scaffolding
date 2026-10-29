---
name: skill-factory
description: "Use when creating or updating one OpenCode skill workspace from requirements and source material."
selection:
  role: owner
  tags:
    actions:
      - create skill
      - update skill
    inputs:
      - skill requirements
      - source material
    outputs:
      - validated skill workspace
    topics:
      - OpenCode skills
    constraints:
      - direct selection profile
  use_when:
    - creating or updating one selected skill workspace under skills/<name>/
  not_for:
    - reviewing one existing skill, migrating a family, choosing taxonomy, or maintaining passive guidance
class: operation
---

# Skill Factory

Create or update one skill workspace and validate its direct-selection profile.

## Normalize Input

1. Determine the skill name, mode, class, requirements, and source material.
2. Load `skill-authoring-guide` and read its relevant canonical references for
   frontmatter, tags, authoring style, trigger evaluation, and progressive disclosure.
   Use `skill-authoring-guide -> reference/cross-references.md` for shared pointers.
   Reading a skill's `SKILL.md` never replaces its skill-tool load.
   Load relevant class and maintenance references; use template guidance separately
   when needed. The guide owns authoring policy; these references do not replace this
   factory workflow. When authoring or substantively revising filled Markdown prose in
   the one selected workspace, apply the shared guide only where compatible with
   `skill-authoring-guide`, applicable class templates and profile policy,
   semantic-form and `TABLE-001` rules, disclosure limits, and the local artifact
   contract. For direct use outside canonical-packet execution, load
   `markdown-writing-guide` and read
   `markdown-writing-guide -> reference/writing-quality.md` before drafting. For
   canonical packets, read that reference before drafting only when
   `markdown-writing-guide` is explicitly assigned and successfully loaded. Do not
   self-load an undeclared guide; have the task author resolve its fit within the
   packet's two-documentation-skill maximum.
3. Derive the profile from the owned request, inputs, outputs, and nearest competitors,
   applying `skill-authoring-guide -> reference/tagging-guide.md` and
   `skill-authoring-guide -> reference/trigger-evaluation.md`.

## Procedure

1. Read `./reference/workflow-create-update.md` in full. Confirm the request is
   limited to one workspace.
2. Create or update only the `name`, `description`, `selection`, and `class`
   frontmatter fields. Add supported profile fields only when explicitly required.
   Follow `skill-authoring-guide -> reference/frontmatter-rules.md`.
3. Apply `skill-authoring-guide -> reference/tagging-guide.md` and `skill-authoring-guide -> reference/trigger-evaluation.md` when deriving grouped tags and selection conditions from the request contract.
4. Preserve the skill body. Update all examples or evaluation cases relevant to the
   profile.
5. For changed filled content, apply `skill-authoring-guide -> reference/authoring-style.md`
   and `skill-authoring-guide -> reference/progressive-disclosure.md`, including
   semantic form and `TABLE-001` policy.
6. Before handoff, validate every changed `SKILL.md` with the shared profile validator.
7. Run the repository's Markdown lint command on every modified Markdown file.
8. Perform a separate human review of semantic form choice; lint does not establish
   prose clarity, comprehension, navigation quality, or task success.

Family migration is a workflow applied as bounded updates through this operation;
there is no standalone migration operation. Taxonomy, ownership policy, review, and
passive reference authority belong to their canonical owners.

## Self-Validation

- Review the profile against `skill-authoring-guide -> reference/frontmatter-rules.md`,
  `skill-authoring-guide -> reference/tagging-guide.md`, and
  `skill-authoring-guide -> reference/trigger-evaluation.md`. Correct profile
  discrepancies in the target workspace. Report canonical-policy conflicts without
  changing the guide under this task.
- Review changed filled content against `skill-authoring-guide -> reference/authoring-style.md`
  and `skill-authoring-guide -> reference/progressive-disclosure.md`, including
  semantic form and `TABLE-001`.
- Keep deterministic lint evidence separate from human clarity judgment.
- Confirm the shared validator passes before declaring the workspace complete.

## Docs

See `./reference/workflow-create-update.md` for detailed create and update procedures.
