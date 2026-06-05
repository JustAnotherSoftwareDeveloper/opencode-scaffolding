id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: "../../.proposals/<timestamp>-<proposal-slug>/INDEX.md"
---

# Handoff Guidance

**Optional transition notes for the next owner or runbook conversion.** Include only if non-obvious routing decisions need clarification beyond what's in `steps/`.

## To Runbook Skill Owner

- Load order: validation → rollback-recovery → steps/* files.
- Worker sizing guidance (use delegation): <specific unit estimates>.
- Open questions blocked on external input: none / <list>.

### Context Package Contents

Include the following supporting files when converting this plan to a runbook:

1. `source.md` — accepted proposal link and decision summary
2. `constraints.md` — prerequisites and sequencing rules
3. `validation.md` — checkpoint verification commands
4. `rollback-recovery.md` — undo procedures