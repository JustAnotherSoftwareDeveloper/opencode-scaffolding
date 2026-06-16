# Description Trigger Evals

The `description` field is the primary signal an agent sees before loading a skill. Optimize it like a router rule.

## Description Pattern

Start with concrete trigger words and the use boundary:

```text
Use when creating or reviewing OpenCode skills, SKILL.md files, skill trigger descriptions, skill schemas, or skill validation rules.
```

Prefer:

- File names or domains users will mention (`SKILL.md`, `skills/`, `opencode.json`).
- Verbs that match user intent (`create`, `review`, `validate`, `migrate`).
- Boundaries (`Use ONLY when...`) for narrow or risky skills.

Avoid:

- Vague benefits (`helps improve quality`).
- Personality or role claims.
- Long lists where key trigger terms appear late.

## Eval Set

For each skill, maintain at least informal eval queries:

### Positive examples

- User asks to create the exact artifact.
- User asks to review or validate the artifact.
- User mentions a known file path or domain term.

### Near-miss negatives

- User asks about adjacent application code.
- User asks for generic explanation that does not need the skill.
- User asks for a different harness artifact.

## Iteration Loop

1. Run the positive and near-miss prompts mentally or with a reviewer.
2. If the skill would load too often, narrow the description.
3. If the skill would not load for core work, front-load stronger trigger terms.
4. Re-check after real execution traces or review findings.
