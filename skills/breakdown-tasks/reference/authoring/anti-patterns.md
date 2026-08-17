# Atomicity Anti-Patterns

Reject these boundary shortcuts during decomposition.

## Hidden Independent Work

- A broad purpose contains several questions or changes.
- A lifecycle label hides analysis, implementation, and review concerns.
- A final document is used to merge independently reviewable findings.
- Implementation and a separately requested test artifact share one task.

## Unsupported Coupling

- The rationale names only a shared topic, file, destination, release, or skill.
- A dependency is treated as proof that work is inseparable.
- Several outputs are called a package without one shared result.
- Verification checks unrelated results under one task.

## Artificial Granularity

- A fixed task count is chosen before concerns are inventoried.
- One file, step, or skill is required per task.
- Tasks are merged to fit an available skill.
- Tasks are split only because a sentence contains “and” or a comma.

## Invalid Assignment

- Skills are assigned before operation and documentation profiles are collected.
- A fallback skill is forced when no contract matches.
- A selected skill changes an already established boundary.

Use [Atomicity Examples](atomicity-examples.md) for short contrastive cases. Use
[Core Rules](core-rules.md) for the authoritative boundary test.
