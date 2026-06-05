id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: "../../.proposals/<timestamp>-<proposal-slug>/INDEX.md"
---

# Step 01: Implementation

## Purpose

<State what this step accomplishes in one clear sentence. This is the objective for anyone reading, from senior to intern.>

Example: Update the Plan Skill contract documentation to match the required execution-focused artifact structure.

## Files In Scope

- `skills/plan/SKILL.md` — Contains outdated frontmatter/examples that need alignment
- `<other files>` — As specified in file-impact.md

## Actions

1. **Edit SKILL.md Section 4–6**   <Brief description of what to change>
    - Locate the "Plan Artifact Contract" section header
    - Update any deprecated examples or references to old taxonomy
    - Ensure all required files are documented correctly

2. **Run Validation Commands**
    ```bash
    # Check for legacy references that should be removed
    grep -rE "schema_version|init-.*state|\.plans/.*\.json" skills/plan/ || echo "OK: no deprecated patterns found"
    
    # Verify the plan template directory structure
    ls skills/plan/templates/plan-workspace/steps/01-implementation.md
    ```

## Expected Observations

<Describe what a successful outcome looks like after completing each action.>

- Grep for legacy references returns zero matches or "OK: no deprecated patterns found"
- `steps/01-implementation.md` exists and contains the required sections
- All edits maintain valid markdown with frontmatter intact

## Common Mistakes & How to Avoid Them

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Editing without reading full context first | Missing dependencies or incorrect changes | Always read linked files before editing |
| Forgetting YAML frontmatter format | Plan validator may reject the file | Use existing template as reference for exact format |
| Hardcoding worker size instead of using `delegation` skill guidance | Wrong execution tier picked later | Note in handoff that delegation should choose smallest capable worker |

## Completion Criteria (Pass/Fail)

✅ **PASS if all conditions met:**

- [ ] Every required template file exists with correct frontmatter
- [ ] No instances of `problem-opportunity`, `alternatives-considered`, or `risks-and-unknowns` in any artifact
- [ ] `steps/01-implementation.md` contains Purpose, Files In Scope, Actions, Expected Observations, Common Mistakes, Completion Criteria
- [ ] Grep for prohibited legacy patterns returns zero matches

❌ **FAIL:** Any unchecked criterion above. Review and re-run validation before proceeding.