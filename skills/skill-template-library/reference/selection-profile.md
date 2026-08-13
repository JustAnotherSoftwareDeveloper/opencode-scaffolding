# Selection Profile Reference

Every active skill declares one direct-selection profile in its frontmatter.
The profile helps an author select the right class and relationship without
ranking, scoring, or path-based matching.

## Required Shape

```yaml
name: example-skill
selection:
  role: owner
  tags:
    actions: [inspect, produce]
    inputs: [request]
    outputs: [artifact]
    topics: [example domain]
    environments: [OpenCode]
    constraints: [bounded writes]
   aliases: [example operation] # optional recognition-only wording
  use_when: [the request asks for the example artifact]
  not_for: [unrelated documentation lookup]
  supports: [skill-template-library]
class: operation
```

The four top-level fields are `name`, `description`, `selection`, and `class`.
Optional repository metadata may be added only when it is meaningful and
allowed by the shared validator.

`aliases` is optional metadata for recognizing requests owned by this skill. It does
not create a skill or canonical name, alter ownership, or change the selected skill's
class, output, or execution authority. The `name` remains the sole canonical identity
and must match the skill directory. Aliases are not inventory entries, routing rules,
scores, ranks, thresholds, delegation instructions, or compatibility metadata.

## Profile Questions

- **Actions:** What verbs does the skill own?
- **Inputs:** What information or artifacts does it consume?
- **Outputs:** What artifact or decision does it produce?
- **Topics:** What subject matter does it cover?
- **Environments:** Where does it apply?
- **Constraints:** What boundary or safety condition matters?
- **Aliases:** Which alternate natural-language wording should an author recognize as
  a request for this skill? Keep recognition tied to the same canonical owner.
- **Use when:** What positive request conditions justify selection?
- **Not for:** Which nearby requests must not select it?
- **Supports:** Which other skill does this reference or assist? Support is
  directional and cannot target the declaring skill.

## Class and Role

- `operation`, `delegated`, and `inline` skills normally use
  `owner` because they perform or coordinate an owned operation.
- `planning` and `documentation` skills normally use `reference` because they
  provide passive context without executing a workflow.
- `support` is reserved for a skill whose primary purpose assists another
  skill without owning the user's operation.
- A profile must describe the skill's behavior, not its directory path,
  implementation language, or an unused tag category.

## Authoring Rules

- Keep values short, concrete, lowercase where ordinary language permits, and
  unique within each group.
- Preserve authored order; put the most discriminating values first.
- Omit an optional group rather than supplying an empty array.
- Use `not_for` for conditional boundaries and do not encode exclusions as
  negative aliases.
- Use aliases only as recognition aids. They must not override `description`, role,
  tags, conditions, or `name`, and must not authorize delegation or recursive loading.
- Validate local shape with the shared metadata validator and validate support
  targets against the complete active inventory.
