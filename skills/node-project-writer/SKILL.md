---
name: node-project-writer
description: "Use when changing production behavior in a TypeScript Node.js or Bun project."
selection:
  role: owner
  tags:
    actions: [change production behavior]
    inputs: [TypeScript Node.js or Bun project, behavior change request]
    outputs: [implemented behavior, validated change report]
    topics: [production TypeScript source, directly coupled regression tests]
    environments: [Node.js application, Bun application, service, CLI product, package, library]
    constraints: [bounded authorized changes, preserve project-specific compatibility]
  use_when:
    - a request asks to implement or modify production behavior in a TypeScript Node.js or Bun project
  not_for:
    - a request asks only to add, change, or repair tests
    - a request asks for standalone quality configuration or check/report work
    - a request asks to choose or change dependencies, package managers, runtimes, or environment locks
    - a request asks to build or validate package artifacts, publish, or deploy
    - a request for JavaScript-only source work, JavaScript diagnostics, or JSDoc typing of .js files
    - a request that treats JavaScript or mixed-language project eligibility as in scope
class: operation
---

# Production Behavior Change Workflow

Change production behavior in an existing TypeScript Node.js or Bun application,
service, CLI product, package, or library. Include only regression tests directly needed
to establish the changed behavior.

TypeScript is the only source scope. An authorized change touches the TypeScript surface
plus only the manifests and configuration its authorization names; JavaScript source
edits are reported as out of scope, and a JavaScript-only request is reported as out of
scope. Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear
only where they explain how TypeScript source executes, emits, resolves, declares, or
reaches a consumer. TypeScript API documentation comments on exported declarations
remain in scope. Standalone JavaScript source guidance, JavaScript or mixed-language
eligibility, JavaScript checking (`allowJs`, `checkJs`), and JSDoc typing of `.js` files
are excluded.

## Normalize Input

Identify the target project and package, requested observable behavior, target runtime(s),
compatibility constraints, and the authorized TypeScript surface, manifests, and
configuration. Repository access alone does not authorize edits, migrations, installs, or
commands with material side effects. Ask before acting when missing information could
materially change the behavior, compatibility surface, target, or allowed effects.

## Procedure

1. **Inspect the affected behavior.** Trace its implementation, callers, public imports,
   package boundaries, project instructions, runtime and module configuration, and
   relevant tests. Establish only the context that can affect the requested outcome.
   Reconcile the affected package, exact script/invocation, compiler config and runtime
   separately; a lockfile, filename, or passing test is not a substitute for that evidence.
   Distinguish Node.js from Bun execution; Bun used as a package manager or command runner
   does not itself establish Bun runtime targeting. Keep this general-project workflow
   separate from this repository's `scripts/node/` utilities and their local defaults.
2. **Bound the change.** Preserve established project configuration and compatibility
   promises, then applicable local policy. Identify the smallest authorized production
   edits and directly coupled regression tests. Do not silently migrate module formats,
   runtimes, frameworks, adapters, managers, build systems, dependency graphs, or public
   interfaces. Keep test-only work with
   `node-project-test-writer -> #test-only-change-workflow`, dependency and environment
   changes with
   `node-project-dependencies -> #dependency-decision-and-environment-workflow`,
   standalone quality with `node-quality-workflow -> #standalone-quality-workflow`, and
   package artifacts with
   `node-package-distribution -> #package-artifact-and-consumer-workflow`. Publication,
   deployment, and registry administration stay outside this operation, and executable
   source-based plans remain with `plan-writer`.
3. **Resolve version-sensitive details.** Use the target project's declared and effective
   versions, commands, package/workspace scope, and verified local documentation. Runtime,
   package manager, checker, transpiler, build tool, framework, adapter, test runner, and
   artifact consumer are separate dimensions, and the runtime is not inferred from
   TypeScript syntax, a manager, a framework name, or a path. Treat examples as
   representative, not as a tested compatibility matrix or universal stack. A successful
   transform or type check does not establish runtime behavior. If a required fact cannot
   be established within scope, state the gap and defer the affected action rather than
   guessing. Use the
   [conflicting-clue production decision](reference/change-design-and-validation.md#reconcile-conflicting-project-clues)
   when signals disagree.
4. **Implement the bounded behavior.** Follow the project's source and error-handling
   conventions where they are established. Preserve unrelated interfaces and behavior.
   Keep sensitive values out of source, logs, tests, and reports. Add or adjust only
   regression coverage directly coupled to the changed behavior. If a necessary effect
   exceeds authorization, stop before that effect and identify what approval or owner is
   needed.
5. **Validate the actual outcome.** Run applicable project-configured tests and checks
   only when authorized. Match each check to its scope: a type checker checks its selected
   program; a transform/build produces its configured output; a test runner exercises
   its configured runtime and selection; lint and formatting tools cover their configured
   files. Validate an emitted or selected artifact in its actual consumer/runtime only
   when the request requires it and that work is authorized. Record exact commands,
   versions when known, targets, and results. Separate new findings from pre-existing
   ones; do not repair unrelated findings. Report skipped, unavailable, deferred, or
   inconclusive checks explicitly.

## Self-Validation

- The diff contains only the authorized production changes, authorization-named manifests
  or configuration, and directly coupled regression tests.
- The report distinguishes observed checks from untested runtime, compatibility,
  security, and deployment claims; no claim exceeds the checks actually run.
- No workflow selects or relies on Vite; incidental transitive package presence is not
  treated as direct selection or proof of graph absence.

## Expected Output

Return the behavior change and a concise report of observable behavior, changed paths,
runtime and compatibility assumptions, exact validation evidence, and remaining gaps. If
blocked or unchanged, state why and the bounded next step.

## Docs

- [Reference index](reference/README.md) — scope and navigation for the local project
  context.
- [Change design and validation](reference/change-design-and-validation.md) — effective
  project context, module-to-runtime alignment, regression scope, and evidence limits.
- [Behavior and caller contracts](reference/behavior-and-caller-contracts.md) —
  caller-observable results, failure channels, timing, cancellation, side effects, and
  behavioral and public boundaries.
