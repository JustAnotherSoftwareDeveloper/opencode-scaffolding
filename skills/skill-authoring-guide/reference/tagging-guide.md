# Grouped Selection Tags

Use the six tag groups to answer selection questions, but include a group only when it
helps distinguish the skill. Do not fill every group.

- `actions`: What does the skill do?
- `inputs`: What does it receive or inspect?
- `outputs`: What does it produce?
- `topics`: What subject or artifact does it concern?
- `environments`: Where does the request apply?
- `constraints`: What condition materially changes ownership?

Start with the request the skill owns and its input/output contract. Identify the
nearest neighboring skills and the requests they own. Keep a tag only if changing or
removing it could change skill selection. Prefer request wording to implementation
details. Keep each value atomic: one concept per value. Test discoverability with
likely request wording; where useful, add concise aliases for alternate wording of the
same owned request.

## Conditions And Aliases

Use `use_when` for plain-language conditions that make the profile applicable. Use
`not_for` for conditional near-misses, not as a second tag list. Use a small number of
`selection.aliases` only for alternate wording of the same owned request; aliases are
recognition-only and never create identity, routing, ranking, delegation, or a second
concept.

Use `supports` directionally for skills this skill directly supports. Do not use it to
express similarity, ownership, or a general relatedness list.

## Stop Rules

Stop when the profile distinguishes its nearest neighbors. Reject tags that merely
repeat the skill name, describe a shared implementation detail, fill an unused group,
name a one-off ticket, or duplicate a built-in value under another name. Do not use
popularity, frequency, ranking, scores, paths, or compatibility/routing metadata to
select a skill.

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
