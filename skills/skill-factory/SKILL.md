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
   Use `skill-authoring-guide -> reference/cross-references.md` for shared pointers;
   reading a skill's `SKILL.md` never replaces its skill-tool load.
   Load relevant class and maintenance references; use template guidance separately
   when needed. The guide owns authoring policy; these references do not replace this
   factory workflow.
3. Derive the profile from the owned request, inputs, outputs, and nearest competitors,
   applying `skill-authoring-guide -> reference/tagging-guide.md` and
   `skill-authoring-guide -> reference/trigger-evaluation.md`.

## Procedure

1. Read `./reference/workflow-create-update.md` in full and confirm the request is limited to one workspace.
2. Create or update only `name`, `description`, `selection`, and `class` frontmatter, plus supported profile fields only when explicitly required; follow `skill-authoring-guide -> reference/frontmatter-rules.md`.
3. Apply `skill-authoring-guide -> reference/tagging-guide.md` and `skill-authoring-guide -> reference/trigger-evaluation.md` when deriving grouped tags and selection conditions from the request contract.
4. Preserve the skill body and update all relevant examples or evaluation cases with the profile.
5. Apply `skill-authoring-guide -> reference/authoring-style.md` and `skill-authoring-guide -> reference/progressive-disclosure.md` to changed filled content, including semantic form and `TABLE-001` policy.
6. Validate every changed `SKILL.md` with the shared profile validator before handoff.
7. Run the repository Markdown lint command on every modified Markdown file.
8. Perform a separate human review of semantic form choice; lint does not establish
   prose clarity, comprehension, navigation quality, or task success.

Family migration is a workflow applied as bounded updates through this operation;
there is no standalone migration operation. Taxonomy, ownership policy, review, and
passive reference authority belong to their canonical owners.

## Self-Validation

- Review the profile against `skill-authoring-guide -> reference/frontmatter-rules.md`, `skill-authoring-guide -> reference/tagging-guide.md`, and `skill-authoring-guide -> reference/trigger-evaluation.md`; correct profile discrepancies in the target workspace. Report canonical-policy conflicts without changing the guide under this task.
- Review changed filled content against `skill-authoring-guide -> reference/authoring-style.md` and `skill-authoring-guide -> reference/progressive-disclosure.md`, including semantic form and `TABLE-001`.
- Confirm deterministic lint evidence remains separate from human clarity judgment.
- Confirm the shared validator passes before declaring the workspace complete.

## Docs

See `./reference/workflow-create-update.md` for detailed create and update procedures.
