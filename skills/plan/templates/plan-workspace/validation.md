# Validation & Gates

## Pre-Approval Validation

- [ ] `INDEX.md` has every required section from the plan skill.
- [ ] Supporting files linked from `INDEX.md` exist.
- [ ] File scopes are concrete and bounded.
- [ ] Skill/file routing aligns with `skill-map.md`.
- [ ] The plan does not contain executable runbook XML/state.

## Post-Execution Verification

- [ ] All planned artifact changes were made or explicitly skipped with rationale.
- [ ] Required command checks ran and results are recorded.
- [ ] Embedded `review-work` completed and findings were reconciled.
- [ ] No sensitive information was introduced.
- [ ] Links in `INDEX.md` remain valid.

## Rollback / Recovery

| Change | Recovery |
| --- | --- |
| Modify `<file>` | Restore from git or revert the specific section. |
| Create `<directory>` | Delete the directory if review rejects it. |
| Delete `<file>` | Restore from git if validation finds an active dependency. |
