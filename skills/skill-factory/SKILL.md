---
name: skill-factory
description: "Use when creating or updating all OpenCode skill files under skills/<name>/ (SKILL.md, reference/, templates/, schemas/, and snippets/) from user requirements, source material."
tags: [skill-scaffolding, file-generation, frontmatter-validation, create-workflow, update-workflow, skill-maintenance]
class: operation
---

# Skill Factory

Create or update skill files under `skills/<name>/`.
Consume user requirements and source material.
Produce a validated skill artifact.

## Normalize Input

1. Determine `<name>` from context or the request.
2. Check existence of `skills/<name>/`.
   - Does not exist → mode is CREATE.
   - Exists → mode is UPDATE.
3. Determine `<class>` from requirements (CREATE) or existing frontmatter (UPDATE).
4. Derive 4–7 descriptive `<tags>` from the trigger, deliverable, domain, tools, and workflow context.
5. Preserve existing tags unless the request explicitly changes them.
6. Load `skill-architect` when class determination requires taxonomy, boundary rules, or platform layout context.
7. Gather source material: requirements, reference content, class guidance, template path.

## Procedure

1. Load relevant documentation skills based on mode and class.
   - Load `skill-authoring-guide` for editorial conventions, required frontmatter, descriptive tag selection, progressive disclosure guidance, and trigger evaluation rules.
   - Load `skill-orchestration-reference` when the target skill is orchestrated or uses delegated worker patterns.
   - Load `skill-maintenance-reference` when mode is UPDATE or when migration guidance or validation checklist items are needed.
   - Load `skill-template-library` for template selection, schema indices, and snippet indices.
2. Execute the CREATE or UPDATE workflow by reading and following `./workflow-create-update.md`.
   - Read `./workflow-create-update.md` in full before proceeding.
   - Follow the CREATE path when mode is CREATE.
   - Follow the UPDATE path when mode is UPDATE.
3. Validate all created or modified files against the validation checks in `./workflow-create-update.md#validation`.
3a. Cross-reference tags against sibling skills:
      - Run `uv run --directory ~/.config/opencode/scripts/python collect-skills` to enumerate all skills with their tags.
      - For each tag in the created/updated skill, count total occurrences across all skills.
      - Reject any tag appearing in 6+ skills total.
      - Reject any tag that is a filler value (general, helper, tool, misc, utility, etc.).
      - Ensure the tag count is between 4 and 7 (inclusive).
4. **Run automated lint check** — Invoke `bun run --cwd ~/.config/opencode/scripts/node lint:md -- <path-to-created-or-modified-file>` on all created or modified `.md` files. Address any violations before proceeding.

## Guardrails

- **Consumer-contract protection for shared convention files** — Shared convention files under `skills/<name>/reference/` (e.g., `skill-node-script-conventions`) may be referenced by consumer skills (e.g., `node-writer`, `node-test-writer`). The factory MUST NOT overwrite or delete these files without also updating all referring consumers.
- When updating or deleting any file under `skills/<name>/reference/`, cross-reference consumers by searching for references in sibling skill directories before making changes.

## Self-Validation

- All required documentation skills were loaded by name — no external file paths appear in SKILL.md or workflow-create-update.md.
- `skill-architect` was loaded when class determination needed planning guidance.
- `skill-authoring-guide` was loaded before drafting body content.
- `skill-maintenance-reference` was loaded before UPDATE path execution.
- `skill-template-library` was loaded before template selection.
- Every created or modified SKILL.md contains 4-7 descriptive tags, with no filler values, no cluster-wide duplicates (6+ occurrences), and at least one tag naming a tool or deliverable.
- All created or modified files pass the validation checklist.

## Expected Output

- `skills/<name>/SKILL.md` created (CREATE) or edited (UPDATE).
- `skills/<name>/reference/` populated (CREATE) or updated as targeted (UPDATE).
- `skills/<name>/templates/` populated (CREATE) or updated as targeted (UPDATE).
- `skills/<name>/schemas/` populated (CREATE) or updated as targeted (UPDATE).
- `skills/<name>/snippets/` populated (CREATE) or updated as targeted (UPDATE).
- `## Docs` section present at bottom of created SKILL.md referencing the skill's `reference/README.md`.
- All output passes validation checklist.

## Docs

See `./workflow-create-update.md` for the detailed CREATE and UPDATE workflow procedures.
