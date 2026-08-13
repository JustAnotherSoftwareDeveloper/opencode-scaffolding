# Schema Index

Skill metadata has one shared top-level shape:

```yaml
name: skill-name
selection:
  role: owner | reference | support
  tags:
    actions: [verb]
    inputs: [noun]
    outputs: [artifact]
    topics: [domain]
    environments: [context]
    constraints: [boundary]
  aliases: [alternate phrase]
  use_when: [positive condition]
  not_for: [explicit boundary]
  supports: [skill-name]
class: inline | planning | operation | documentation | delegated
```

`name`, `description`, `selection`, and `class` are required. Optional profile
groups may be omitted when they have no useful values; empty groups are not a
substitute for authoring a value. Lists preserve authored order and contain
canonical, unique strings. `aliases` is optional recognition-only metadata: it may
provide alternate wording for requests owned by the same skill, but it does not
create a canonical identity, inventory entry, ownership boundary, routing rule,
score, rank, threshold, delegation path, or compatibility route. The `name` remains
the sole canonical identity and must match the skill directory. `supports` is
directional and must not point to the skill itself.

This index documents the shared metadata contract; the presence of an alias example
here does not by itself establish validator support.

Class behavior and role invariants are documented in
`../reference/selection-profile.md` and `skills/skill-architect/class-taxonomy.md`.
Per-skill output schemas remain owned by the skill that produces that artifact;
this directory indexes metadata profiles rather than copying those schemas.
each skill's contract.
