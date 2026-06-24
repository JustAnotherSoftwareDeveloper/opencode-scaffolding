# Trigger / Non-Trigger Eval

When composing a skill's `description`, anticipate both **positive** and **near-miss** trigger scenarios.

### Positive trigger

- The description matches requests where the skill activates.
- Phrase as: *"Use when <<action>> <<domain>> <<optional qualifier>>."*
- Be specific enough to avoid false negatives — generic descriptions cause misses.

### Near-miss negative

- The description does *not* match adjacent but unrelated requests.
- Example: A skill for *"referencing authoring style, frontmatter field rules, progressive disclosure, or trigger evaluation conventions"* does not match *"creating or updating skill files"*.
  Those are different tasks.
- Test mentally: "Would this description match a request for X?"
  If yes for the wrong X, tighten.

### Manual eval procedure

1. Write plausible user requests that trigger the skill.
2. Check if the description clearly covers them.
3. Write plausible near-miss requests that do NOT trigger.
4. Verify the description excludes them.