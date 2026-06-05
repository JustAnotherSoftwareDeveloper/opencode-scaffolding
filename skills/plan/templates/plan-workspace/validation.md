id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: "../../.proposals/<timestamp>-<proposal-slug>/INDEX.md"
---

# Validation & Checkpoints

## Pre-Execution Gates (Plan Approval)

- [ ] All required files present with frontmatter matching proposal reference.
- [ ] `execution-overview.md` goal aligns with accepted proposal.
- [ ] No executable runbook XML/state in any markdown file.

### Commands to Verify Template Compliance

```bash
# Check for prohibited sections (should return nothing)
grep -rE "problem-opportunity|alternatives-considered|risks-and-unknowns" . --include="*.md" || echo "OK: no proposal-style rationale found"

# List required files exist
ls INDEX.md metadata.md source.md execution-overview.md constraints.md \
   file-impact.md validation.md rollback-recovery.md handoff.md \
   steps/01-implementation.md
```

## Execution Checkpoints

| Step | Checkpoint Command | Expected Result | Pass/Fail |
|------|-------------------|-----------------|-----------|
| `steps/01-implementation` | `<command>` | `<expected output>` | ☐ |

### Manual Verification Items

- [ ] Review file changes in scope before modification.
- [ ] Confirm rollback strategy works by dry-run.