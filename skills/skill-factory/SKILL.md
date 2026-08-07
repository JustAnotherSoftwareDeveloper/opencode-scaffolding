---
name: skill-factory
description: "Use when creating or updating all OpenCode skill files under skills/<name>/ from requirements and source material."
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
    - creating or updating the files of a skill under skills/<name>/
  not_for:
    - maintaining guidance without changing a skill workspace
class: operation
---

# Skill Factory

Create or update a skill workspace and validate its direct-selection profile.

## Normalize Input

1. Determine the skill name, mode, class, requirements, and source material.
2. Load authoring guidance and the relevant class and maintenance references; use template guidance separately when needed.
3. Derive the profile from the owned request, inputs, outputs, and nearest competitors.

## Procedure

1. Read `./reference/workflow-create-update.md` in full.
2. Create or update only `name`, `description`, `selection`, and `class` frontmatter, plus supported profile fields only when explicitly required.
3. Set `selection.role` and grouped tags from the request contract; add concise `use_when`, `not_for`, or directional `supports` values only when they improve selection.
4. Preserve the skill body and update all relevant examples or evaluation cases with the profile.
5. Validate every changed `SKILL.md` with the shared profile validator before handoff.
6. Run the repository Markdown lint command on every modified Markdown file.

## Self-Validation

- Confirm the metadata contains exactly the current profile shape: `name`, `description`, `selection`, and `class`, with no obsolete routing fields.
- Confirm tags are grouped by request-facing actions, inputs, outputs, topics, environments, or constraints and are the smallest sufficient set.
- Confirm `use_when` and `not_for` distinguish owned requests from neighboring requests without scoring, ranking, path, registry, or compatibility guidance.
- Confirm the shared validator passes before declaring the workspace complete.

## Docs

See `./reference/workflow-create-update.md` for detailed create and update procedures.
