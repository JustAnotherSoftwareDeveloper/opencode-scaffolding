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

## Script Delegation and Platform Selection Rule

Scripts are the sole exception to directory confinement. They may reference files in other directories since they are executed rather than read as skill content. A skill may invoke a script when the work is deterministic, repeatable, token-intensive, or has well-defined I/O. Python is the default platform for all scripts. Select Node (TypeScript/Bun) only when the core logic requires a Node-specific library (remark, mdast, babel, typescript) and no mature Python equivalent exists. Follow the decision framework in the Node Script Support proposal.

A skill may invoke a Python script when the work:

1. Is **deterministic** — produces identical output for identical input.
   Example: parsing YAML, validating JSON schema, computing diffs.
2. Is **repeatable** — the same operation runs many times with different inputs.
   Example: collecting metadata across many skill directories, transforming batch data.
3. Is **token-intensive** — the LLM reasoning cost exceeds the script's execution cost.
   Example: iterating over hundreds of files, performing regex transformations at scale.
4. Has **well-defined I/O** — inputs and outputs map cleanly to CLI arguments, stdin, stdout, or files.
   Example: a click CLI that reads a file path and writes a processed file.
5. Benefits from **library dependencies** — PyYAML, jsonschema, lxml, or other Python packages provide reliable functionality.
   Example: validating a YAML file against a JSON Schema.

**Anti-triggers** — do NOT delegate to a script when:

1. The work requires **judgment or creativity** — LLM reasoning is the correct tool.
   Example: determining whether a design document is complete.
2. The work involves **ambiguous or variable inputs** — the I/O shape changes per invocation.
   Example: interpreting a user's freeform request.
3. The work is a **one-off with no reuse** — the overhead of creating a script exceeds the tokens it saves.
   Example: a single ad-hoc grep across one file.
4. The work requires **adaptive decision-making** — the LLM must decide the next step based on partial results.
   Example: debugging an unknown error where the next diagnostic step depends on prior output.