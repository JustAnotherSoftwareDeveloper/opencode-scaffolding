# Migration Guide: Old Monolithic skill-writer to Decomposed Structure

Reference for migrating skills from the old monolithic `skill-writer` structure to the new decomposed skill layout with separate planning, documentation, and operation skills.

## Background

The `skill-writer` skill was originally a single monolithic skill handling architectural planning, authoring-style guidance, orchestration-pattern documentation, maintenance workflows, template management, and file-level create/update operations. It has been decomposed into six focused skills:

| # | Skill | Class | Purpose |
|---|-------|-------|---------|
| 1 | **skill-architect** | planning | Class taxonomy, class decision flow, class boundary rules, platform layout/context |
| 2 | **skill-authoring-guide** | documentation | Authoring style, frontmatter field rules, progressive disclosure, trigger evaluation |
| 3 | **skill-orchestration-reference** | documentation | Orchestrated/delegated worker patterns, collation format, orchestration usage |
| 4 | **skill-maintenance-reference** | documentation | Update workflow, migration guide, validation checklist, gotchas |
| 5 | **skill-template-library** | documentation | All skill templates, common workflow template, schemas/snippets indices |
| 6 | **skill-factory** | operation | Actual CREATE/UPDATE workflow for skills |

## Section Mapping: Monolithic to Decomposed

| Old Monolithic Section | New Decomposed Location | Notes |
|---|---|---|
| Platform Context | `skill-architect/platform-layout-context.md` | Planning-level content moved to architect skill. |
| Class Taxonomy & Decision Flow | `skill-architect/class-taxonomy.md`, `skill-architect/class-decision-flow.md` | Class definitions separated into dedicated planning skill. |
| Authoring Style & Frontmatter Rules | `skill-authoring-guide/authoring-style.md`, `skill-authoring-guide/frontmatter-rules.md` | Editorial conventions in dedicated documentation skill. |
| Orchestration Patterns | `skill-orchestration-reference/orchestrated-worker-patterns.md` | Orchestration reference in dedicated skill. |
| Update Workflow | `skill-maintenance-reference/update-workflow.md` | Maintenance reference in this skill. |
| Migration Procedures | `skill-maintenance-reference/migration-guide.md` | Migration guide in this skill. |
| Validation Checklist | `skill-maintenance-reference/validation-checklist.md` | Validation checks in this skill. |
| Gotchas | `skill-maintenance-reference/gotchas.md` | Known pitfalls in this skill. |
| Templates | `skill-template-library/templates/` | Template library in dedicated skill. |
| CREATE/UPDATE Operations | `skill-factory/workflow-create-update.md` | Operational workflow in dedicated skill. |

## Updating a Partially Migrated Skill

When a skill has been partially migrated (some content converted to the new structure, others not) or requires targeted updates after an initial migration, follow the UPDATE path from the update workflow reference rather than re-running the full migration.

### Incremental Checklist Application

Apply the [Migration Checklist](#migration-checklist) selectively based on what remains:

- **Old monolithic sections still present** — Remove each remaining old section (Platform Context, Class Decisions, Authoring Style blocks embedded in operation workflows, etc.).
  Move content to the appropriate decomposed skill per the section mapping table above.
- **New decomposed files still missing** — Add any missing new files (the six target skill directories with their entry-point SKILL.md files).
- **Already-converted sections** — Leave unchanged unless the request targets them for revision.

### Partial Update Verification

After a partial migration update, verify:

- [ ] All old monolithic sections that were targeted for removal are gone.
- [ ] New decomposed files that were added are structurally complete.
- [ ] Unchanged sections are preserved exactly (no accidental overwrites).
- [ ] Cross-references and relative paths still resolve correctly within each skill's directory.
- [ ] No hard-coded cross-skill file paths exist (use skill loading instead).

### Content Integrity During Partial Updates

- Apply targeted edits only to the sections the request addresses.
- Do not rewrite full files — use precise edits for minimal changes.
- Preserve any user customizations (gotchas, custom conventions) added after the original migration.

## Migration Checklist

- [ ] Remove old monolithic SKILL.md with combined planning/authoring/operation content
- [ ] Remove old `reference/` directory with mixed concerns
- [ ] Remove old `templates/` directory (moved to skill-template-library)
- [ ] Create `skill-architect/` with planning content
- [ ] Create `skill-authoring-guide/` with authoring content
- [ ] Create `skill-orchestration-reference/` with orchestration content
- [ ] Create `skill-maintenance-reference/` with maintenance content
- [ ] Create `skill-template-library/` with template content
- [ ] Create `skill-factory/` with operational workflow
- [ ] Verify each new skill's SKILL.md has valid frontmatter (name, description, class)
- [ ] Verify documentation-class skills have a file index in SKILL.md
- [ ] Verify no cross-skill file path references exist (use skill loading only)
- [ ] Verify scripts are the only exception to directory confinement

## Cross-References

- `./update-workflow.md` — Update workflow reference.
- `./validation-checklist.md` — Validation and manual checklist guidance.
- `./gotchas.md` — Common pitfalls and gotchas.