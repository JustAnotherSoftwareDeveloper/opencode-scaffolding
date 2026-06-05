id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: "../../.proposals/<timestamp>-<proposal-slug>/INDEX.md"
---

# Rollback & Recovery

## Strategy Overview

If execution fails partway through, use these instructions to return the workspace to a known-good state or minimize impact.

## By File Change Type

| Action | Detection Command | Recovery Step |
|--------|------------------|---------------|
| Modified file | `git diff --name-only` shows `<path>` | `git checkout <path>` |
| Created directory | Directory exists at `<path>` | `rm -rf <path>` if validation rejects it |
 | Deleted file | Git history has deletion of `<path>` | `git restore <path>` or revert commit |

## Checkpoint Undo Points

- Before Step 01: Verify plan approval status.
- After each phase: Confirm success before proceeding; failure → rollback to last checkpoint.

### Emergency Commands

```bash
# Restore all working tree files to HEAD (nuclear option)
git checkout -- .
# Or restore specific files
git restore <path>
```