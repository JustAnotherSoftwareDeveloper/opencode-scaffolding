---
name: skill-factory
description: "Use when creating or updating all OpenCode skill files under skills/<name>/ from requirements and source material."
schema_version: "1.0"
cues:
  - facet: operation
    value: create-or-update-skill
    primary: true
  - facet: subject
    value: OpenCode skill files
  - facet: outcome
    value: validated skill workspace
relationships:
  - role: owner
    rationale: owns skill creation and update workflows
class: operation
---

# Skill Factory

Create or update a skill workspace and validate its routing signature.

## Normalize Input

1. Determine the skill name, mode, class, requirements, and source material.
2. Load the authoring guide and relevant class, template, maintenance, and orchestration references.
3. Derive the routing signature from owned tasks and nearest competing skills.

## Procedure

1. Read `./workflow-create-update.md` in full.
2. Create or update frontmatter using the structured metadata contract.
3. Require one primary owned operation for an executable owner skill.
4. Add only cues that pass the universal routing rubric and registry resolution.
5. Preserve explicit owner, support, and reference relationships.
6. Validate every modified file with the shared schema and registry path.
7. Run the repository Markdown lint command on every modified Markdown file.

## Self-Validation

- Confirm the metadata uses structured cues and no obsolete field or rule.
- Confirm local facets and values have declarations, namespaces, aliases, hierarchy, and lifecycle status where applicable.
- Confirm routing evaluation covers owners, neighbors, unrelated tasks, paraphrases, and low-overlap requests.

## Docs

See `./workflow-create-update.md` for detailed create and update procedures.
