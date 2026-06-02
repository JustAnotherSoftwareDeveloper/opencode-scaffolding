# Skill/File Routing

Map each file or workstream to the skill guidance an executor should use. This is a planning artifact: do not select permanent worker tiers here. During execution, load `delegation` to select the smallest capable configured worker for each atomic unit.

| File / Workstream | Skill to load | How to use it | Do not use it for |
| --- | --- | --- | --- |
| `skills/<name>/SKILL.md` | `skill-hygiene` when changing skill frontmatter, class metadata, trigger description, or framework-owned structure | Check naming, description, class contract, concision, and validation requirements. | Do not redesign unrelated skills. |
| Proposal interpretation | `proposal` as reference | Preserve accepted decisions, scope boundaries, and acceptance criteria. | Do not reopen proposal decisions unless a blocker is found. |
| Runbook handoff | `runbook` after plan approval | Convert this plan into executable XML steps and state initialization guidance. | Do not execute implementation while planning. |
| Delegated execution | `delegation` during runbook execution | Select worker size dynamically and build bounded handoff packets. | Do not hardcode static worker tiers in this plan. |
| Embedded review | `review-work` | Review completed changes for correctness, prompt quality, validation, and permission safety. | Do not turn review into new scope. |

## Anti-Patterns

- **Avoid**: "Update docs" without naming files, skill guidance, expected output, and validation.
- **Avoid**: Treating plan workspaces as executable runbooks or state stores.
- **Avoid**: Copying external frameworks wholesale when a native OpenCode skill/runbook handoff is sufficient.
- **Avoid**: Hardcoding a worker size where `delegation` should evaluate the actual atomic unit.
