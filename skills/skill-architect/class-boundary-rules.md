# Class Boundary Rules

Each class has a distinct contract for side effects, delegation, and output shape.
A skill whose behavior spans multiple classes must be split or rewritten.
Hybrid classes are not supported.

## Side Effects

- `operation`, `delegated`, `inline`, and `orchestrated` produce side effects (file writes, tool calls).
- `planning` and `documentation` must not produce side effects, modify files, or invoke tools.

## Delegation

- `orchestrated` and `delegated` participate in delegation pipelines.
- `operation`, `inline`, `planning`, and `documentation` do not sub-delegate.

## Execution Steps

- All classes except `planning` and `documentation` define execution steps with numbered prefixes.
- `planning` and `documentation` use passive content sections instead.

## Boundary Disambiguation

- **A planning skill must not be loaded** when the goal is to modify files or run a procedure.
  Loading a planning skill during execution tasks will provide structural context but will not produce workflow steps.
- **An operation skill must not be loaded** during reasoning-only tasks.
  Loading an operation skill for reasoning will introduce unnecessary execution structure.
- **A delegated skill must accept a well-formed delegation packet** and return structured output.
  Delegated skills are not autonomous — they depend on a delegator for context and invocation.
- **An inline skill is ephemeral** — load it for one reasoning pass, then discard.
  Inline skills are not designed for repeated invocation across multiple task phases.
- **An orchestrated skill owns sub-delegation and result collation.**
  Orchestrated skills define the worker strategy, dispatch workers, and collate results into a single output.
- **A documentation skill is a passive data store** consumed by other skills via relative-path references.
  It must not define execution steps or produce side effects.

## When the Boundary is Unclear

Trace the proposed skill's contract by asking three questions:

1. **Does it produce side effects?**
   - Yes → `operation`, `delegated`, `inline`, or `orchestrated`.
   - No → `planning` or `documentation`.

2. **Does it delegate work to other skills or workers?**
   - Yes → `orchestrated` or `delegated`.
   - No → `operation`, `inline`, `planning`, or `documentation`.

3. **Does it run in a single pass or coordinate multiple phases?**
   - Single pass → `operation`, `inline`, or `delegated`.
   - Multiple phases → `orchestrated`.

The answers to these three questions map to exactly one class.

## Cross-Skill Interaction Rule

Cross-skill interaction is represented exclusively through skill loading.
No skill file may contain a literal path to a file in another skill's directory.
Scripts are the sole exception to this rule — they may reference files in other directories since they are executed rather than read as skill content.