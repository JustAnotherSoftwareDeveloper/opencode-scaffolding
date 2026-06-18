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
| Failure Handling | Worker Strategy (note) | Orchestrator handles failures; may note recovery hints. |
| Inline Skills (standalone) | Execution Steps (Inline:) | Convert to `Inline:` prefixed steps. |
| Verification Checklist | Self-Validation | Old checklist moved to structural self-checks. |
| Exit Criteria | Verification Checklist | Exit conditions become verification assertions. |

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
- `./orchestrated-usage.md`
- `../REFERENCE.md`