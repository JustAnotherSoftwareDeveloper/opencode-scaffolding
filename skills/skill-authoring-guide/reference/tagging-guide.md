# Grouped Selection Tags

Write tags as answers to six selection questions. Use only groups that improve a
decision; do not fill every group.

- `actions`: What does the skill do?
- `inputs`: What does it receive or inspect?
- `outputs`: What does it produce?
- `topics`: What subject or artifact does it concern?
- `environments`: Where does the request apply?
- `constraints`: What condition materially changes ownership?

Start with the owned request and its input/output contract. Then list the nearest
neighboring skills and the requests they own. Keep a tag only when changing or
removing it could change selection. Prefer request vocabulary over implementation
details.

## Conditions And Aliases

Use `use_when` for plain-language conditions that make the profile applicable. Use
`not_for` for conditional near-misses, not as a second tag list. Use a small number of
global aliases in tags or conditions when authors and users use different words; an
alias must identify the same concept, not create a second concept.

Use `supports` directionally for skills this skill directly supports. Do not use it to
express similarity, ownership, or a general relatedness list.

## Stop Rules

Stop when the profile distinguishes its nearest neighbors. Reject tags that merely
repeat the skill name, describe a shared implementation detail, fill an unused group,
or name a one-off ticket. Do not use popularity, frequency, ranking, scores, paths,
or compatibility/routing metadata to select a skill.

## Example

For a skill that creates deterministic Python CLI scripts from requirements:

```yaml
selection:
  role: owner
  tags:
    actions: [create]
    inputs: [script requirements]
    outputs: [Python CLI script]
    constraints: [deterministic]
  not_for:
    - writing tests for an existing Python script
```

The testing neighbor should own the changed action and output. Do not add `python`
merely because both skills use Python.
