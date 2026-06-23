# Migration: Old Template to 7-Section Layout

Reference for converting orchestrated skills from the old template structure to the canonical 7-section layout.
See `../templates/orchestrated.SKILL.template.md` for the target structure.

## Section Mapping

| Old Section | New Section | Notes |
|---|---|---|
| Delegated Backing Skills | Execution Steps (inline) | Referenced inline as prefixed step types, not standalone. |
| Phases | Execution Steps | Phase actions become Delegated, Inline, Decompose, or Verify steps. |
| State Ownership | Worker Strategy | Dispatch model replaces ownership table. |
| Quality Gates / Checkpoints | Verification Checklist | Gate conditions become per-skill verification assertions. |
| Failure Handling | Worker Strategy (note) | Orchestrator handles failures; can note recovery hints. |
| Inline Skills (standalone) | Execution Steps (Inline:) | Convert to `Inline:` prefixed steps. |
| Verification Checklist | Self-Validation | Old checklist moved to structural self-checks. |
| Exit Criteria | Verification Checklist | Exit conditions become verification assertions. |

## Updating a Migrated Skill

When a skill has been partially migrated (some sections converted, others not) or requires targeted updates after an initial migration, follow the UPDATE path from `SKILL.md` rather than re-running the full migration.

### Incremental Checklist Application

Apply the [Migration Checklist](#migration-checklist) selectively based on what remains:

- **Old sections still present** — Remove each remaining old section (Delegated Backing Skills, Phases, State Ownership, Quality Gates, Failure Handling).
  Update section mappings per the table above.
- **New sections still missing** — Add any missing new sections (Worker Strategy, Verification Checklist, Self-Validation, Cross-References).
- **Already-converted sections** — Leave unchanged unless the request targets them for revision.

### Partial Update Verification

After a partial migration update, verify:

- [ ] All old-template sections that were targeted for removal are gone.
- [ ] New sections that were added are structurally complete.
- [ ] Unchanged sections are preserved exactly (no accidental overwrites).
- [ ] Cross-references and relative paths still resolve correctly.
- [ ] The 7-section layout is internally consistent — no duplicate section headings or misplaced content.

### Content Integrity During Partial Updates

- Apply targeted edits only to the sections the request addresses.
- Do not rewrite full files — use precise edits for minimal changes.
- Preserve any user customizations (gotchas, custom conventions) added after the original migration.

## Migration Checklist

- [ ] Remove Delegated Backing Skills section
- [ ] Remove Phases section
- [ ] Remove State Ownership section
- [ ] Remove Quality Gates / Checkpoints section
- [ ] Remove Failure Handling section
- [ ] Convert phase actions to typed Execution Steps (Delegated/Inline/Decompose/Verify)
- [ ] Add Worker Strategy section
- [ ] Update Verification Checklist for per-skill gates
- [ ] Add Self-Validation section
- [ ] Add Cross-References section
- [ ] Verify 7-section layout is complete
- [ ] Verify no old-template sections remain

## Cross-References

- `../templates/orchestrated.SKILL.template.md`
- `../orchestration/orchestrated-usage.md`
- `../authoring/frontmatter-rules.md` — Frontmatter rules and class selection.
- `./update-workflow.md` — Update workflow reference.